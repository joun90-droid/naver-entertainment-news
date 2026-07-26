import os
import sys
import json
import urllib.parse
import urllib.request
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8080

class NaverEntertainWebHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Handle API Proxy endpoint
        if parsed_path.path == '/api/news':
            query = urllib.parse.parse_qs(parsed_path.query)
            target_url = query.get('url', [''])[0]
            
            if not target_url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing url parameter"}')
                return

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://m.entertain.naver.com/'
                }
                req = urllib.request.Request(target_url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as response:
                    content = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content)
            except Exception as e:
                print(f"[API Proxy Error] {target_url} => {e}")
                self.send_response(500)
                self.end_headers()
                err_msg = json.dumps({"error": str(e)}).encode('utf-8')
                self.wfile.write(err_msg)
            return

        # Serve static files
        return super().do_GET()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, NaverEntertainWebHandler)
    local_ip = get_local_ip()
    
    print("=" * 65)
    print(f" [Jun Young-jae] Naver Entertain News Web Server Started!")
    print(f" PC Browser Access: http://localhost:{PORT}")
    print(f" Mobile/Phone Access (Same Wi-Fi): http://{local_ip}:{PORT}")
    print("=" * 65)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    run_server()
