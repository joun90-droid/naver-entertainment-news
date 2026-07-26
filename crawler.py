import requests
import re
import html
import os
from io import BytesIO
from PIL import Image
import concurrent.futures

class NaverEntertainCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.entertain.naver.com/'
        }
        self.image_cache = {}
        self.categories = {
            "실시간 랭킹": "https://api-gw.entertain.naver.com/news/ranking",
            "연예가 핫토픽": "https://api-gw.entertain.naver.com/news/articles?sid=221&pageSize=30",
            "방송·TV": "https://api-gw.entertain.naver.com/news/articles?sid=224&pageSize=30",
            "영화": "https://api-gw.entertain.naver.com/news/articles?sid=222&pageSize=30",
            "드라마": "https://api-gw.entertain.naver.com/news/articles?sid=225&pageSize=30",
            "뮤직": "https://api-gw.entertain.naver.com/news/articles?sid=7a5&pageSize=30",
            "해외연예": "https://api-gw.entertain.naver.com/news/articles?sid=309&pageSize=30"
        }

    def clean_text(self, text):
        if not text:
            return ""
        text = html.unescape(str(text))
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def fetch_category(self, category_name):
        url = self.categories.get(category_name)
        if not url:
            return []

        try:
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code != 200:
                return []

            data = r.json().get('result', {})
            raw_items = data.get('articles') or data.get('newsList') or []

            parsed_list = []
            for idx, item in enumerate(raw_items, 1):
                office = self.clean_text(item.get('officeName', '연예뉴스'))
                title = self.clean_text(item.get('title', '제목 없음'))
                summary = self.clean_text(item.get('subContent', ''))
                article_url = item.get('url', '')
                thumbnail = item.get('thumbnail', '')
                
                # Extract image URL if available
                if not thumbnail and 'image' in item:
                    thumbnail = item['image'].get('url', '')

                # Article ID for unique bookmarking
                office_id = item.get('officeId', '')
                article_id_num = item.get('articleId', '')
                unique_id = f"{office_id}_{article_id_num}" if office_id and article_id_num else article_url

                parsed_list.append({
                    "rank": idx,
                    "id": unique_id,
                    "office": office,
                    "title": title,
                    "summary": summary if summary else title,
                    "url": article_url,
                    "thumbnail": thumbnail,
                    "category": category_name
                })
            return parsed_list
        except Exception as e:
            print(f"Error fetching {category_name}: {e}")
            return []

    def fetch_image(self, url, size=(120, 90)):
        if not url:
            return None
        if url in self.image_cache:
            return self.image_cache[url]

        try:
            r = requests.get(url, headers=self.headers, timeout=4)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGB")
                img.thumbnail(size, Image.LANCZOS)
                self.image_cache[url] = img
                return img
        except Exception as e:
            pass
        return None
