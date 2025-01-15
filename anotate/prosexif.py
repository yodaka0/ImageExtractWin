import numpy as np
import os
import pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import filedialog

def find_image_files(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

#    image_files = natsorted(image_files)

    return image_files

#get path of directory by browsing directories
root = tk.Tk()
path = filedialog.askdirectory()
root.destroy()
print(path)
results = []

#list of files in directory by 
files = find_image_files(path)
print(files)

#get list of files in directory
for im_file in files:
    print(im_file)
    img_fullpath = os.path.join(path, im_file)
    img = Image.open(img_fullpath)
    exif_data = img._getexif()
    date, time = exif_data[36867].split(' ')
    result = {}
    result["img_id"] = img_fullpath
    result["object"] = "None"
    result["Date"] = date
    result["Time"] = time
    #get deployment ID from second section of path 
    result["deploymentID"] = os.path.split(im_file)[-2]
    result['eventStart']  = exif_data[36867]
    result['eventEnd'] = exif_data[36867]
    result["Make"] = exif_data[271]
    result["scientificName"] = "False"
    result["file"] = os.path.basename(im_file)
    results.append(result)
results_dataframe = pd.DataFrame(results)
#write to csv file

csvfilename = path + "output.csv"
results_dataframe.to_csv(csvfilename, index=True)
