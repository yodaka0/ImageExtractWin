import os
import subprocess

current_dir = os.getcwd()

bat_contents = '''
@echo on
(
cd {}

conda activate pwlife

python mdet_gui.py

conda deactivate

pause
)
'''.format(current_dir)

# ファイルを書き込みモードで開く
with open('detect_gui.bat', 'w') as file:
    file.write(bat_contents) 


def get_desktop_path():
    # OneDriveのデスクトップパスを取得
    onedrive_path = os.environ.get('OneDrive')
    if onedrive_path:
        desktop_paths = [os.path.join(onedrive_path, 'Desktop'), os.path.join(onedrive_path, 'デスクトップ')]
        for path in desktop_paths:
            if os.path.exists(path):
                return path
    
    # OneDriveがない場合は通常のデスクトップパスを使用
    userprofile_path = os.environ.get('USERPROFILE')
    if userprofile_path:
        desktop_paths = [os.path.join(userprofile_path, 'Desktop'), os.path.join(userprofile_path, 'デスクトップ')]
        for path in desktop_paths:
            if os.path.exists(path):
                return path

    # デスクトップパスが見つからない場合はNoneを返す
    return None

def create_shortcuts_in_directory(directory):
    desktop = get_desktop_path()
    if not desktop:
        print("デスクトップパスが見つかりませんでした。")
        return

    shortcut_path = os.path.join(desktop, "detect_gui.lnk")
    target_path = os.path.join(directory, "detect_gui.bat")

        # ショートカットが既に存在する場合は削除
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

    vbs_script = f"""
Set WshShell = WScript.CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{target_path}"
Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
Shortcut.WindowStyle = 1
Shortcut.IconLocation = "{target_path}, 0"
Shortcut.Save
    """
    with open("create_shortcut.vbs", "w") as file:
        file.write(vbs_script)

    result = subprocess.run(['cscript', '//nologo', 'create_shortcut.vbs'], capture_output=True, text=True)
    os.remove("create_shortcut.vbs")

    if result.returncode != 0:
        print(f"Error creating shortcut: {result.stderr}")
    else:
        print("Shortcut created successfully")


if __name__ == "__main__":
    create_shortcuts_in_directory(current_dir)
    print("Shortcuts created successfully on the desktop.")
