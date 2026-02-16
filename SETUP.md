# Buzz Controller - Remote Setup Guide

## Overview

The Buzz Controller now supports **remote play** over the internet! The system is split into:

1. **Static HTML files** - Hosted anywhere (GitHub Pages, Netlify, etc.)
2. **Python server** - Runs on your computer and processes button presses
3. **ngrok tunnel** - Creates a public URL so anyone can connect

## Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install ngrok (if not already installed)
# Visit: https://ngrok.com/download
# Or on macOS:
brew install ngrok
```

### 2. Set Up ngrok

```bash
# Sign up at https://ngrok.com and get your auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 3. Start the Server

```bash
python buzz_controller.py
```

The server will:
- Start an ngrok tunnel
- Display a **SESSION CODE** (e.g., `ABCD1`)
- Show the public URL

### 4. Host the Static HTML Files

You have several options:

#### Option A: GitHub Pages (Best for permanent hosting)

1. Create a new GitHub repository
2. Upload the files from `static/` folder
3. Enable GitHub Pages in repository settings
4. Access at: `https://yourusername.github.io/repo-name/`

#### Option B: Netlify/Vercel (Easy drag-and-drop)

1. Go to [Netlify](https://netlify.com) or [Vercel](https://vercel.com)
2. Drag and drop the `static/` folder
3. Get instant public URL

#### Option C: Local Testing

```bash
cd static
python -m http.server 8000
```

Then open: `http://localhost:8000`

### 5. Players Join the Game

1. Players open your hosted HTML page
2. Enter the **SESSION CODE** shown by the server
3. Select their player number (1-4)
4. Start pressing buttons!

## How It Works

```
Player's Phone/Computer
       ↓
   Static HTML (hosted on GitHub Pages, etc.)
       ↓
   Enter Session Code
       ↓
   HTTPS Request → ngrok tunnel
       ↓
   Your Computer (Python Server)
       ↓
   PyAutoGUI presses keyboard keys
```

## Session Code System

The session code is derived from the ngrok URL subdomain. For example:
- ngrok URL: `https://abc123-def-456.ngrok-free.app`
- Session Code: `ABC123`

Players use this code to connect to your server.

## Customizing the HTML

The HTML files are in the `static/` folder:

- **index.html** - Landing page where players enter the code
- **controller.html** - The actual button controller interface

Feel free to customize colors, layouts, and styles!

## Advanced Configuration

### Custom Session Code

Edit `buzz_controller.py` and modify the `generate_session_code()` function:

```python
def generate_session_code():
    return 'MYCODE'  # Use any 4-6 letter code
```

### Custom Key Mappings

Edit the `KEY_MAPPING` dictionary in `buzz_controller.py`:

```python
KEY_MAPPING = {
    1: {'big': '1', 'blue': 'q', 'orange': 'w', 'green': 'e', 'yellow': 'r'},
    # ... add your custom mappings
}
```

### Running Without ngrok (Local Only)

```bash
python buzz_controller.py --local
```

This runs the server on your local network only (no internet access).

## Troubleshooting

### "ngrok not found"

Install ngrok from https://ngrok.com/download or via:
```bash
brew install ngrok  # macOS
```

### "Connection failed"

- Check that the server is running
- Verify the session code is correct
- Make sure ngrok tunnel is active
- Check firewall settings

### "CORS errors"

The server includes CORS headers, but if you still have issues:
- Make sure you're using HTTPS for the static site
- Check browser console for specific errors

### Players can't connect

- Verify ngrok is running (check for the public URL in terminal)
- Test the public URL in your own browser
- Some corporate networks block ngrok - try a different network

## Security Notes

- The ngrok free tier creates a new URL each time you restart
- Anyone with the session code can connect
- For private games, share the code only with intended players
- Consider ngrok's paid tier for permanent URLs and password protection

## API Endpoints

The server exposes these JSON endpoints:

- `GET /api/ping` - Health check
- `POST /api/press` - Send button press
- `GET /api/info` - Get server info

## Tips

1. **Share the code verbally** - Easier than sharing full URLs
2. **Use short codes** - 4-5 letters are easiest to remember
3. **Test locally first** - Use `--local` mode before going live
4. **Keep the terminal visible** - Shows all button presses in real-time

## Need Help?

- Check that all dependencies are installed: `pip list`
- Verify ngrok is authenticated: `ngrok config check`
- Test the server locally first: `python buzz_controller.py --local`

Enjoy your remote Buzz games! 🎮
