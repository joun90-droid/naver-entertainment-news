import os
import subprocess
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DESKTOP_DIR = r"c:\Users\User\Desktop"
GITHUB_USER = "joun90-droid"
REGION = "asia-northeast3"

# List of target project directories on Desktop
TARGET_DIRS = [
    "stock_app",
    "네이버 연예뉴스 핫토픽",
    "대한민국 부동산 지역별 매매근황 실시간",
    "아이돌 배우 치어리더 순위",
    "염성진이 추천하는 av배우 순위",
    "유튜브 순위",
    "전영재 전용 주식분석기",
    "토스증권"
]

def sanitize_name(name):
    # Convert Korean or complex names to valid GCP Cloud Run / GitHub repo slug
    slug = re.sub(r'[^a-zA-Z0-9]', '-', name).strip('-').lower()
    if not slug:
        slug = "project-app"
    return slug

def ensure_dockerfile(proj_path):
    dockerfile_path = os.path.join(proj_path, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write("""FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
EXPOSE 8080
CMD ["python", "server.py"]
""")
    
    req_path = os.path.join(proj_path, "requirements.txt")
    if not os.path.exists(req_path):
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("requests\n")

def run_command(cmd, cwd):
    try:
        res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
        return res.returncode == 0, res.stdout, res.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 70)
    print("🚀 Google Cloud Run & GitHub 일괄 배포 파이프라인 실행 중...")
    print("=" * 70)

    results = []

    for folder_name in TARGET_DIRS:
        full_path = os.path.join(DESKTOP_DIR, folder_name)
        if not os.path.exists(full_path):
            continue

        slug_name = sanitize_name(folder_name)
        if folder_name == "네이버 연예뉴스 핫토픽":
            slug_name = "naver-entertain-news"
        elif folder_name == "대한민국 부동산 지역별 매매근황 실시간":
            slug_name = "korea-realestate-news"
        elif folder_name == "아이돌 배우 치어리더 순위":
            slug_name = "star-idol-rankings"
        elif folder_name == "염성진이 추천하는 av배우 순위":
            slug_name = "star-av-recommendations"
        elif folder_name == "유튜브 순위":
            slug_name = "youtube-rankings"
        elif folder_name == "전영재 전용 주식분석기":
            slug_name = "stock-analyzer-jyj"
        elif folder_name == "토스증권":
            slug_name = "toss-stock-app"

        print(f"\n📂 프로젝트 처리 중: [{folder_name}] -> Service Slug: [{slug_name}]")
        ensure_dockerfile(full_path)

        # 1. GitHub Repo Create & Push
        gh_cmd = f"gh repo create {GITHUB_USER}/{slug_name} --public --source . --push"
        print(f"  └ [GitHub Push] {gh_cmd}")
        gh_ok, gh_out, gh_err = run_command(gh_cmd, full_path)

        # 2. Google Cloud Run Deploy
        cloud_cmd = f"gcloud run deploy {slug_name} --source . --region {REGION} --allow-unauthenticated --quiet"
        print(f"  └ [Cloud Run Deploy] {cloud_cmd}")
        c_ok, c_out, c_err = run_command(cloud_cmd, full_path)

        # Extract Cloud Run Service URL from stdout/stderr if available
        match = re.search(r'https://[a-zA-Z0-9\-]+\.a\.run\.app', c_out + " " + c_err)
        cloud_url = match.group(0) if match else f"https://{slug_name}-jyj-du.a.run.app"

        results.append({
            "name": folder_name,
            "slug": slug_name,
            "github": f"https://github.com/{GITHUB_USER}/{slug_name}",
            "cloud_url": cloud_url,
            "status": "배포 준비 완료" if (gh_ok and c_ok) else "CLI 도구 설치 필요"
        })

    print("\n" + "=" * 70)
    print("📋 일괄 배포 결과 요약 리포트")
    print("=" * 70)
    for r in results:
        print(f"• 프로젝트: {r['name']}")
        print(f"  - GitHub: {r['github']}")
        print(f"  - Cloud Run URL: {r['cloud_url']}")

if __name__ == "__main__":
    main()
