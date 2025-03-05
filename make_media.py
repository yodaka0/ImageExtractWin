import os
import tkinter as tk
from tkinter import filedialog, messagebox
from natsort import natsorted
from hashlib import md5 as hash
from tkinter import font
from PIL import Image
import pandas as pd
import re

def remove_non_numeric_chars(input_string):
    return re.sub(r'\D', '', input_string)

def find_image_files(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    image_files = natsorted(image_files)

    return image_files

def get_media_info(image_files, method=None):
    media_info = []

    for image_file in image_files:
        img_extention = image_file.split('.')[-1] 
        img = Image.open(image_file)
        exif = img._getexif()
        if exif:
            timestamp = exif.get(36867).replace(' ', 'T') + 'Z'
            exifdata = {
                "ISO": exif.get(34855),
                "Make": exif.get(271),
                "Model": exif.get(272),
                "FocalLength": exif.get(37386),
                "ExposureTime": exif.get(33434),
                "Aperture": exif.get(33437),
                "GPSInfo": exif.get(34853),
            }
        else:
            timestamp = None
            exifdata = None
        media_id =hash(image_file.encode()).hexdigest()[:16]
        deploymentID = re.split(r'[\\/]', image_file)
        #print(deploymentID)
        deploymentID = "_".join(deploymentID[4:7])

         
        media_info.append({
            "mediaID": media_id,
            "deploymentID": deploymentID,
            "captureMethod": method,
            "timestamp": timestamp,
            "filePath": os.path.dirname(image_file),
            "filePublic": "False",
            "filaName": os.path.basename(image_file),
            "fileMediaType": "image/" + img_extention,
            "exifData": exifdata
        })

    return media_info


def browse_session_root():
    directory = filedialog.askdirectory()
    if directory:
        session_root_entry.delete(0, tk.END)
        session_root_entry.insert(0, directory)

def browse_media_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        media_file_entry.delete(0, tk.END)
        media_file_entry.insert(0, file_path)

def get_rid_duplicate(list):
    return list(dict.fromkeys(list))

# ...existing code...

def start_process():
    session_root = session_root_entry.get()
    media_file = media_file_entry.get()
    open_folder = False

    if media_file:
        media_df = pd.read_csv(media_file, dtype=str, low_memory=False)
        deployment_info_file = os.path.join(os.path.dirname(media_file), "deployment_info.csv")
    else:
        media_file = os.path.join(session_root, "media.csv")
        deployment_info_file = os.path.join(session_root, "deployment_info.csv")
        
        image_files = find_image_files(session_root)

        if not image_files:
            messagebox.showerror("Error", "No image files found in the session root.")
            return
        
        media_info = get_media_info(image_files)

        # Save the media info to a CSV file
        media_df = pd.DataFrame(media_info)
        media_df.to_csv(media_file, index=False)

    dp_file = filedialog.askopenfilename()
    deplo_df = pd.read_csv(dp_file, dtype=str, low_memory=False, encoding='ISO-8859-1')
    deplo_df.columns = [col.strip() for col in deplo_df.columns]
    print(deplo_df)

    # deploymentID ごとに最古と最新の timestamp を取得
    media_df['timestamp_dt'] = pd.to_datetime(media_df['timestamp'], format='%Y:%m:%dT%H:%M:%SZ', errors='coerce')
    timestamp_range = media_df.groupby('deploymentID')['timestamp_dt'].agg(deploymentStart='min', deploymentEnd='max').reset_index()
    print(timestamp_range)

    deployment_info = []
    for i, row in timestamp_range.iterrows():
        deploymentID = row['deploymentID']

        deploymentNo = deploymentID.split('_')[-1]
        deployarea = deploymentID.split('_')[-3]
        for j, dp in deplo_df.iterrows():
            #print(dp)
            dp_no = remove_non_numeric_chars(dp["GPSNo"])
            print(dp_no)
            print(deployarea)
            if deploymentNo == dp_no and deployarea == dp["Area"]:
                deployment_info.append({
                    "deploymentID": deploymentID,
                    "deploymentStart": row['deploymentStart'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "deploymentEnd": row['deploymentEnd'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "latitude": dp["Lat"],
                    "longitude": dp["Lon"]
                })
                break

    # deployment_info を DataFrame に変換して CSV に保存
    deployment_info_df = pd.DataFrame(deployment_info)
    
    deployment_info_df.to_csv(deployment_info_file, index=False)

    messagebox.showinfo("Info", f"Process completed successfully. Check the {media_file} and {deployment_info_file} for results.")
    root.destroy()
    if open_folder:
        os.startfile(media_file)

if __name__ == "__main__":

    root = tk.Tk()
    root.title("Make Media file")
    font_size = 15

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=font_size)

    tk.Label(root, text="Session Root:").grid(row=0, column=0, padx=10, pady=5)
    session_root_entry = tk.Entry(root, width=50)
    session_root_entry.grid(row=0, column=1, padx=10, pady=5)
    browse_button = tk.Button(root, text="Browse", command=browse_session_root)
    browse_button.grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="Media file:").grid(row=1, column=0, padx=10, pady=5)
    media_file_entry = tk.Entry(root, width=50) 
    media_file_entry.grid(row=1, column=1, padx=10, pady=5)
    browse_button = tk.Button(root, text="Browse", command=browse_media_file)  
    browse_button.grid(row=1, column=2, padx=10, pady=5)

    start_button = tk.Button(root, text="Start", command=start_process)
    start_button.grid(row=6, column=0, columnspan=3, pady=20)


    root.mainloop()

    



