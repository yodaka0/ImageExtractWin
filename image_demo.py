# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" Demo for image detection"""

#%% 
# Importing necessary basic libraries and modules
#import numpy as np
import os
from PIL import Image

#%% 
# PyTorch imports 
import torch
#%% 
# Importing the model, dataset, transformations and utility functions from PytorchWildlife
from PytorchWildlife.models import detection as pw_detection
from PytorchWildlife import utils as pw_utils

def contains_animal(labels):
    for label in labels:
        if 'animal' in label:
            return True
    return False

def pw_detect(im_file, new_file, threshold=None):
    #print("Threshold_pw: ",threshold)
    if not isinstance(threshold, float):
        threshold = 0.2
        
    #%% 
    # Setting the device to use for computations ('cuda' indicates GPU)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    #%% 
    # Initializing the MegaDetectorV5 model for image detection
    detection_model = pw_detection.MegaDetectorV6(device=DEVICE, weights='../MDV6b-yolov9c.pt', pretrained=False)


    #filename = os.path.basename(new_file)
    new_file_base = "\\" + os.path.basename(new_file) 
    new_file_path = new_file.replace(new_file_base,"")
    

    # Performing the detection on the single image
    result = detection_model.single_image_detection(img_path=im_file, conf_thres=threshold)
    
    #result['img_id'] = result['img_id'].replace("\\","/")

    # Saving the detection results 
    #print(results['labels'])
    if contains_animal(result['labels']):
        pw_utils.save_detection_images(result, new_file_path)
        result['object'] = len(result['labels'])
        try:
            img = Image.open(im_file)
            exif_data = img._getexif()
            date, time = exif_data[36867].split(' ')
            result["Date"] = date
            result["Time"] = time
            result["Make"] = exif_data[271]
        except:
            result["Date"] = "None"
            result["Time"] = "None"
            result["Make"] = "None"
        print(f"Result: {result}")
    else:
        result['object'] = 0
        result["Date"] = 0
        result["Time"] = 0
        result["Make"] = None

    
    return result
