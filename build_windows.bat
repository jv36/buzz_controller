@echo off
REM Build script for Windows .exe

echo Building Buzz Controller Windows App...

REM Install dependencies if needed
pip install -r requirements.txt

REM Download cloudflared if not present
if not exist cloudflared.exe (
    echo Downloading cloudflared...
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -o cloudflared.exe
    echo cloudflared downloaded
)

REM Build with PyInstaller
pyinstaller --name="BuzzController" ^
    --windowed ^
    --onefile ^
    --add-binary "cloudflared.exe;." ^
    --add-data "controller.html;." ^
    --add-data "index.html;." ^
    --hidden-import=PIL._tkinter_finder ^
    buzz_controller.py

echo Build complete!
echo App location: dist\BuzzController.exe
echo.
echo This app is fully standalone - no cloudflared installation needed!
echo To run: dist\BuzzController.exe
