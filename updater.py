import requests
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

categories = {
    "실시간 랭킹": "https://api-gw.entertain.naver.com/news/ranking",
    "연예가 핫토픽": "https://api-gw.entertain.naver.com/news/articles?sid=221&pageSize=30",
    "방송·TV": "https://api-gw.entertain.naver.com/news/articles?sid=224&pageSize=30",
    "영화": "https://api-gw.entertain.naver.com/news/articles?sid=222&pageSize=30",
    "드라마": "https://api-gw.entertain.naver.com/news/articles?sid=225&pageSize=30",
    "뮤직": "https://api-gw.entertain.naver.com/news/articles?sid=7a5&pageSize=30",
    "해외연예": "https://api-gw.entertain.naver.com/news/articles?sid=309&pageSize=30"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://m.entertain.naver.com/'
}

def update_cache_files():
    cache_data = {}
    for cat, url in categories.items():
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                res_json = r.json()
                if isinstance(res_json, dict):
                    data = res_json.get('result') or {}
                    if isinstance(data, dict):
                        items = data.get('articles') or data.get('newsList') or []
                        parsed = []
                        for idx, item in enumerate(items, 1):
                            office = item.get('officeName', '연예뉴스')
                            title = item.get('title', '')
                            summary = item.get('subContent', title)
                            article_url = item.get('url', '')
                            thumb = item.get('thumbnail', '')
                            if not thumb and isinstance(item.get('image'), dict):
                                thumb = item['image'].get('url', '')
                            parsed.append({
                                "rank": idx,
                                "id": f"{item.get('officeId', '')}_{item.get('articleId', '')}",
                                "office": office,
                                "title": title,
                                "summary": summary,
                                "url": article_url,
                                "thumbnail": thumb,
                                "category": cat
                            })
                        cache_data[cat] = parsed
        except Exception as e:
            print(f"Error caching {cat}: {e}")

    js_content = f"window.INITIAL_NEWS_CACHE = {json.dumps(cache_data, ensure_ascii=False, indent=2)};\n"
    target_path = os.path.join(os.path.dirname(__file__), "news_cache.js")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    return cache_data

if __name__ == "__main__":
    data = update_cache_files()
    print("Cache generated successfully! Realtime Ranking count:", len(data.get("실시간 랭킹", [])))
