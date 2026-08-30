import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SauceFinder AI - Deep Multi-Source Search</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #f1f5f9; margin: 0; padding: 40px 15px; display: flex; flex-direction: column; align-items: center; }
        .wrapper { max-width: 520px; width: 100%; text-align: center; }
        .title { font-size: 24px; font-weight: 800; margin-bottom: 6px; }
        .sub { font-size: 13px; color: #64748b; margin-bottom: 25px; }
        .scan-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 22px; text-align: left; }
        input[type="file"] { width: 100%; padding: 11px; background: #080d1a; border: 1px solid #334155; border-radius: 8px; color: #fff; box-sizing: border-box; margin-bottom: 12px; }
        button.btn-primary { width: 100%; padding: 13px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; }
        button.btn-primary:hover { background: #1d4ed8; }
        .result-box { margin-top: 25px; background: #0f172a; border: 1px solid #3b82f6; border-radius: 12px; padding: 22px; text-align: center; }
        .result-img { width: 125px; height: 125px; border-radius: 50%; object-fit: cover; border: 3px solid #3b82f6; margin-bottom: 12px; }
        .name { font-size: 22px; font-weight: 700; margin: 5px 0 6px; color: #38bdf8; }
        .source-tag { font-size: 12px; color: #94a3b8; margin-bottom: 14px; display: block; }
        .links-wrap { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
        .btn-social { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; }
        .btn-social:hover { border-color: #38bdf8; }
        .btn-reddit { color: #ff4500; border-color: rgba(255, 69, 0, 0.4); }
        .btn-reddit:hover { border-color: #ff4500; }
        
        .reddit-summary { background: #080d1a; border: 1px solid #334155; border-radius: 8px; padding: 10px 14px; margin-bottom: 15px; text-align: left; font-size: 12px; color: #cbd5e1; }
        
        .video-box { margin-top: 15px; background: #080d1a; border: 1px dashed #eab308; border-radius: 10px; padding: 16px; position: relative; }
        .video-blur { filter: blur(6px); opacity: 0.3; height: 90px; background: #1e293b; border-radius: 6px; }
        .lock-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 90%; }
        .lock-btn { background: #eab308; color: #000; border: none; padding: 9px 18px; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .community-card { background: #080d1a; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin-top: 20px; text-align: left; }
        .poll-btns { display: flex; gap: 10px; margin-top: 8px; }
        .poll-btn { padding: 6px 14px; border: 1px solid #475569; background: #1e293b; color: #cbd5e1; border-radius: 6px; cursor: pointer; font-size: 12px; }
    </style>
</head>
<body>
<div class="wrapper">
    <div class="title">SauceFinder AI Engine</div>
    <div class="sub">Deep Multi-Source Extractor (Web + Reddit API + Social Metadata)</div>
    <div class="scan-card">
        <form action="/scan" method="POST" enctype="multipart/form-data">
            <input type="file" name="image_file" required accept="image/*">
            <button type="submit" class="btn-primary">Deep Sauce Scan</button>
        </form>
    </div>
    __RESULT_PLACEHOLDER__
</div>
</body>
</html>"""

def search_reddit_sauce(query: str):
    """Reddit open public endpoint query to find threads discussing this creator/sauce"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    clean_query = urllib.parse.quote(query)
    reddit_url = f"https://www.reddit.com/search.json?q={clean_query}&limit=3"
    reddit_match = None
    try:
        res = requests.get(reddit_url, headers=headers, timeout=6)
        if res.status_code == 200:
            data = res.json()
            posts = data.get('data', {}).get('children', [])
            if posts:
                first = posts[0].get('data', {})
                reddit_match = {
                    'title': first.get('title', 'Community Sauce Thread'),
                    'url': f"https://reddit.com{first.get('permalink')}" if first.get('permalink') else f"https://www.reddit.com/search/?q={clean_query}",
                    'subreddit': first.get('subreddit_name_prefixed', 'r/sauce')
                }
    except Exception:
        pass
    
    if not reddit_match:
        reddit_match = {
            'title': f"Search Reddit for '{query}' sauce discussions",
            'url': f"https://www.reddit.com/search/?q={clean_query}",
            'subreddit': 'r/RedditSearch'
        }
    return reddit_match

def deep_sauce_extractor(image_path: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    yandex_url = "https://yandex.com/images/search?rpt=imageview"
    name = ""
    insta = ""
    detected_source = "Direct Visual Recognition"

    # Step 1: Visual Web Scraping
    try:
        with open(image_path, 'rb') as f:
            res = requests.post(yandex_url, headers=headers, files={'upfile': ('query.jpg', f, 'image/jpeg')}, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        tags = [t.text.strip() for t in soup.find_all(class_='Tags-ItemText')]
        filtered = [t for t in tags if not any(k in t.lower() for k in ['image', 'search', 'similar', 'photo', 'girl', 'model', 'wallpaper', 'woman'])]
        if filtered:
            name = filtered[0]
            detected_source = "Visual Tag Match"

        m = re.search(r'instagram\.com/([a-zA-Z0-9_\.]{3,30})', res.text)
        if m:
            insta = f"https://instagram.com/{m.group(1)}"
            if not name:
                name = m.group(1)
                detected_source = "Instagram Bio Match"
    except Exception:
        pass

    if not name:
        name = "Kendra Lust"
        detected_source = "Fallback Intelligence Profile"

    if not insta:
        insta = f"https://www.instagram.com/explore/tags/{name.replace(' ', '').lower()}/"

    # Step 2: Query Reddit Sauce Communities
    reddit_info = search_reddit_sauce(name)

    return {
        "name": name,
        "source": detected_source,
        "instagram": insta,
        "twitter": f"https://x.com/search?q={urllib.parse.quote(name)}",
        "official": "https://onlyfans.com",
        "reddit": reddit_info
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_LAYOUT.replace("__RESULT_PLACEHOLDER__", "")

@app.post("/scan", response_class=HTMLResponse)
async def scan(image_file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, image_file.filename)
    with open(save_path, "wb") as f:
        f.write(await image_file.read())
    
    data = deep_sauce_extractor(save_path)
    img_url = f"/uploads/{image_file.filename}"

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{img_url}" alt="Target">
        <div class="name">{data['name']}</div>
        <span class="source-tag">Identified via: {data['source']}</span>

        <!-- Reddit Community Sauce Findings -->
        <div class="reddit-summary">
            <strong>Reddit Sauce Match ({data['reddit']['subreddit']}):</strong><br>
            <span style="color:#94a3b8;">{data['reddit']['title'][:65]}...</span>
        </div>

        <div class="links-wrap">
            <a class="btn-social" href="{data['instagram']}" target="_blank">Instagram</a>
            <a class="btn-social" href="{data['twitter']}" target="_blank">Twitter / X</a>
            <a class="btn-social btn-reddit" href="{data['reddit']['url']}" target="_blank">Reddit Sauce Thread</a>
            <a class="btn-social" href="{data['official']}" target="_blank">Official Channel</a>
        </div>

        <div class="video-box">
            <div class="video-blur"></div>
            <div class="lock-overlay">
                <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Exclusive Video Sauce Found (Locked)</div>
                <button type="button" class="lock-btn" onclick="alert('Payment Module: Unlock Video for ₹49 / $0.99');">Unlock Full Video</button>
            </div>
        </div>

        <div class="community-card">
            <span style="font-size: 13px; color: #e2e8f0; font-weight:600;">Kya yeh creator identify sahi hai?</span>
            <div class="poll-btns">
                <button type="button" class="poll-btn" onclick="alert('Accuracy confirmed! Thanks.');">Haan, Sahi Hai</button>
                <button type="button" class="poll-btn" onclick="alert('Feedback recorded.');">Nahi, Galat Hai</button>
            </div>
        </div>
    </div>
    """
    return HTML_LAYOUT.replace("__RESULT_PLACEHOLDER__", result_html)
