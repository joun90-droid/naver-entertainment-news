import os
import sys
import time
import json
import requests
from flask import Flask, send_from_directory, jsonify, request
from updater import update_cache_files

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

@app.route('/')
def index():
    """Explicit main route (/) serving index.html"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/health')
@app.route('/healthz')
@app.route('/ping')
def health():
    """Healthcheck endpoint for Cloud Run & Load Balancers"""
    return 'OK', 200

@app.route('/api/news')
def api_news():
    """Naver Entertain News API Proxy"""
    target_url = request.args.get('url', '')
    if not target_url:
        return jsonify({"error": "Missing url parameter"}), 400

    try:
        t_buster = str(int(time.time() * 1000))
        real_url = target_url + ("&" if "?" in target_url else "?") + f"_tb={t_buster}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.entertain.naver.com/',
            'Cache-Control': 'no-cache'
        }
        r = requests.get(real_url, headers=headers, timeout=6)
        return (r.content, r.status_code, {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    try:
        update_cache_files()
    except Exception as e:
        print(f"[Init Cache Warning] {e}")
        
    port = int(os.environ.get('PORT', 8080))
    print(f"🎬 Flask Server Running on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
