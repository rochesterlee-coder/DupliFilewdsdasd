@echo off
cd /d "%~dp0"
py -3 -m pip install --upgrade pyinstaller
py -3 -m PyInstaller --noconfirm --onefile --windowed --name DupliFile --icon duplifile.ico app.py
echo Done! Check the dist folder.
pause
