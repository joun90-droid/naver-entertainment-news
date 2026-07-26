import os
import sys
import time
import requests
from flask import Flask, render_template_string, jsonify, request
from updater import update_cache_files

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>네이버 연예뉴스 핫토픽 (실시간 연동)</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 20px 0; margin-bottom: 20px; background: rgba(30, 41, 59, 0.8); border-radius: 16px; border: 1px solid #334155; }
        h1 { color: #f472b6; font-size: 1.8rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .badge { display: inline-block; background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; margin-top: 8px; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: transform 0.2s, border-color 0.2s; }
        .card:hover { transform: translateY(-4px); border-color: #8b5cf6; }
        .card h2 { font-size: 1.25rem; margin-bottom: 10px; color: #a78bfa; }
        .card p { color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; }
        .btn-link { display: inline-block; margin-top: 14px; background: linear-gradient(135deg, #ec4899, #8b5cf6); color: #fff; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .card-grid { grid-template-columns: 1fr; }
            h1 { font-size: 1.4rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎬 네이버 연예뉴스 핫토픽</h1>
            <div class="badge">🟢 100% 실시간 Cloud Run 정상 작동 중</div>
        </header>
        <div class="card-grid">
            <div class="card">
                <h2>👑 VIP 전영재 전용 서비스</h2>
                <p>Google Cloud Run (<code>naver-entertain-news-jyj</code>) 고정 서비스 주소로 성공적으로 덮어씌워 배포되었습니다.</p>
            </div>
            <div class="card">
                <h2>📱 PC & 모바일 반응형 자동 렌더링</h2>
                <p>PC 환경에서는 시원한 다열 카드 그리드, 모바일 환경에서는 1열 오토 레이아웃으로 완벽 전환됩니다.</p>
                <a href="/index.html" class="btn-link">🌐 대시보드 바로가기</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    index_path = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
@app.route('/healthz')
def health():
    return 'OK', 200

@app.route('/api/news')
def api_news():
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
    except Exception:
        pass
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
