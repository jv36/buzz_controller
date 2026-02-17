#!/bin/bash
# Build script for Mac app

echo "🚀 Building Buzz Controller Mac App..."

# Install dependencies if needed
pip install -r requirements.txt

# Download cloudflared if not present
if [ ! -f "cloudflared" ]; then
    echo "📥 Downloading cloudflared..."
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz -o cloudflared.tgz
    tar -xzf cloudflared.tgz
    chmod +x cloudflared
    rm cloudflared.tgz
    echo "✅ cloudflared downloaded"
fi

# Build with PyInstaller
pyinstaller --name="BuzzController" \
    --windowed \
    --onefile \
    --add-binary "cloudflared:." \
    --add-data "controller.html:." \
    --add-data "index.html:." \
    --hidden-import=PIL._tkinter_finder \
    buzz_controller.py

echo "✅ Build complete!"
echo "📦 App location: dist/BuzzController.app"
echo ""
echo "✨ This app is fully standalone - no cloudflared installation needed!"
echo "To run: open dist/BuzzController.app"
echo ""
echo "To run: open dist/BuzzController.app"
