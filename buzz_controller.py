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

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

print(f"GUI_AVAILABLE: {GUI_AVAILABLE}")
if (GUI_AVAILABLE == False):
    print("This means TKinter is not available. The server will run in CLI mode only.")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

KEY_MAPPING = {
    1: {'big': '1', 'blue': 'q', 'orange': 'w', 'green': 'e', 'yellow': 'r'}, # 1, QWER
    2: {'big': '2', 'blue': 'a', 'orange': 's', 'green': 'd', 'yellow': 'f'}, # 2, ASDF
    3: {'big': '3', 'blue': 'z', 'orange': 'x', 'green': 'c', 'yellow': 'v'}, # 3, ZXCV
    4: {'big': '4', 'blue': 'u', 'orange': 'i', 'green': 'o', 'yellow': 'p'}, # 4, UIOP
}

# Global variable to store server URL and session code
SERVER_INFO = {
    'session_code': None,
    'public_url': None
}


def generate_session_code():
    """Generate a random 4-6 letter session code"""
    return ''.join(random.choices(string.ascii_uppercase, k=5))


def get_cloudflared_path():
    """Get path to cloudflared executable (bundled or system)"""
    import os
    import platform
    
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        bundle_dir = sys._MEIPASS
        if platform.system() == 'Windows':
            cloudflared_path = os.path.join(bundle_dir, 'cloudflared.exe')
        else:
            cloudflared_path = os.path.join(bundle_dir, 'cloudflared')
        
        if os.path.exists(cloudflared_path):
            return cloudflared_path
    
    # Fall back to system cloudflared
    return 'cloudflared'


class BuzzControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Buzz Controller Server")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")
        
        # Main container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Buzz Controller Server",
            font=("Courier", 24, "bold"),
        )
        title_label.pack(pady=(0, 20))
        
        # Status indicator
        self.status_frame = tk.Frame(main_frame, padx=15, pady=10)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Starting server...",
            font=("Courier", 12),
            fg="white"
        )
        self.status_label.pack()
        
        # Info frame
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Session Code
        code_label = tk.Label(info_frame, text="Session Code:", font=("Courier", 10, "bold"))
        code_label.pack(anchor=tk.W)
        
        self.code_display = tk.Entry(
            info_frame,
            font=("Courier", 12, "bold"),
            justify="center",
            state="readonly",
            highlightbackground="#ffffff",
            highlightthickness=1
        )
        self.code_display.pack(fill=tk.X, pady=(5, 15))
        
        # Public URL
        url_label = tk.Label(info_frame, text="Server URL:", font=("Courier", 10, "bold"), highlightbackground="#ffffff", highlightthickness=2)
        url_label.pack(anchor=tk.W)
        
        self.url_display = tk.Entry(
            info_frame,
            font=("Courier", 12),
            justify="center",
            state="readonly",
            highlightbackground="#ffffff",
            highlightthickness=1
        )
        self.url_display.pack(fill=tk.X, pady=(5, 15))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.copy_url_btn = tk.Button(
            button_frame,
            text="Copy URL",
            command=self.copy_url,
            state=tk.DISABLED,
            font=("Courier", 10),
            bg="#3c3c3c",
            cursor="hand2",
            padx=15,
            pady=5
        )
        self.copy_url_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Log area (collapsible)
        self.show_logs = tk.BooleanVar(value=False)
        log_toggle = tk.Checkbutton(
            main_frame,
            text="Show Logs",
            variable=self.show_logs,
            command=self.toggle_logs,
            font=("Courier", 9)
        )
        log_toggle.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            font=("Courier", 9),
            state=tk.DISABLED
        )
    
    def toggle_logs(self):
        if self.show_logs.get():
            self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.root.geometry("500x600")
        else:
            self.log_text.pack_forget()
            self.root.geometry("500x400")
    
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        print(message)
    
    def update_status(self, status, color):
        """Update status indicator"""
        self.status_label.config(text=status)
        self.status_frame.config(bg=color)
        self.status_label.config(bg=color)
    
    def update_info(self, code, url):
        """Update session code and URL displays"""
        self.code_display.config(state=tk.NORMAL)
        self.code_display.delete(0, tk.END)
        self.code_display.insert(0, code)
        self.code_display.config(state="readonly")
        
        self.url_display.config(state=tk.NORMAL)
        self.url_display.delete(0, tk.END)
        self.url_display.insert(0, url)
        self.url_display.config(state="readonly")
        
        self.copy_url_btn.config(state=tk.NORMAL)
    
    def copy_url(self):
        """Copy URL to clipboard"""
        url = self.url_display.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.log("✅ URL copied to clipboard!")


def start_cloudflared(gui=None):
    """Start cloudflared tunnel and return the public URL"""
    def log(msg):
        if gui:
            gui.log(msg)
        else:
            print(msg)
    
    try:
        log("🚀 Starting Cloudflare tunnel...")
        log("⏳ Waiting for Flask server to be ready...")
        
        # Wait for Flask to be ready
        import requests
        for i in range(10):
            try:
                requests.get('http://localhost:5001/api/ping', timeout=1)
                log("✅ Flask server is ready!")
                break
            except:
                time.sleep(0.5)
        
        # Get cloudflared path (bundled or system)
        cloudflared_cmd = get_cloudflared_path()
        
        # Start cloudflared
        proc = subprocess.Popen(
            [cloudflared_cmd, 'tunnel', '--url', 'http://localhost:5001'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output to get the URL
        log("🔍 Getting tunnel URL...")
        for line in proc.stdout:
            if 'trycloudflare.com' in line or 'https://' in line:
                match = re.search(r'(https://[a-z0-9-]+\.trycloudflare\.com)', line)
                if match:
                    public_url = match.group(1)
                    SERVER_INFO['public_url'] = public_url
                    
                    # Extract subdomain for session code
                    match2 = re.search(r'https://([a-z0-9-]+)\.trycloudflare', public_url)
                    if match2:
                        subdomain = match2.group(1)
                        SERVER_INFO['session_code'] = subdomain.upper()
                    else:
                        SERVER_INFO['session_code'] = generate_session_code()
                    
                    log(f"✅ Cloudflare tunnel established!")
                    log(f"🌐 Public URL: {public_url}")
                    log(f"🔑 Session Code: {SERVER_INFO['session_code']}")
                    
                    if gui:
                        gui.root.after(0, lambda: gui.update_status("Server Running", "#2ecc71"))
                        gui.root.after(0, lambda: gui.update_info(SERVER_INFO['session_code'], public_url))
                    
                    return public_url
            
            if 'Connection' in line or 'Registered' in line:
                time.sleep(1)
                break
            
    except FileNotFoundError:
        log("⚠️  cloudflared not found!")
        log("Install: brew install cloudflare/cloudflare/cloudflared")
        if gui:
            gui.root.after(0, lambda: gui.update_status("❌ cloudflared not found", "#e74c3c"))
    except Exception as e:
        log(f"⚠️  Error: {e}")
        if gui:
            gui.root.after(0, lambda: gui.update_status("❌ Error starting tunnel", "#e74c3c"))
    
    return None


# API Endpoints
@app.route('/', methods=['GET'])
def home():
    """Root endpoint - simple message to verify server is running"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Buzz Controller Server</title>
    <style>
        body {{ font-family: Courier, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
    </style>
</head>
<body>
    <h1>Buzz Controller Server</h1>
    <div>Server is running!</div>
    <div>
        <h3>Session Info:</h3>
        <p>Session Code:</strong> <code>{SERVER_INFO.get('session_code', 'N/A')}</code></p>
        <p>Public URL:</strong> <code>{SERVER_INFO.get('public_url', 'http://localhost:5001')}</code></p>
    </div>
</body>
</html>'''

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
        print(f"\n🔑 SESSION CODE: {SERVER_INFO['session_code']}")
        print(f"   👆 Share this code OR the full URL below")
        print(f"\n🌐 SERVER URL: {SERVER_INFO['public_url']}")
        print(f"\n🔗 TEST: Visit {SERVER_INFO['public_url']} to verify it's working")
        print("\n📱 PLAYERS: Connect in 3 steps:")
        print("  1. Open a NEW terminal and run: python -m http.server 8000")
        print("     Then visit: http://localhost:8000")
        print(f"  2. Enter either:")
        print(f"     • CODE: {SERVER_INFO['session_code']}")
        print(f"     • URL: {SERVER_INFO['public_url']}")
        print("  3. Select your player number and play!")
        print("\n💡 For permanent hosting, upload HTML files to:")
        print("   - GitHub Pages: https://pages.github.com")
        print("   - Netlify: https://netlify.com")
    else:
        print(f"\n⚠️  Running in LOCAL mode only")
        print(f"🌐 Local URL: http://localhost:5001")
        print(f"🌐 Network URL: Find your local IP and use port 5001")
        print("\nTo enable remote access:")
        print("  1. Install cloudflared: brew install cloudflare/cloudflare/cloudflared")
        print("  2. Restart this server")
    
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    # Check for flags
    local_mode = '--local' in sys.argv
    cli_mode = '--cli' in sys.argv
    gui_mode = not cli_mode and GUI_AVAILABLE  # GUI by default if available
    
    def run_flask():
        app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
    
    if gui_mode and GUI_AVAILABLE:
        # GUI MODE
        root = tk.Tk()
        gui = BuzzControllerGUI(root)
        
        # Start Flask in background
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        gui.log("🚀 Starting Flask server...")
        time.sleep(2)
        
        if not local_mode:
            # Start cloudflared in background
            cloudflared_thread = threading.Thread(target=start_cloudflared, args=(gui,), daemon=True)
            cloudflared_thread.start()
        else:
            gui.log("Running in local mode")
            SERVER_INFO['session_code'] = "LOCAL"
            SERVER_INFO['public_url'] = "http://localhost:5001"
            gui.update_status("✅ Local Server Running", "#2ecc71")
            gui.update_info("LOCAL", "http://localhost:5001")
        
        # Run GUI
        root.mainloop()
    
    else:
        # CLI MODE
        if not local_mode:
            # Start Flask in a thread
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            time.sleep(2)
            start_cloudflared()
            print_instructions()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Server stopped. Goodbye!")
                sys.exit(0)
        else:
            print("Running in local mode (no cloudflared)")
            SERVER_INFO['session_code'] = "LOCAL"
            print_instructions()
            
            try:
                app.run(host="0.0.0.0", port=5001, debug=False)
            except KeyboardInterrupt:
                print("\n\n👋 Server stopped. Goodbye!")
                sys.exit(0)
