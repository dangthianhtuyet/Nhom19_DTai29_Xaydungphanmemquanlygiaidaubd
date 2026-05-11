@echo off
title Football Manager
echo Dang kiem tra PySide6...
python -c "import PySide6" 2>nul
if errorlevel 1 (
    echo Chua co PySide6, dang cai dat...
    pip install PySide6
)
echo Dang khoi dong Football Manager...
python "%~dp0main.py"
pause
