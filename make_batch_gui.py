import os
import subprocess

current_dir = os.getcwd()

sh_contents = '''
#!/bin/bash
cd {}

source activate pwlife

python mdet_gui.py

source deactivate
'''.format(current_dir)

# ファイルを書き込みモードで開く
with open('detect_gui.sh', 'w') as file:
    file.write(sh_contents)

# 実行権限を付与する
os.chmod('detect_gui.sh', 0o755)

def create_shortcuts_in_directory(directory):
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    #shortcut_path = os.path.join(desktop, "detect_gui_alias")
    target_path = os.path.join(directory, "detect_gui.command")

    # AppleScript to create alias
    applescript = """
    tell application "Finder"
        make alias file to POSIX file "{target_path}" at POSIX file "{desktop}"
        set name of result to "detect_gui_alias"
    end tell
    """.format(target_path,desktop)
    script_path = os.path.join(directory, "create_alias.scpt")
    with open(script_path, "w") as file:
        file.write(applescript)

    subprocess.run(['osascript', script_path])
    os.remove(script_path)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    create_shortcuts_in_directory(current_dir)
    print("Shortcuts created successfully on the desktop.")
