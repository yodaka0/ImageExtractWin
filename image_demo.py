# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" Demo for image detection"""

#%% 
# Importing necessary basic libraries and modules
import numpy as np
import os
from PIL import Image

#%% 
# PyTorch imports 
import torch
#%% 
# Importing the model, dataset, transformations and utility functions from PytorchWildlife
from PytorchWildlife.models import detection as pw_detection
from PytorchWildlife.data import transforms as pw_trans
#from PytorchWildlife.data import datasets as pw_data 
from PytorchWildlife import utils as pw_utils

def contains_animal(labels):
    for label in labels:
        if 'animal' in label:
            return True
    return False

def pw_detect(im_file, new_file, threshold=None):
    if threshold is not float:
        threshold = 0.2
    #print(f"Threshold: {threshold}")

    #file_path = im_file.replace("\\","/")
    #print(f"File path: {im_file}")
    #im_file_path = im_file.replace("\\","/")
    #new_file_path = new_file_path.replace("\\","/")
    #print(f"New file path: {new_file}")
    #%% 
    # Setting the device to use for computations ('cuda' indicates GPU)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    #%% 
    # Initializing the MegaDetectorV5 model for image detection
    detection_model = pw_detection.MegaDetectorV5(device=DEVICE, pretrained=True)

    #%% Single image detection
    # Specifying the path to the target image TODO: Allow argparsing

    # Opening and converting the image to RGB format
    img = np.array(Image.open(im_file).convert("RGB"))

    # Initializing the Yolo-specific transform for the image
    transform = pw_trans.MegaDetector_v5_Transform(target_size=detection_model.IMAGE_SIZE,
                                                stride=detection_model.STRIDE)

    #filename = os.path.basename(new_file)
    new_file_base = "\\" + os.path.basename(new_file) 
    new_file_path = new_file.replace(new_file_base,"")
    

    # Performing the detection on the single image
    result = detection_model.single_image_detection(transform(img), img.shape, im_file, conf_thres=threshold)
    
    result['img_id'] = result['img_id'].replace("\\","/")

    # Saving the detection results 
    #print(results['labels'])
    if contains_animal(result['labels']):
        pw_utils.save_detection_images(result, new_file_path)
        result['object'] = len(result['labels'])
        img = Image.open(im_file)
        exif_data = img._getexif()
        date, time = exif_data[36867].split(' ')
        result["Date"] = date
        result["Time"] = time
        result["Make"] = exif_data[271]
    else:
        result['object'] = 0
        result["Date"] = 0
        result["Time"] = 0
        result["Make"] = None

    #%% Output to cropped images
    # Saving the detected objects as cropped images
    #pw_utils.save_crop_images(results, "crop_output")

    #%% Output to JSON results
    # Saving the detection results in JSON format
    """output_folder = session_root + "_out"
    pw_utils.save_detection_json(results, output_folder,
                                categories=detection_model.CLASS_NAMES)"""
    
    return result
