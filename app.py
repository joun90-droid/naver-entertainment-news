import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 연예뉴스 핫토픽</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, sans-serif; background: #f5f6f7; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 20px 0; }
        h1 { font-size: 1.8rem; color: #00bf18; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .card h2 { font-size: 1.2rem; margin-bottom: 8px; color: #111; }
        @media (max-width: 768px) { .card-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>🔥 연예뉴스 핫토픽</h1></header>
        <div class="card-grid">
            <div class="card">
                <h2>🟢 정상 서비스 실행 완료</h2>
                <p>Google Cloud Run 배포가 문제없이 완료되었습니다.</p>
            </div>
            <div class="card">
                <h2>📱 반응형 모드</h2>
                <p>PC 다열 카드 및 모바일 1열 오토 레이아웃이 지원됩니다.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.errorhandler(404)
def not_found(e):
    return render_template_string(HTML_LAYOUT), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
