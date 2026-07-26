import os
import sys
import json
import time
import urllib.parse
import urllib.request
import socket
import threading
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from updater import update_cache_files

sys.stdout.reconfigure(encoding='utf-8')

PORT = int(os.environ.get('PORT', 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class NaverEntertainWebHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent any browser caching for real-time responsiveness
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        req_path = parsed_path.path.strip('/')

        # 1. Health Check Endpoint for Cloud Run / Load Balancer
        if req_path in ['health', 'healthz', 'ping']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        # 2. Main Root Route ("/" or "") -> Explicitly serve index.html
        if req_path == '' or req_path == 'index.html':
            index_file_path = os.path.join(BASE_DIR, 'index.html')
            if os.path.exists(index_file_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(index_file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 Not Found: index.html missing')
                return

        # 3. API Proxy Endpoint ("/api/news")
        if req_path == 'api/news':
            query = urllib.parse.parse_qs(parsed_path.query)
            target_url = query.get('url', [''])[0]
            
            if not target_url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing url parameter"}')
                return

            try:
                t_buster = str(int(time.time() * 1000))
                real_url = target_url + ("&" if "?" in target_url else "?") + f"_tb={t_buster}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://m.entertain.naver.com/',
                    'Cache-Control': 'no-cache'
                }
                req = urllib.request.Request(real_url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as response:
                    content = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                err_msg = json.dumps({"error": str(e)}).encode('utf-8')
                self.wfile.write(err_msg)
            return

        # 4. Explicit Static File Serving (.css, .js, .json, .png, etc.)
        target_file = os.path.join(BASE_DIR, req_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            mime_type, _ = mimetypes.guess_type(target_file)
            if not mime_type:
                if target_file.endswith('.js'):
                    mime_type = 'application/javascript; charset=utf-8'
                elif target_file.endswith('.css'):
                    mime_type = 'text/css; charset=utf-8'
                elif target_file.endswith('.json'):
                    mime_type = 'application/json; charset=utf-8'
                else:
                    mime_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.end_headers()
            with open(target_file, 'rb') as f:
                self.wfile.write(f.read())
            return

        # Fallback 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(f'404 Not Found: {self.path}'.encode('utf-8'))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def background_realtime_sync():
    """Background loop to sync Naver live news every 15 seconds"""
    print("[Background Sync] Live Naver News auto-sync loop started...")
    while True:
        try:
            update_cache_files()
        except Exception as e:
            print(f"[Background Sync Error] {e}")
        time.sleep(15)

def run_server():
    # Initial cache generation on server boot
    try:
        update_cache_files()
    except Exception as e:
        print(f"[Boot Cache Error] {e}")

    # Start background auto sync thread
    sync_thread = threading.Thread(target=background_realtime_sync, daemon=True)
    sync_thread.start()

    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, NaverEntertainWebHandler)
    local_ip = get_local_ip()
    
    print("=" * 65)
    print(f" 🎬 [Jun Young-jae] Naver Live Entertain News Web Server Started!")
    print(f" 🖥️ PC Browser Access: http://localhost:{PORT}")
    print(f" 📱 Mobile/Phone Access (Same Wi-Fi): http://{local_ip}:{PORT}")
    print(f" ☁️ Listening on Port: {PORT}")
    print(" 🔄 Auto Real-time Live Sync: ACTIVE (15sec interval)")
    print("=" * 65)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    run_server()
