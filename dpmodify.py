import pandas as pd
import tkinter as tk
from tkinter import filedialog
tk.Tk().withdraw()
import os
import warnings
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

data_path = filedialog.askopenfilename()
data = pd.read_csv(data_path, dtype=str, low_memory=False)

#change label names
data = data.rename(columns={'img_id': 'mediaID', 'object': 'count','Unnamed: 0':'observationID'})

if 'eventStart' not in data.columns or 'eventEnd' not in data.columns:
    data = data.rename(columns={'file':'mediaID'})
    data['Date'] = data['Date'].astype(str)
    data['Time'] = data['Time'].astype(str)
    datetime = data['Date'] + ' ' + data['Time']
    print(datetime[0:10])
    # convert to datetime
    data['eventStart'] = datetime
    data['eventEnd'] = datetime
    # drop 'Date' and 'Time' columns
    data = data.drop(columns=['Date', 'Time'])

# join date and time columns in the format yyyy/mm/dd hh:mm:ss
# Ensure 'Date' and 'Time' columns are strings
data["observationType"] = None
data["observationLevel"] ="media"
for i in range(len(data)):
    try:
        observationType = data['scientificName'][i]
        if observationType == 'blank':
            data['observationType'][i] = 'blank'
        elif observationType == 'human':
            data['observationType'][i] = 'human'
        elif observationType == 'vehicle':
            data['observationType'][i] = 'vehicle'
        elif observationType == 'unknown':
            data['observationType'][i] = 'unknown'
        elif pd.isna(observationType) or observationType == 'False':
            data['observationType'][i] = "unclassified"
        else:
            data['observationType'][i] = 'animal'
        #separate path
        deploymentID = (data['mediaID'][i].split(os.path.sep)[1:5])
        #paste path back
        data["deploymentID"][i] = os.path.sep.join(deploymentID).replace(os.path.sep, '_')
        #Formatted as an ISO 8601 string with timezone designator (YYYY-MM-DDThh:mm:ssZ or YYYY-MM-DDThh:mm:ss±hh:mm).
        data["eventStart"][i] = data['eventStart'][i].replace(' ', 'T') + 'Z'
        data["eventEnd"][i] = data['eventEnd'][i].replace(' ', 'T') + 'Z'
        #convert 2024-05-08 10:00:58.163140 to 2024-05-08T10:00:58Z
        data['classificationTimestamp'][i] = data['classificationTimestamp'][i].replace(' ', 'T')[:19] + 'Z'
        #mediaID convert hash 16 digit
        from hashlib import md5 as hash
        data["mediaID"][i] = hash(data['mediaID'][i].encode()).hexdigest()[:16]
        

        if 'bbox' in data.columns and data["bbox"][i] is not None:
            data["bboxX"] = data["bbox"][i][0]
            data["bboxY"] = data["bbox"][i][1]
            data["bboxWidth"] = data["bbox"][i][2] - data["bbox"][i][0]
            data["bboxHeight"] = data["bbox"][i][3] - data["bbox"][i][1]
        else:
            data["bboxX"] = None
            data["bboxY"] = None
            data["bboxWidth"] = None
            data["bboxHeight"] = None
    except Exception as e:
        print(f"Error in row {i}: {e}")
        continue
#save to new file
data.to_csv(os.path.basename(data_path).replace('.csv','_modi.csv'), index=False)
