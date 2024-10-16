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

# 動物のクラスラベル
txt_animalclass = [
    "badger", "ibex", "beaver", "red deer", "chamois", "cat", "goat", "roe deer", "dog", "fallow deer", "squirrel", "equid", "genet",
    "hedgehog", "lagomorph", "wolf", "otter", "lynx", "marmot", "micromammal", "mouflon",
    "sheep", "mustelid", "bird", "bear", "nutria", "raccoon", "fox", "wild boar", "cow"
]
BACKBONE = "vit_large_patch14_dinov2.lvd142m"
weight_path = 'deepfaune-vit_large_patch14_dinov2.lvd142m.v2.pt'
CROP_SIZE = 518


class Classifier:
    def __init__(self, model_dir=os.getcwd()):
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
            return predictions, confidences
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

        if path[-3:] != ".pt":
            path += ".pt"
        try:
            params = torch.load(path, map_location=device)
            if 'args' in params:
                args = params['args']
                if 'num_classes' in args and self.base_model.num_classes != args['num_classes']:
                    raise Exception("You load a model ({}) that does not have the same number of class ({})".format(args['num_classes'], self.base_model.num_classes))
            self.load_state_dict(params['state_dict'])
        except Exception as e:
            print("Can't load checkpoint model because :\n\n " + str(e), file=sys.stderr)
            raise e


if __name__ == "__main__":
    classifier = Classifier()
    image_path = "C:/Users/tomoyakanno/Documents/nullremove/ogawa.2020.12/21/10100043.JPG"
    img = Image.open(image_path)
    result = {
        "bbox": [
            [668, 1001, 1386, 1692],
            [0, 931, 591, 1831]
        ]
    }
    classifier.run_prediction(result, img)