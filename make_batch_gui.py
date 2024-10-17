import os
from pathlib import Path
import subprocess

current_dir = os.getcwd()

mdet_bat_contents = '''
@echo on
(
cd {}

conda activate pwlife

python mdet_gui.py

conda deactivate

pause
)
'''.format(current_dir)

ano_bat_contents = '''
@echo on
(
cd {}
cd anotate

python anotateform_soft.py

pause
)
'''.format(current_dir)

# ファイルを書き込みモードで開く
with open('detect_gui.bat', 'w') as file:
    file.write(mdet_bat_contents) 

with open('anotation_form.bat', 'w') as file:
    file.write(ano_bat_contents) 




def get_desktop_path():
    # Step 1: OneDriveフォルダの確認
    onedrive_path = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    
    if onedrive_path:
        # OneDrive内のDesktopフォルダのパスを生成
        desktop_path = Path(onedrive_path) / "Desktop"
        if desktop_path.exists():
            return desktop_path

        # 日本語名の場合
        desktop_path_jp = Path(onedrive_path) / "デスクトップ"
        if desktop_path_jp.exists():
            return desktop_path_jp

    # Step 2: ローカルのデスクトップフォルダの確認
    home_dir = Path.home()

    # ローカルのDesktopフォルダを確認
    local_desktop_path = home_dir / "Desktop"
    if local_desktop_path.exists():
        return local_desktop_path

    # 日本語名の場合
    local_desktop_path_jp = home_dir / "デスクトップ"
    if local_desktop_path_jp.exists():
        return local_desktop_path_jp

    # どちらも見つからない場合
    raise FileNotFoundError("Desktop folder not found in both OneDrive and local directories.")


def create_shortcuts_in_directory(directory,bat_name):
    desktop_path = get_desktop_path()
    print(desktop_path)
    shortcut_path = os.path.join(desktop_path, f"{bat_name}.lnk")
    target_path = os.path.join(directory, f"{bat_name}.bat")
    print(f"Creating shortcut for {bat_name} at {shortcut_path}")

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

    subprocess.run(['cscript', '//nologo', 'create_shortcut.vbs'])
    os.remove("create_shortcut.vbs")


if __name__ == "__main__":
    create_shortcuts_in_directory(current_dir,"detect_gui")
    create_shortcuts_in_directory(current_dir,"anotation_form")
    print("Shortcuts created successfully on the desktop.")
