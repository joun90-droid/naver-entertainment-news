import os
import sys
import time
import threading
import urllib.request
from urllib.error import URLError, HTTPError

from flask import Flask, request, Response, send_from_directory, abort, jsonify

from updater import update_cache_files

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)

NAVER_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.entertain.naver.com/",
    "Cache-Control": "no-cache",
}

NO_CACHE_MIMETYPES = (
    "text/html",
    "application/javascript",
    "text/javascript",
    "application/json",
)


@app.after_request
def add_common_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # This is a real-time news app: never let browsers/CDNs cache stale rankings.
    if resp.mimetype in NO_CACHE_MIMETYPES:
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp


@app.route("/health")
@app.route("/healthz")
@app.route("/ping")
def health():
    return "OK", 200


@app.route("/api/news")
def api_news():
    """Server-side proxy to Naver's entertainment news API.

    A direct browser fetch is blocked (403) without the correct Referer, so
    every category tab relies on this endpoint for genuine real-time data.
    """
    target_url = request.args.get("url", "")
    if not target_url:
        return jsonify({"error": "Missing url parameter"}), 400

    try:
        buster = str(int(time.time() * 1000))
        sep = "&" if "?" in target_url else "?"
        real_url = f"{target_url}{sep}_tb={buster}"

        req = urllib.request.Request(real_url, headers=NAVER_REQUEST_HEADERS)
        with urllib.request.urlopen(req, timeout=6) as r:
            content = r.read()
        return Response(content, mimetype="application/json; charset=utf-8")
    except (HTTPError, URLError) as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    # Never expose server-side source files through the static route.
    blocked_ext = (".py", ".pyc", ".bat", ".json.bak")
    if filename.endswith(blocked_ext) or filename in ("requirements.txt", "Dockerfile", "Procfile"):
        abort(404)

    full_path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(full_path):
        return send_from_directory(BASE_DIR, filename)
    abort(404)


def _background_realtime_sync():
    """Refresh the news_cache.js fallback file every 15 seconds."""
    print("[Background Sync] Live Naver News auto-sync loop started...")
    while True:
        try:
            update_cache_files()
        except Exception as e:
            print(f"[Background Sync Error] {e}")
        time.sleep(15)


def _bootstrap():
    try:
        update_cache_files()
    except Exception as e:
        print(f"[Boot Cache Error] {e}")

    sync_thread = threading.Thread(target=_background_realtime_sync, daemon=True)
    sync_thread.start()


# Run once per worker process (module import time), so it also works under gunicorn.
_bootstrap()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
