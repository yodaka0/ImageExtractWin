import sys
import torch
from torch import tensor
import torch.nn as nn
from torchvision.transforms import InterpolationMode, transforms
import torch.nn.functional as F
import timm
import numpy as np
from PIL import Image
import os
import json



def download_model(path):

    # 動物のクラスラベル

    model = "Kirghizistan - Manas v1 - OSI-Panthera - Hex Data"
    print(f"classify model: {model}")
    #import json file
    model_info = json.load(open("model_info_v1.json"))
    txt_animalclass = model_info["cls"][model]["all_classes"]

    """[
        "badger", "ibex", "beaver", "red deer", "chamois", "cat", "goat", "roe deer", "dog", "fallow deer", "squirrel", "equid", "genet",
        "hedgehog", "lagomorph", "wolf", "otter", "lynx", "marmot", "micromammal", "mouflon",
        "sheep", "mustelid", "bird", "bear", "nutria", "raccoon", "fox", "wild boar", "cow"
    ]"""
    BACKBONE = "vit_large_patch14_dinov2.lvd142m"
    weight_url = model_info["cls"][model]["download_info"][0][0]
    #'deepfaune-vit_large_patch14_dinov2.lvd142m.v2.pt'
    CROP_SIZE = 518

    # home directory
    path = os.path.expanduser("~")
    downloading_dir = os.path.join(path, ".cache", "torch", "hub", "checkpoints")
    download_path = os.path.join(downloading_dir, weight_url.split("/")[-1]).replace("?download=true", "")
    if not os.path.exists(download_path):
        print(f"Dowloading model to {download_path}")
        import requests
        r = requests.get(weight_url, stream=True)
        
        with open(download_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Model downloaded to {download_path}")
    return txt_animalclass, BACKBONE, CROP_SIZE, download_path

class Classifier:
    def __init__(self, model_dir=os.getcwd()):
        global txt_animalclass
        global BACKBONE
        global CROP_SIZE
        global weight_path
        txt_animalclass, BACKBONE, CROP_SIZE, weight_path = download_model(model_dir)
        self.model = Model()
        self.model.load_weights(os.path.join(model_dir, weight_path))
        self.transforms = transforms.Compose([
            transforms.Resize(size=(CROP_SIZE, CROP_SIZE), interpolation=InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.4850, 0.4560, 0.4060], std=[0.2290, 0.2240, 0.2250])
        ])

    # croppedimage loaded by PIL
    def preprocess_image(self, croppedimage):
        preprocessimage = self.transforms(croppedimage)
        return preprocessimage.unsqueeze(dim=0)

    def load_cropped_images(self, result, img):
        cropped_images = []
        for bbox in result['detections'].xyxy:
            try:
                cropped_image = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                cropped_images.append(cropped_image)
            except Exception as e:
                print(f"Error in cropping image: {e}")
        return cropped_images

    def run_prediction(self, result, img):
        try:
            cropped_images = self.load_cropped_images(result, img)
            predictions = []
            confidences = []
            for cropped_image in cropped_images:
                image_tensor = self.preprocess_image(cropped_image)
                prediction = self.model.predict(image_tensor)
                predicted_class_idx = np.argmax(prediction, axis=1)[0]
                predictions.append(txt_animalclass[predicted_class_idx])
                confidences.append(prediction[0][predicted_class_idx])
                print(f"Predicted class: {txt_animalclass[predicted_class_idx]}, Confidence: {prediction[0][predicted_class_idx]}")
            return predictions, confidences, self.model
        
        except Exception as e:
            print(f"Error in running prediction: {e}")
            return None, None


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        
        self.base_model = timm.create_model(BACKBONE, pretrained=False, num_classes=len(txt_animalclass))

    def forward(self, input):
        x = self.base_model(input)
        return x

    def predict(self, data, withsoftmax=True):
        self.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(device)
        with torch.no_grad():
            x = data.to(device)
            if withsoftmax:
                output = self.forward(x).softmax(dim=1)
            else:
                output = self.forward(x)
        return output.cpu().numpy()

    def load_weights(self, path):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if not path.endswith(".pt"):
            path += ".pt"
        try:
            # まず torch.load で読み込んでみる
            params = torch.load(path, map_location=device)
            if isinstance(params, dict) and 'state_dict' in params:
                # 通常の checkpoint の場合
                if 'args' in params:
                    args = params['args']
                    if 'num_classes' in args and self.base_model.num_classes != args['num_classes']:
                        raise Exception("Loaded model classes ({}) do not match expected ({})".format(args['num_classes'], self.base_model.num_classes))
                self.load_state_dict(params['state_dict'])
            else:
                # TorchScript 形式の場合
                script_module = torch.jit.load(path, map_location=device)
                self.base_model = script_module
        except Exception as e:
            print("Can't load checkpoint model because :\n\n " + str(e), file=sys.stderr)
            raise e
