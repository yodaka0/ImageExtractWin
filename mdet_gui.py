import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
#from omegaconf import OmegaConf
from exec_mdet import find_image_files, run_detector_with_image_queue

def create_new_structure(src_dir, dst_dir):
    for dir, _ ,_ in os.walk(src_dir):
        dirs_name = dir.replace(dst_dir, "")
        new_dir = dst_dir + "\\" + dirs_name.replace("\\", "_out\\") + "_out"
        print("output directory is ", new_dir)
        os.makedirs(new_dir, exist_ok=True)


def browse_session_root():
    directory = filedialog.askdirectory()
    if directory:
        session_root_entry.delete(0, tk.END)
        session_root_entry.insert(0, directory)

def start_process():
    session_root = session_root_entry.get()
    threshold = float(threshold_entry.get())
    checkpoint = checkpoint_entry.get()
    print("Session Root:{} threshold:{} checkpoint".format(session_root, threshold, checkpoint))
    
    if checkpoint.startswith("r"):
        image_files = find_image_files(session_root)
        checkpoint = len(image_files) // int(checkpoint[1:])
    elif not checkpoint:
        checkpoint = None
    else:
        checkpoint = int(checkpoint)
    
    parent_dir = os.path.dirname(session_root)
    create_new_structure(session_root, parent_dir)
    image_files = find_image_files(session_root)

    run_detector_with_image_queue(image_files, threshold, session_root, checkpoint)
    messagebox.showinfo("Info", "Process completed successfully.")
    root.destroy()


root = tk.Tk()
root.title("CLI to GUI")

tk.Label(root, text="Session Root:").grid(row=0, column=0, padx=10, pady=5)
session_root_entry = tk.Entry(root, width=50)
session_root_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_session_root)
browse_button.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Threshold:").grid(row=1, column=0, padx=10, pady=5)
threshold_entry = tk.Entry(root, width=50)
threshold_entry.insert(0, "0.2") 
threshold_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Checkpoint:").grid(row=2, column=0, padx=10, pady=5)
checkpoint_entry = tk.Entry(root, width=50)
checkpoint_entry.grid(row=2, column=1, padx=10, pady=5)

start_button = tk.Button(root, text="Start", command=start_process)
start_button.grid(row=3, column=0, columnspan=3, pady=20)

root.mainloop()

