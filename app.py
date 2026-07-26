import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Desktop (card grid) & Mobile (single column) Responsive Layout
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 연예뉴스 핫토픽</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f5f6f7; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 20px 0; margin-bottom: 20px; }
        h1 { color: #111; font-size: 1.8rem; }
        
        /* PC Card Grid Layout */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-4px); }
        .card h2 { font-size: 1.2rem; margin-bottom: 10px; color: #00bf18; }
        .card p { color: #555; font-size: 0.95rem; line-height: 1.5; }

        /* Mobile Single-Column Responsive Layout */
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
                <h2>서비스가 정상 연결되었습니다</h2>
                <p>Google Cloud Run 배포 및 라우팅 설정이 완료되었습니다.</p>
            </div>
            <div class="card">
                <h2>반응형 레이아웃 자동 적용</h2>
                <p>PC에서는 카드형 다열 레이아웃, 모바일에서는 1열 오토 레이아웃으로 표시됩니다.</p>
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
    # Cloud Run assigns a dynamic PORT environment variable.
    # Defaulting to 8080 and binding strictly to host 0.0.0.0 prevents 404/connection refusal errors.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
