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


def pw_detect(im_file, new_file, threshold=None):

    verbose = False

    if not isinstance(threshold, float):
        threshold = 0.2
    
    #%% 
    # Setting the device to use for computations ('cuda' indicates GPU)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    if verbose:
        print(DEVICE)
        print(f"Threshold: {threshold}")
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
    
    #result['img_id'] = result['img_id'].replace("\\","/")

    # Saving the detection results 
    animal_n = sum('animal' in item for item in result['labels'])
    print(animal_n)
    result['object'] = animal_n
    try:
        img = Image.open(im_file)
        exif_data = img._getexif()
        result['eventStart']  = exif_data[36867]
        result['eventEnd'] = exif_data[36867]
        result["Make"] = exif_data[271]
    except:
        result['eventStart'] = "None"
        result['eventEnd'] = "None"
        result["Make"] = None

    if animal_n > 0:
        pw_utils.save_detection_images(result, new_file_path)
    
    return result
