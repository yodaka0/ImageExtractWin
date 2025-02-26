
#%% 
# Importing necessary basic libraries and modules
import numpy as np
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#%% 
# PyTorch imports 
import torch
#%% 
# Importing the model, dataset, transformations and utility functions from PytorchWildlife
from PytorchWildlife.models import detection as pw_detection
#from PytorchWildlife.data import transforms as pw_trans
from PytorchWildlife import utils as pw_utils

try:
    from classifier import Classifier
    from dp_ethi import estimate_depth
except:
    print("Classifier and depth estimation not available")


def pw_detect(im_file, new_file, threshold=None, pre_detects=None, diff_reasoning=False, verbose=False, model=None):

    if not isinstance(threshold, float):
        threshold = 0.2

    classify = False
    depth = False
    exif_inherit = False
    
    #%% 
    # Setting the device to use for computations ('cuda' indicates GPU)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    if verbose:
        print(DEVICE)
        print(f"Threshold: {threshold}")
    #%% 
    # Initializing the MegaDetectorV5 model for image detection
    if model == "MegaDetector_v5":
        detection_model = pw_detection.MegaDetectorV5(device=DEVICE, pretrained=True, version="a")
    elif model == "HerdNet":
        if DEVICE == "cpu":
            print("HerdNet model is too heavy for CPU, please use GPU")
            raise ValueError("Model not supported")
        elif DEVICE == "cuda":
            detection_model = pw_detection.HerdNet(device=DEVICE, dataset="ennedi")
    else:
        detection_model = pw_detection.MegaDetectorV6(device=DEVICE, pretrained=True, version=model)

    #%% Single image detection
    # Specifying the path to the target image TODO: Allow argparsing

    # Opening and converting the image to RGB format
    img = np.array(Image.open(im_file).convert("RGB"))

    # Initializing the Yolo-specific transform for the image
    #transform = pw_trans.MegaDetector_v5_Transform(target_size=detection_model.IMAGE_SIZE,
    #                                            stride=detection_model.STRIDE)

    new_file_path = os.path.dirname(new_file)

    # Performing the detection on the single image
    #result = detection_model.single_image_detection(transform(img), img.shape, im_file, conf_thres=threshold)
    # Performing the detection on the single image
    if model == "HerdNet":
        result = detection_model.single_image_detection(img=im_file)
        #print(result)
    else:
        try:
            result = detection_model.single_image_detection(img=img, img_path=im_file, det_conf_thres=threshold)
        except:
            result = detection_model.single_image_detection(img=img, img_path=im_file)
            print("threshold set defalut value")

    
        #result['img_id'] = result['img_id'].replace("\\","/")

        if diff_reasoning and pre_detects is not None:
            # extract values of bounding boxes from the result dictionary
            bounding_boxes = result['detections'].xyxy
            prev_bounding_boxes = pre_detects.xyxy
            # if bounding boxes heardly change, then animal change into blank
            if len(bounding_boxes) == len(prev_bounding_boxes):
                for i in range(len(bounding_boxes)):
                    if (abs(bounding_boxes[i][0] - prev_bounding_boxes[i][0]) < 5 and
                        abs(bounding_boxes[i][1] - prev_bounding_boxes[i][1]) < 5 and
                        abs(bounding_boxes[i][2] - prev_bounding_boxes[i][2]) < 5 and
                        abs(bounding_boxes[i][3] - prev_bounding_boxes[i][3]) < 5):
                        print(f"bounding boxes:{bounding_boxes[i]}")
                        print(f"previous bounding boxes:{prev_bounding_boxes[i]}")
                        print("bounding box not move, change to blank")
                        #transform animal in the labels to 'blank'
                        result['labels'][i] = "blank"

        # Saving the detection results 
        animal_n = sum('animal' in item for item in result['labels'])
        print(f'{im_file} has {animal_n} animals')
        result['object'] = animal_n

    try:
        img = Image.open(im_file)
        exif_data = img._getexif()
        result['eventStart']  = exif_data[36867]
        result['eventEnd'] = exif_data[36867]
        result["Make"] = exif_data[271]
        result["bbox"] = result['detections'].xyxy
    except:
        result['eventStart'] = "None"
        result['eventEnd'] = "None"
        result["Make"] = None

    if model == "HerdNet":
        pw_utils.save_detection_images_dots(result, new_file_path, overwrite=False)
    elif animal_n > 0:
        if verbose:
            print(f"Saving detection images to {new_file_path}")
            print(result)
        pw_utils.save_detection_images(result, new_file_path, overwrite=False)
        if exif_inherit:
            new_img = Image.open(new_file)
            if "exif" in img.info:
                new_img.save(new_file, exif=img.info["exif"])
        if classify:
            try:
                animalclass = Classifier(model_dir=os.getcwd())
                sp, conf = animalclass.run_prediction(result, img)
                result['scientific_name'] = sp
                result['sp_confidence'] = conf
            except Exception as e:
                print(f"Error in classification: {e}")
                raise
        if depth:
            try:
                bbox = result['detections'].xyxy
                depth_map, mean_depths = estimate_depth(img, bbox)
                #print("Depth estimation successful")
                #result['depth_map'] = depth_map
                result['mean_depths'] = [round(depth, 3) for depth in mean_depths]
                # Saving the depth map
                #print(f"new_file_path is {new_file_path}")
                depth_map_path = os.path.join(new_file_path, os.path.basename(im_file).replace(".JPG", "_depth.JPG"))
                #print(f"Saving depth map to {depth_map_path}")
                if not os.path.exists(depth_map_path):
                    # Convert depth_map to PIL Image
                    depth_map_image = Image.fromarray((depth_map * 255).astype(np.uint8))
                    # put bbox on the depth map and save it
                    draw = ImageDraw.Draw(depth_map_image)
                    for i, b in enumerate(bbox):
                        #image_width, image_height = depth_map_image.size
                        image_bbox = [
                            int(b[0]),  # x0
                            int(b[1]),  # y0
                            int(b[2]),  # x1
                            int(b[3])   # y1
                            ]
                        draw.rectangle(image_bbox, outline='orange', width=5)
                        #add mean depth to the bbox in the depth map
                        font = ImageFont.truetype("arial.ttf", 40)
                        draw.text((image_bbox[0], image_bbox[1] - 40), f"depth:{mean_depths[i]:.2f}", fill="orange", font=font)
                    depth_map_image.save(depth_map_path)
            except Exception as e:
                print(f"Error in depth estimation: {e}")
                raise

    return result
