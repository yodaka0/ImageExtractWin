import os
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

with open('anotation.bat', 'w') as file:
    file.write(ano_bat_contents) 


def create_shortcuts_in_directory(directory):
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    shortcut_path = os.path.join(desktop, "detect_gui.lnk")
    target_path = os.path.join(directory, "detect_gui.bat")

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
    create_shortcuts_in_directory(current_dir)
    print("Shortcuts created successfully on the desktop.")
