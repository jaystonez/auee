@echo off
echo === Checking for Python ===
where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.x and re-run this script.
    pause
    exit /b
)

echo === Installing required Python modules ===
pip install -r requirements.txt

echo === Running OMMS Capsule Script ===
python omms.py

echo === Opening Shrine Dashboard ===
start "" "C:\mnt\data\index.html"

echo === Script complete ===
pause
