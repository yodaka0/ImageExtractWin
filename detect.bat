@echo on
(
cd ImageExtractWin

conda activate pwlife

python exec_mdet.py session_root=%~dp0 threshold=0.2

conda deactivate

pause
)
