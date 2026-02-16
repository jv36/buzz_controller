# Buzz Controller - Quick Start

## What Changed?

Your buzz controller now works **over the internet**! 🌐

- ✅ HTML files are separate (can host anywhere)
- ✅ Players join using a URL or code
- ✅ Works from anywhere, not just same WiFi
- ✅ Uses ngrok for public access

## Running the Server

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install ngrok (one-time setup)
# Download from: https://ngrok.com/download
# Or on macOS: brew install ngrok

# 3. Configure ngrok (one-time setup)
ngrok config add-authtoken YOUR_TOKEN_HERE

# 4. Start the server
python buzz_controller.py
```

You'll see:
```
🔑 SESSION CODE: ABC12
🌐 Public URL: https://abc12-def-456.ngrok-free.app
```

## Hosting the HTML Files

### Quick Test (Local)
```bash
cd static
python -m http.server 8000
# Open: http://localhost:8000
```

### Production (GitHub Pages - Recommended)
1. Create GitHub repo
2. Upload `static/` folder contents
3. Enable Pages in Settings
4. Share the GitHub Pages URL with players

### Alternatives
- **Netlify**: Drag & drop `static/` folder at [netlify.com](https://netlify.com)
- **Vercel**: Same at [vercel.com](https://vercel.com)

## How Players Connect

1. Open your hosted HTML page
2. Enter the server URL shown in your terminal
3. Select player number
4. Play!

## Example Workflow

**You (Host):**
```bash
python buzz_controller.py
# Shows: https://abc123xyz.ngrok-free.app
```

**Players:**
1. Go to: `your-github-pages-url.github.io`
2. Paste: `https://abc123xyz.ngrok-free.app`
3. Pick player, press buttons!

## Troubleshooting

**"ngrok not found"**  
→ Install from https://ngrok.com/download

**"Connection failed"**  
→ Check that server is running and URL is correct

**Want local-only?**  
→ Run: `python buzz_controller.py --local`

See [SETUP.md](SETUP.md) for detailed instructions.
