import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 연예뉴스 핫토픽</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, sans-serif; background-color: #f5f6f7; padding: 20px; }
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
            <h1>🔥 네이버 연예뉴스 핫토픽</h1>
        </header>
        <div class="card-grid">
            <div class="card">
                <h2>서비스 정상 연결 완료</h2>
                <p>Google Cloud Run 배포 및 404 오류 수정이 완료되었습니다.</p>
            </div>
            <div class="card">
                <h2>자동 반응형 레이아웃</h2>
                <p>PC에서는 시원한 카드형, 모바일에서는 1열 세로 화면으로 자동 조율됩니다.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
