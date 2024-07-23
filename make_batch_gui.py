import os

bat_contents = '''
@echo on
(
cd {}

conda activate pwlife

python mdet_gui.py

conda deactivate

pause
)
'''.format(os.getcwd())

# ファイルを書き込みモードで開く
with open('detect_gui.bat', 'w') as file:
    file.write(bat_contents) 
