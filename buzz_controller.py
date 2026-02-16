from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui
import threading
import time
import random
import string
import subprocess
import re
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

KEY_MAPPING = {
    1: {'big': '1', 'blue': 'q', 'orange': 'w', 'green': 'e', 'yellow': 'r'},
    2: {'big': '2', 'blue': 'a', 'orange': 's', 'green': 'd', 'yellow': 'f'},
    3: {'big': '3', 'blue': 'z', 'orange': 'x', 'green': 'c', 'yellow': 'v'},
    4: {'big': '4', 'blue': 'u', 'orange': 'i', 'green': 'o', 'yellow': 'p'},
}

# Global variable to store ngrok URL and session code
SERVER_INFO = {
    'ngrok_url': None,
    'session_code': None,
    'public_url': None
}


def generate_session_code():
    """Generate a random 4-6 letter session code"""
    return ''.join(random.choices(string.ascii_uppercase, k=5))


def start_ngrok():
    """Start ngrok tunnel and return the public URL"""
    try:
        # Try to start ngrok using subprocess
        print("🚀 Starting ngrok tunnel...")
        proc = subprocess.Popen(
            ['ngrok', 'http', '5001', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give ngrok a moment to start and retry getting the URL
        import requests
        for attempt in range(6):  # Try for up to 12 seconds (6 attempts * 2 seconds)
            time.sleep(2)
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    SERVER_INFO['ngrok_url'] = public_url
                    SERVER_INFO['public_url'] = public_url
                    
                    # Extract subdomain for session code
                    match = re.search(r'https://([a-z0-9-]+)\.ngrok', public_url)
                    if match:
                        subdomain = match.group(1)
                        # Use first 6 chars of subdomain as code
                        SERVER_INFO['session_code'] = subdomain[:6].upper()
                    else:
                        SERVER_INFO['session_code'] = generate_session_code()
                    
                    print(f"✅ ngrok tunnel established!")
                    print(f"🌐 Public URL: {public_url}")
                    print(f"🔑 Session Code: {SERVER_INFO['session_code']}")
                    print()
                    return public_url
            except Exception as e:
                if attempt == 5:  # Last attempt
                    print(f"⚠️  Could not get ngrok URL from API: {e}")
                    print(f"💡 Tip: Make sure ngrok is configured with: ngrok config add-authtoken <your-token>")
                continue
            
    except FileNotFoundError:
        print("⚠️  ngrok not found. Install it from: https://ngrok.com/download")
        print("   Or run locally with: python buzz_controller.py --local")
    except Exception as e:
        print(f"⚠️  Could not start ngrok: {e}")
    
    return None


# API Endpoints
@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok", "session_code": SERVER_INFO['session_code']})


@app.route('/api/press', methods=['POST'])
def press_key():
    """Handle button press from remote client"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    player = data.get('player')
    button = data.get('button')
    
    if not player or not button:
        return jsonify({"status": "error", "message": "Missing player or button"}), 400
    
    try:
        player = int(player)
        if player not in KEY_MAPPING or button not in KEY_MAPPING[player]:
            return jsonify({"status": "error", "message": "Invalid player or button"}), 400
        
        key = KEY_MAPPING[player][button]
        
        def hold_key():
            pyautogui.keyDown(key)
            time.sleep(0.1)
            pyautogui.keyUp(key)
        
        threading.Thread(target=hold_key).start()
        
        return jsonify({
            "status": "success",
            "message": f"Player {player} pressed {button}",
            "key": key
        })
    except Exception as e:
        print(f"Error processing button press: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get server information"""
    return jsonify({
        "session_code": SERVER_INFO['session_code'],
        "public_url": SERVER_INFO['public_url'],
        "players": [1, 2, 3, 4]
    })



def print_instructions():
    """Print connection instructions"""
    print("\n" + "="*60)
    print("🎮  BUZZ CONTROLLER SERVER")
    print("="*60)
    
    if SERVER_INFO['public_url']:
        print(f"\n✅ Server is running and accessible from anywhere!")
        print(f"\n🌐 SERVER URL: {SERVER_INFO['public_url']}")
        print(f"   👆 Copy this full URL")
        print("\n📱 PLAYERS: Connect in 3 steps:")
        print("  1. Open a NEW terminal and run: python -m http.server 8000")
        print("     Then visit: http://localhost:8000")
        print(f"  2. Paste THIS URL in the form: {SERVER_INFO['public_url']}")
        print("  3. Select your player number and play!")
        print("\n💡 For permanent hosting, upload HTML files to:")
        print("   - GitHub Pages: https://pages.github.com")
        print("   - Netlify: https://netlify.com")
    else:
        print(f"\n⚠️  Running in LOCAL mode only")
        print(f"🌐 Local URL: http://localhost:5001")
        print(f"🌐 Network URL: Find your local IP and use port 5001")
        print("\nTo enable remote access:")
        print("  1. Install ngrok: https://ngrok.com/download")
        print("  2. Run: ngrok authtoken <your-token>")
        print("  3. Restart this server")
    
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    # Check for local mode flag
    local_mode = '--local' in sys.argv
    
    if not local_mode:
        # Try to start ngrok
        start_ngrok()
    else:
        print("Running in local mode (no ngrok)")
        SERVER_INFO['session_code'] = "LOCAL"
    
    # Print instructions
    print_instructions()
    
    # Start Flask server
    try:
        app.run(host="0.0.0.0", port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
