import tkinter as tk
from tkinter import filedialog
import pandas as pd
import datetime
import json
from tkinter import ttk
import sys
import os
import re


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CsvEditor:
    def __init__(self, root, spieces):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.load_button = tk.Button(self.frame, text="Load CSV", command=self.load_csv)
        self.load_button.pack()

        self.save_button = tk.Button(self.frame, text="Save to CSV", command=self.save_on_interrupt)
        self.save_button.pack()

        self.skip_button = tk.Button(self.frame, text="Skip", command=self.skip_row, state=tk.DISABLED)
        self.skip_button.pack()

        self.next_button = tk.Button(self.frame, text="Modified and Next", command=self.next_row, state=tk.DISABLED)
        self.next_button.pack()

        self.prev_button = tk.Button(self.frame, text="Previous", command=self.prev_row, state=tk.DISABLED)
        self.prev_button.pack()

        # 入力フィールドを作成します。
        self.input_field = tk.Entry(self.frame)
        self.input_field.pack()

        # ボタンを作成します。
        self.jump_button = tk.Button(self.frame, text="Move", command=self.go_to_row)
        self.jump_button.pack()

        self.entries = []
        self.data = None
        self.current_row = 0
        self.anotated_file = None
        self.spieces = spieces
        self.options = spieces["japanese_name"].tolist()
        # list of dicts
        #self.list_of_dicts = []

    def load(self, filepath):
        try:
            if filepath:
                if filepath.endswith(".csv"):
                    self.data = pd.read_csv(filepath, low_memory=False, encoding='utf-8')
                else:
                    print("Invalid file format")
                #load the length of the data
                self.data_length = len(self.data)
                #add a column for self.data
                if "deploymentID" not in self.data.columns:
                    self.data["deploymentID"] = input("Please input the deploymentID: ")
                if "scientificName" not in self.data.columns:
                    self.data["scientificName"] = False
                if "lifestage" not in self.data.columns:
                    self.data["lifestage"] = "unknown"
                if "sex" not in self.data.columns:
                    self.data["sex"] = "unknown"
                if "classificationMethod" not in self.data.columns:
                    self.data["classificationMethod"] = "machine"
                if "classifiedBy" not in self.data.columns:
                    self.data["classifiedBy"] = False
                if "classificationTimestamp" not in self.data.columns:
                    self.data["classificationTimestamp"] = False
                self.current_row = 0
                # get time within minite
                nowmin = str(datetime.datetime.now().strftime("%Y%m%d%H%M")) 
                # change the file name to new one
                file_dir = filepath.split("/")[:-1]
                self.anotated_file = "/".join(file_dir) + "/" + file_name + "_" + nowmin + ".csv"
                self.column = self.data.columns[0]
                self.column_name_num = {col: num for num, col in enumerate(self.data.columns)}
                #print(self.column_name_num)
                self.update_form()

        except Exception as e:
            print(e)
            raise


    def load_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.load(filepath)
        try:
            if os.path.exists("data/position.json"):
                saved_position = json.load(open("data/position.json", "r"))
                if saved_position["file"] == filepath:
                    self.go_to_row(saved_position["position"])
                    print(f"Move to {saved_position["position"]}.")
        except:
            
            print("No saved position found.")
            pass

    def skip_row(self):
        if self.data is not None:
            if self.current_row < self.data_length - 1:
                # save the input data to dict from the form
                input_dict = {}  # Create an empty dictionary to store the input data
                for frame, widget in self.entries:
                    input_data = widget.get()
                    column = frame.winfo_children()[0].cget("text")
                    input_dict[column] = input_data  # Save the input data to the dictionary
                    #self.data.at[self.current_row, column] = input_data
                #self.list_of_dicts.append(input_dict)
                self.current_row += 1
                self.update_form()
            else:
                self.root.destroy()

    def next_row(self):
        if self.data is not None:
            now = datetime.datetime.now()
            # save the input data to dict from the form
            input_dict = {}  # Create an empty dictionary to store the input data
            for frame, widget in self.entries:
                input_data = widget.get()
                column = frame.winfo_children()[0].cget("text")

                # データ型を適切にキャスト
                if pd.api.types.is_numeric_dtype(self.data[column]):
                    input_data = pd.to_numeric(input_data, errors='coerce')
                elif pd.api.types.is_datetime64_any_dtype(self.data[column]):
                    input_data = pd.to_datetime(input_data, errors='coerce')
            
                input_dict[column] = input_data  # Save the input data to the dictionary
                self.data.at[self.current_row, column] = input_data
            
            animal_jname  = self.data.at[self.current_row, 'scientificName']
            if bool(re.match(r'^[A-Za-z]+$', animal_jname)):
                animal_sname = animal_jname
            else:
                try:
                    animal_sname = self.spieces[self.spieces["japanese_name"] == animal_jname]["scientific_name"].values[0]
                except:
                    animal_sname = "unknown"
                
            print(f"scientificName was set to {animal_sname} at {now}")

            # Save classificationTimestamp and classifiedBy to self.data as well
            self.data.at[self.current_row, "scientificName"] = animal_sname
            self.data.at[self.current_row, "classificationTimestamp"] = str(now)
            self.data.at[self.current_row, "classifiedBy"] = user_name
            self.data.at[self.current_row, "classificationMethod"] = "human"
            print(f"Next button was clicked at {now}")
            print(self.data.iloc[self.current_row])
            #display the percentage of the data
            print(f"{self.current_row + 1}/{self.data_length} ({(self.current_row/self.data_length)*100}%) data was anotated.")
            if self.current_row < self.data_length -1:
                time_current = datetime.datetime.strptime(self.data.at[self.current_row, 'eventEnd'], "%Y:%m:%d %H:%M:%S")
                time_next = datetime.datetime.strptime(self.data.at[self.current_row+1, 'eventStart'], "%Y:%m:%d %H:%M:%S")
                time_diff = (time_next - time_current).total_seconds()
                if  abs(time_diff) < 120:
                    self.data.at[self.current_row + 1, 'scientificName'] = animal_jname
                self.current_row += 1
                self.update_form()
            elif self.current_row == self.data_length - 1:
                self.save_on_interrupt()
                self.root.destroy()
            else:
                self.root.destroy()

    def prev_row(self):
        if self.data is not None and self.current_row > 0:
            # remove latest dict from the list
            #self.list_of_dicts.pop()
            self.current_row -= 1
            self.update_form()

    def update_form(self):
        for frame, widget in self.entries:
            widget.destroy()
            frame.destroy()
        self.entries = []
        # the rest of your code

        row_data = self.data.iloc[self.current_row]
        for column in self.data.columns:
            frame = tk.Frame(self.root)
            frame.pack()
            label = tk.Label(frame, text=column)
            label.pack(side=tk.LEFT)
            if column == "scientificName":
                combobox = ttk.Combobox(frame, values=self.options)
                combobox.set(str(row_data[column]))
                combobox.pack(side=tk.LEFT)
                self.entries.append((frame, combobox))
                if row_data[column] == "False":
                    #change the color of default value
                    combobox.config(foreground="red")
            elif column == "lifestage":
                combobox = ttk.Combobox(frame, values=["adult", "subadult", "juvenile", "unknown"])
                combobox.set(str(row_data[column]))
                combobox.pack(side=tk.LEFT)
                self.entries.append((frame, combobox))
            elif column == "sex":
                combobox = ttk.Combobox(frame, values=["female", "male", "unknown"])
                combobox.set(str(row_data[column]))
                combobox.pack(side=tk.LEFT)
                self.entries.append((frame, combobox))
            else:
                entry = tk.Entry(frame)
                entry.insert(0, row_data[column])
                entry.pack(side=tk.LEFT)
                self.entries.append((frame, entry))

        self.next_button.config(state=tk.NORMAL if self.current_row < len(self.data) else tk.DISABLED)
        self.skip_button.config(state=tk.NORMAL if self.current_row < len(self.data) - 1 else tk.DISABLED)
        self.prev_button.config(state=tk.NORMAL if self.current_row > 0 else tk.DISABLED)
    
    def save_on_interrupt(self):
        
        #print(self.list_of_dicts)
        # form a dataframe from the list of dicts
        print(f"Data saved to {self.anotated_file}.")
        self.data.to_csv(self.anotated_file, index=False)
        #overwrite current_row name and self_anotate_csv
        with open("data/position.json", "w") as f:
            json.dump({"position": self.data.at[self.current_row, "img_id"], "file": self.anotated_file}, f)

    def on_close(self):
        self.save_on_interrupt()
        self.root.destroy()

    def go_to_row(self, input_value=None):

        if input_value is None:
            # ユーザーが入力した値を取得します。
            input_value = self.input_field.get()
        # 入力値に対応する行を検索します。
        matching_rows = self.data[self.data["img_id"] == input_value]
        #print(matching_rows)
        if not matching_rows.empty:
            # 最初の一致する行を現在の行として設定します。
            self.current_row = matching_rows.index[0]
            # フォームを更新します。
            self.update_form()


def preinput():
    global file_name_entry
    global user_name_entry
    global file_name
    global user_name
    file_name = file_name_entry.get()
    user_name = user_name_entry.get()
    root.destroy()



if __name__ == "__main__":
    csv_file_path = resource_path("data/spieces_name.csv")
    spieces = pd.read_csv(csv_file_path)
    
    root = tk.Tk()
    
    # ファイル名とユーザー名を入力するためのフレームの作成
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    # ファイル名のラベルと入力フィールド
    file_name_label = tk.Label(input_frame, text="file name:")
    file_name_label.pack(side=tk.LEFT)
    file_name_entry = tk.Entry(input_frame)
    file_name_entry.pack(side=tk.LEFT)

    # ユーザー名のラベルと入力フィールド
    user_name_label = tk.Label(input_frame, text="user name:")
    user_name_label.pack(side=tk.LEFT)
    user_name_entry = tk.Entry(input_frame)
    user_name_entry.pack(side=tk.LEFT)

    # 次へボタン
    next_button = tk.Button(input_frame, text="Next", command=preinput)
    next_button.pack()

    root.mainloop()

    root = tk.Tk()
    editor = CsvEditor(root, spieces)
    root.protocol("WM_DELETE_WINDOW", editor.on_close)

    try:
        root.mainloop()
    except:
        editor.save_on_interrupt()
        raise
