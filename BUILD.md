# Buzz Controller - One App, Multiple Modes

The `buzz_controller.py` file now includes both GUI and CLI modes in ONE file!

## Quick Start - Testing

**GUI Mode (Default):**
```bash
python buzz_controller.py
```

**CLI Mode (Terminal only):**
```bash
python buzz_controller.py --cli
```

**Local Mode (No cloudflared):**
```bash
python buzz_controller.py --local
```

**GUI + Local:**
```bash
python buzz_controller.py --local --gui
```

## Building Standalone App

1. **Python 3.8+** installed
2. **cloudflared** installed:
   - Mac: `brew install cloudflare/cloudflare/cloudflared`
   - Windows: Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

## Quick Build

### For Mac (.app)

```bash
# Make build script executable
chmod +x build_mac.sh

# Run build
./build_mac.sh
```

The app will be created at `dist/BuzzController.app`

### For Windows (.exe)

```cmd
# Run build script
build_windows.bat
```

The executable will be created at `dist\BuzzController.exe`

## Manual Build (if scripts don't work)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build with PyInstaller

**Mac:**
```bash
pyinstaller --name="BuzzController" \
    --windowed \
    --onefile \
    buzz_controller_gui.py
```

**Windows:**
```cmd
pyinstaller --name="BuzzController" ^
    --windowed ^
    --onefile ^
    buzz_controller_gui.py
```

## Testing the App

1. **Run the built app:**
   - Mac: Double-click `dist/BuzzController.app`
   - Windows: Double-click `dist\BuzzController.exe`

2. **What you should see:**
   - A GUI window with "Buzz Controller Server" title
   - Status updating from "Starting..." to "Server Running"
   - Session code displayed
   - Public URL displayed
   - Buttons to copy URL and open in browser

## Features

The standalone app includes:
- ✅ Simple GUI showing session code and URL
- ✅ One-click URL copying
- ✅ Open in browser button
- ✅ Optional expandable log viewer
- ✅ No terminal window (can be shown via logs)
- ✅ All dependencies bundled

## Troubleshooting

### "cloudflared not found" error
Install cloudflared and make sure it's in your system PATH.

### Build fails on Mac
If you get permission errors:
```bash
chmod +x build_mac.sh
```

### App won't open on Mac (Security warning)
```bash
xattr -cr dist/BuzzController.app
```

### Large file size
The app bundles Python and all dependencies, so it will be 50-100MB. To reduce:
- Use `--onedir` instead of `--onefile` (faster but more files)
- Remove unnecessary packages from requirements.txt before building

## Distribution

Once built, you can distribute:
- **Mac**: Share the `.app` file (users may need to right-click → Open first time)
- **Windows**: Share the `.exe` file (users may see Windows Defender warning first time)

For easier distribution, consider creating:
- Mac: DMG installer (`hdiutil create`)
- Windows: Installer with Inno Setup or NSIS
