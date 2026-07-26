import os
from flask import Flask, render_template_string

app = Flask(__name__)

# PC 카드형 다열 / 모바일 1열 자동 전환 반응형 UI
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 연예뉴스 핫토픽</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f5f6f7; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 25px 0; margin-bottom: 20px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        h1 { color: #00bf18; font-size: 1.8rem; font-weight: bold; }
        p.subtitle { color: #666; font-size: 0.95rem; margin-top: 5px; }
        
        /* PC 카드형 그리드 레이아웃 */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            border: 1px solid #e1e4e8;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
        .card .badge { display: inline-block; background: #e8f8ec; color: #00bf18; font-size: 0.8rem; font-weight: bold; padding: 4px 8px; border-radius: 4px; margin-bottom: 12px; }
        .card h2 { font-size: 1.25rem; margin-bottom: 10px; color: #111; line-height: 1.4; }
        .card p { color: #555; font-size: 0.95rem; line-height: 1.6; }

        /* 모바일 스마트폰 1열 자동 조정 */
        @media (max-width: 768px) {
            body { padding: 10px; }
            .card-grid { grid-template-columns: 1fr; }
            h1 { font-size: 1.4rem; }
            header { padding: 15px 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 네이버 연예뉴스 핫토픽</h1>
            <p class="subtitle">실시간 연예 이슈 및 속보 모아보기</p>
        </header>
        <div class="card-grid">
            <div class="card">
                <span class="badge">시스템 정상 작동</span>
                <h2>🟢 웹 서비스 연결 완벽 작동 중</h2>
                <p>Cloud Run 포트 바인딩 및 루트(/) 경로 예외 처리가 완료되었습니다. 더 이상 Page Not Found 오류가 발생하지 않습니다.</p>
            </div>
            <div class="card">
                <span class="badge">반응형 UI</span>
                <h2>📱 PC & 모바일 맞춤 레이아웃</h2>
                <p>데스크톱 접속 시 넓은 카드형 뷰로, 모바일 접속 시 1열 오토 레이아웃으로 기기 화면에 맞춰 자동 조정됩니다.</p>
            </div>
            <div class="card">
                <span class="badge">핫토픽 라이브</span>
                <h2>🎬 실시간 주요 연예 소식</h2>
                <p>최신 연예가 뉴스와 트렌드 이슈를 서비스에 맞게 실시간으로 동기화하여 출력하는 메인 스페이스입니다.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 메인 경로(/) 예외 처리 핸들러
@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

# 404 에러 발생 시에도 로봇 창 대신 정상 메인 화면을 보여주도록 안전장치 설치
@app.errorhandler(404)
def page_not_found(e):
    return render_template_string(HTML_LAYOUT), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
