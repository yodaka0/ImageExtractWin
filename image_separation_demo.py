# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" Demo for image separation between positive and negative detections"""

#import tkinter as tk
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()
json_file = filedialog.askopenfilename()
if not json_file:
    root.destroy() 


# PyTorch imports 

from PytorchWildlife import utils as pw_utils

output_path = json_file.replace(".json","")
threshold = input("input threshold: ")

# Separate the positive and negative detections through file copying:
pw_utils.detection_folder_separation(json_file, output_path, float(threshold))