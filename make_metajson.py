import json
"""
This script creates a datapackage.json file for a Camtrap Data Package specification.
It provides a GUI for users to input dataset details and select necessary CSV files.
Functions:
    load_config(config_path): Loads an optional configuration file (datapackage_config.json) if it exists.
    browse_media_root(): Opens a file dialog to select the media file and updates the corresponding entry field.
    browse_deployment_root(): Opens a file dialog to select the deployment info file and updates the corresponding entry field.
    browse_observation_root(): Opens a file dialog to select the observation file and updates the corresponding entry field.
    main(): Main function that gathers user inputs, constructs the datapackage.json content, and saves it.
GUI Elements:
    - Dataset name entry
    - Title entry
    - Dataset ID entry
    - Description entry
    - Media file selection
    - Deployment info file selection
    - Observation file selection
    - Button to create datapackage.json
The script uses the tkinter library to create the GUI and pandas to handle CSV files.
"""
import os
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import pandas as pd

def load_config(config_path):
    """オプションの設定ファイル(datapackage_config.json)があれば読み込む"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def browse_media_root():
    file_path = filedialog.askopenfilename()
    if file_path:
        media_root_entry.delete(0, tk.END)
        media_root_entry.insert(0, file_path)

def browse_deployment_root():
    file_path = filedialog.askopenfilename()
    if file_path:
        deployment_root_entry.delete(0, tk.END)
        deployment_root_entry.insert(0, file_path)

def browse_observation_root():
    file_path = filedialog.askopenfilename()
    if file_path:
        observation_root_entry.delete(0, tk.END)
        observation_root_entry.insert(0, file_path)


def main():
    # 設定ファイルがあれば読み込む（ない場合は空のdict）
    config = load_config("datapackage_config.json")


    media_file = media_root_entry.get()
    #media_df = pd.read_csv(media_file, dtype=str, low_memory=False)

    deployment_info_file = deployment_root_entry.get()
    #deplo_df = pd.read_csv(deployment_info_file, dtype=str, low_memory=False, encoding='ISO-8859-1')

    observation_file = observation_root_entry.get()
    #obs_df = pd.read_csv(observation_file, dtype=str, low_memory=False, encoding='ISO-8859-1')

    
    # 必要な項目を設定ファイルから、またはユーザー入力で取得
    dataset_name = dataset_name_entry.get() or "sample_camtrap_dp_dataset"
    dataset_id   = dataset_id_entry.get() or str(uuid.uuid4())
    title        = title_entry.get() or "Sample Camtrap Dataset"
    description  = description_entry.get() or "This is a sample dataset for the Camtrap Data Package specification."
    created      = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    contributors = contributors_entry.get() or config.get("contributors", [])
    sources      = sources_entry.get() or config.get("sources", [])
    licenses     = licenses_entry.get() or config.get("licenses", [])
    keywords     = keywords_entry.get() or config.get("keywords", [])
    image        = image_entry.get() or config.get("image", "")
    homepage     = homepage_entry.get() or config.get("homepage", "")
    bibliographicCitation = bibliographic_citation_entry.get() or config.get("bibliographicCitation", "")
    project      = project_entry.get() or config.get("project", {})
    coordinatePrecision = float(coordinate_precision_entry.get() or config.get("coordinatePrecision", 0.001))
    spatial      = spatial_entry.get() or config.get("spatial", {})
    temporal     = temporal_entry.get() or config.get("temporal", {})
    taxonomic    = taxonomic_entry.get() or config.get("taxonomic", [])
    relatedIdentifiers = related_identifiers_entry.get() or config.get("relatedIdentifiers", [])
    references   = references_entry.get() or config.get("references", [])   
    
    # datapackage.json の内容を定義（リソースなどは必要に応じて編集）
    datapackage = {
        "resources": [
            {
                "name": "deployments",
                "path": os.path.basename(deployment_info_file),
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.1/deployments-table-schema.json"
            },
            {
                "name": "media",
                "path": os.path.basename(media_file),
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.1/media-table-schema.json"
            },
            {
                "name": "observations",
                "path": os.path.basename(observation_file),
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0.1/observations-table-schema.json"
            },
        ],
        "profile": [],
        "name": dataset_name,
        "id": dataset_id,
        "created": created,
        "title": title,
        "description": description,
        "contributors": contributors,
        "sources": sources,
        "licenses": licenses,
        "keywords": keywords,
        "image": image,
        "homepage": homepage,
        "bibliographicCitation": bibliographicCitation,
        "project": project,
        "coordinatePrecision": coordinatePrecision,
        "spatial": spatial,
        "temporal": temporal,
        "taxonomic": taxonomic,
        "relatedIdentifiers": relatedIdentifiers,
        "references": references
    }
    
    # datapackage.jsonとして保存
    package_path = os.path.join(os.path.dirname(media_file), "datapackage.json")
    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(datapackage, f, ensure_ascii=False, indent=2)
    
    print("datapackage.json を作成しました。")
    root.destroy()

if __name__ == "__main__":

    root = tk.Tk()

    tk.Label(root, text="Dataset name").pack()
    dataset_name_entry = tk.Entry(root, width=50)
    dataset_name_entry.pack()

    tk.Label(root, text="Title").pack()
    title_entry = tk.Entry(root, width=50)
    title_entry.pack()

    tk.Label(root, text="Dataset ID").pack()
    dataset_id_entry = tk.Entry(root, width=50)
    dataset_id_entry.pack()

    tk.Label(root, text="Description").pack()
    description_entry = tk.Entry(root, width=50)
    description_entry.pack()


    tk.Label(root, text="Select the media file").pack()
    media_root_entry = tk.Entry(root, width=50)
    media_root_entry.pack()
    browse_button = tk.Button(root, text="Browse", command=browse_media_root)
    browse_button.pack()


    
    tk.Label(root, text="Select the deployment info file").pack()
    deployment_root_entry = tk.Entry(root, width=50)
    deployment_root_entry.pack()
    tk.Button(root, text="Browse", command=browse_deployment_root).pack()


    tk.Label(root, text="Select the observation file").pack()
    observation_root_entry = tk.Entry(root, width=50)
    observation_root_entry.pack()
    tk.Button(root, text="Browse", command=browse_observation_root).pack()

    tk.Label(root, text="Contributors").pack()
    contributors_entry = tk.Entry(root, width=50)
    contributors_entry.pack()

    tk.Label(root, text="Sources").pack()
    sources_entry = tk.Entry(root, width=50)
    sources_entry.pack()

    tk.Label(root, text="Licenses").pack()
    licenses_entry = tk.Entry(root, width=50)
    licenses_entry.pack()

    tk.Label(root, text="Keywords").pack()
    keywords_entry = tk.Entry(root, width=50)
    keywords_entry.pack()

    tk.Label(root, text="Image URL").pack()
    image_entry = tk.Entry(root, width=50)
    image_entry.pack()

    tk.Label(root, text="Homepage URL").pack()
    homepage_entry = tk.Entry(root, width=50)
    homepage_entry.pack()

    tk.Label(root, text="Bibliographic Citation").pack()
    bibliographic_citation_entry = tk.Entry(root, width=50)
    bibliographic_citation_entry.pack()

    tk.Label(root, text="Project").pack()
    project_entry = tk.Entry(root, width=50)
    project_entry.pack()

    tk.Label(root, text="Coordinate Precision").pack()
    coordinate_precision_entry = tk.Entry(root, width=50)
    coordinate_precision_entry.pack()

    tk.Label(root, text="Spatial").pack()
    spatial_entry = tk.Entry(root, width=50)
    spatial_entry.pack()

    tk.Label(root, text="Temporal").pack()
    temporal_entry = tk.Entry(root, width=50)
    temporal_entry.pack()

    tk.Label(root, text="Taxonomic").pack()
    taxonomic_entry = tk.Entry(root, width=50)
    taxonomic_entry.pack()

    tk.Label(root, text="Related Identifiers").pack()
    related_identifiers_entry = tk.Entry(root, width=50)
    related_identifiers_entry.pack()

    tk.Label(root, text="References").pack()
    references_entry = tk.Entry(root, width=50)
    references_entry.pack()

    tk.Button(root, text="Create datapackage.json", command=main).pack()

    root.mainloop()