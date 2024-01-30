import os

bat_contents = '''
@echo on
(
cd {}

conda activate pwlife

python exec_mdet.py session_root=%~dp0 threshold=0.2

conda deactivate

pause
)
'''.format(os.getcwd())

# ファイルを書き込みモードで開く
with open('detect.bat', 'w') as file:
    file.write(bat_contents) 
