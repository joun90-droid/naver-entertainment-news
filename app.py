import os
import sys
import time
import requests
from flask import Flask, render_template_string, jsonify, request
from updater import update_cache_files

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_FALLBACK = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>연예뉴스 핫토픽</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #f5f6f7; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 20px 0; margin-bottom: 20px; }
        h1 { color: #111; font-size: 1.8rem; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .card h2 { font-size: 1.2rem; margin-bottom: 10px; color: #00bf18; }
        .card p { color: #555; font-size: 0.95rem; line-height: 1.5; }
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
            <h1>🔥 연예뉴스 핫토픽</h1>
        </header>
        <div class="card-grid">
            <div class="card">
                <h2>서비스 정상 작동 중</h2>
                <p>Google Cloud Run 배포 및 라우팅 설정이 완료되었습니다.</p>
            </div>
            <div class="card">
                <h2>자동 반응형 적용</h2>
                <p>PC에서는 넓은 카드형, 모바일에서는 1열 오토 레이아웃으로 출력됩니다.</p>
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
    return render_template_string(HTML_FALLBACK)

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
