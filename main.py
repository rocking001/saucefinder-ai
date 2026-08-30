import os
import re
import sqlite3
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

DB_FILE = "saucefinder.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_name TEXT,
        source TEXT,
        image_path TEXT,
        instagram_url TEXT,
        twitter_url TEXT,
        reddit_url TEXT,
        accurate_votes INTEGER DEFAULT 0,
        inaccurate_votes INTEGER DEFAULT 0,
        created_at TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

def log_scan(creator_name, source, img_path, insta, twitter, reddit):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scans (creator_name, source, image_path, instagram_url, twitter_url, reddit_url, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (creator_name, source, img_path, insta, twitter, reddit, datetime.now()))
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SauceFinder AI Engine</title>
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
        .btn-social { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600; }
        .btn-social:hover { border-color: #38bdf8; }
        .btn-reddit { color: #ff4500; border-color: rgba(255, 69, 0, 0.4); }
        .btn-reddit:hover { border-color: #ff4500; }
        
        .info-summary { background: #080d1a; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 15px; text-align: left; font-size: 13px; line-height: 1.5; color: #cbd5e1; }
        
        .video-box { margin-top: 20px; background: #000; border: 1px dashed #eab308; border-radius: 10px; overflow: hidden; position: relative; height: 150px; }
        .video-elem { width: 100%; height: 100%; object-fit: cover; transition: filter 0.4s ease; }
        .video-elem.blurred { filter: blur(14px) brightness(0.4); }
        .lock-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); }
        .lock-overlay.hidden { display: none; }
        .lock-btn { background: #eab308; color: #000; border: none; padding: 10px 20px; font-weight: 800; border-radius: 6px; cursor: pointer; font-size: 13px; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); align-items: center; justify-content: center; z-index: 100; }
        .modal.active { display: flex; }
        .modal-card { background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 24px; max-width: 360px; width: 90%; text-align: center; }
        .qr-placeholder { width: 140px; height: 140px; margin: 15px auto; background: #fff; padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #000; font-weight: bold; font-size: 13px; }
        .pay-btn-demo { background: #22c55e; color: #fff; border: none; padding: 11px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .close-btn { background: transparent; color: #94a3b8; border: none; font-size: 13px; cursor: pointer; margin-top: 12px; display: block; width: 100%; }
        
        .community-card { background: #080d1a; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin-top: 20px; text-align: left; }
        .poll-btns { display: flex; gap: 10px; margin-top: 8px; }
        .poll-btn { padding: 6px 14px; border: 1px solid #475569; background: #1e293b; color: #cbd5e1; border-radius: 6px; cursor: pointer; font-size: 12px; }
    </style>
</head>
<body>
<div class="wrapper">
    <div class="title">SauceFinder AI Engine</div>
    <div class="sub">Multi-Source Web & Keyword Intelligence Active</div>
    
    <div class="scan-card">
        <form action="/scan" method="POST" enctype="multipart/form-data">
            <input type="file" name="image_file" required accept="image/*">
            <button type="submit" class="btn-primary">Deep Sauce Scan</button>
        </form>
    </div>
    
    __RESULT_PLACEHOLDER__
</div>

<div class="modal" id="paywallModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px;">Unlock Video Sauce</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 12px;">Instant uncensored stream access</p>
        <div class="qr-placeholder">
            [ UPI QR Code ]<br>Pay ₹49 / $0.99
        </div>
        <button class="pay-btn-demo" onclick="completeUnlock()">Instant Unlock (Demo / Test)</button>
        <button class="close-btn" onclick="toggleModal(false)">Cancel</button>
    </div>
</div>

<script>
function toggleModal(show) {
    document.getElementById('paywallModal').className = show ? 'modal active' : 'modal';
}
function completeUnlock() {
    toggleModal(false);
    var video = document.getElementById('vaultVideo');
    var overlay = document.getElementById('lockOverlay');
    video.classList.remove('blurred');
    overlay.classList.add('hidden');
    video.controls = true;
    video.play();
    alert('Payment Successful! Video stream unlocked.');
}
function submitVote(scanId, voteType) {
    fetch('/vote', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'scan_id=' + scanId + '&vote=' + voteType
    }).then(res => res.json()).then(data => {
        document.getElementById('pollSection').innerHTML = '<span style="color:#22c55e; font-size:13px; font-weight:bold;">Feedback recorded! Thanks.</span>';
    });
}
</script>
</body>
</html>"""

def query_open_web_keywords(query: str):
    """DuckDuckGo HTML scraper to fetch creator snippet & handle without blocks"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query + ' instagram onlyfans bio')}"
    snippet = "Public web indexed profile."
    insta = None
    try:
        res = requests.post(url, headers=headers, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all('a', class_='result__snippet')
            if results:
                snippet = results[0].text.strip()
            links = soup.find_all('a', class_='result__url')
            for l in links:
                href = l.get('href', '')
                if 'instagram.com/' in href:
                    m = re.search(r'instagram\.com/([a-zA-Z0-9_\.]{3,30})', href)
                    if m:
                        insta = f"https://instagram.com/{m.group(1)}"
                        break
    except Exception:
        pass
    return snippet, insta

def search_reddit_sauce(query: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
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

def extract_visual_keywords(image_path: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    url = "https://yandex.com/images/search?rpt=imageview"
    try:
        with open(image_path, 'rb') as f:
            res = requests.post(url, headers=headers, files={'upfile': ('q.jpg', f, 'image/jpeg')}, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        tags = [t.text.strip() for t in soup.find_all(class_='Tags-ItemText')]
        filtered = [t for t in tags if not any(k in t.lower() for k in ['image', 'search', 'similar', 'photo', 'wallpaper', 'girl', 'model'])]
        if filtered:
            return filtered[0]
        title = soup.find('title')
        if title and "yandex" not in title.text.lower():
            clean = title.text.strip()
            if len(clean) > 2:
                return clean
    except Exception:
        pass
    return None

@app.get("/", response_class=HTMLResponse)
@app.get("/scan", response_class=HTMLResponse)
def index():
    return HTML_LAYOUT.replace("__RESULT_PLACEHOLDER__", "")

@app.post("/scan", response_class=HTMLResponse)
async def scan(image_file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, image_file.filename)
    with open(save_path, "wb") as f:
        f.write(await image_file.read())
    
    cdn_url = None
    if os.getenv("CLOUDINARY_CLOUD_NAME"):
        try:
            upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
            cdn_url = upload_res.get("secure_url")
        except Exception:
            pass
            
    final_img_url = cdn_url if cdn_url else f"/uploads/{image_file.filename}"
    
    # 1. Extract visual keyword
    extracted_keyword = extract_visual_keywords(save_path)
    if not extracted_keyword:
        # Fallback to image base name without extensions
        base = os.path.splitext(image_file.filename)[0]
        extracted_keyword = re.sub(r'[^a-zA-Z0-9\s]', ' ', base).strip()
        if not extracted_keyword or len(extracted_keyword) < 3:
            extracted_keyword = "Verified Creator"

    # 2. Search web & Reddit using extracted keywords
    web_snippet, direct_insta = query_open_web_keywords(extracted_keyword)
    reddit_info = search_reddit_sauce(extracted_keyword)
    
    final_name = extracted_keyword.title()
    final_insta = direct_insta if direct_insta else f"https://www.instagram.com/explore/tags/{final_name.replace(' ', '').lower()}/"
    twitter_url = f"https://x.com/search?q={urllib.parse.quote(final_name)}"
    
    scan_id = log_scan(
        final_name,
        "Keyword Web Indexing Engine",
        final_img_url,
        final_insta,
        twitter_url,
        reddit_info['url']
    )
    
    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{final_img_url}" alt="Target">
        <div class="name">{final_name}</div>
        <span class="source-tag">Identified via: Keyword Web Indexing Engine</span>
        
        <div class="info-summary">
            <strong>Web Intelligence Bio:</strong><br>
            {web_snippet[:140]}...
        </div>

        <div class="info-summary" style="border-color: rgba(255, 69, 0, 0.4);">
            <strong>Reddit Sauce ({reddit_info['subreddit']}):</strong><br>
            <span style="color:#94a3b8;">{reddit_info['title'][:70]}...</span>
        </div>
        
        <div class="links-wrap">
            <a class="btn-social" href="{final_insta}" target="_blank">Instagram Profile</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social btn-reddit" href="{reddit_info['url']}" target="_blank">Reddit Sauce Thread</a>
            <a class="btn-social" href="https://onlyfans.com" target="_blank">Official Channel</a>
        </div>
        
        <div class="video-box">
            <video id="vaultVideo" class="video-elem blurred" autoplay loop muted playsinline>
                <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
            </video>
            <div id="lockOverlay" class="lock-overlay">
                <div style="font-size: 13px; font-weight: 700; color: #fef08a; margin-bottom: 8px;">🔒 Full Video Stream Locked</div>
                <button type="button" class="lock-btn" onclick="toggleModal(true)">Unlock Full Video (₹49)</button>
            </div>
        </div>
        
        <div class="community-card" id="pollSection">
            <span style="font-size: 13px; color: #e2e8f0; font-weight:600;">Kya yeh creator identity sahi hai?</span>
            <div class="poll-btns">
                <button type="button" class="poll-btn" onclick="submitVote({scan_id}, 'yes')">Haan, Sahi Hai</button>
                <button type="button" class="poll-btn" onclick="submitVote({scan_id}, 'no')">Nahi, Galat Hai</button>
            </div>
        </div>
    </div>
    """
    return HTML_LAYOUT.replace("__RESULT_PLACEHOLDER__", result_html)

@app.post("/vote")
async def vote(scan_id: int = Form(...), vote: str = Form(...)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if vote == 'yes':
        cursor.execute("UPDATE scans SET accurate_votes = accurate_votes + 1 WHERE id = ?", (scan_id,))
    else:
        cursor.execute("UPDATE scans SET inaccurate_votes = inaccurate_votes + 1 WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()
    return JSONResponse({"status": "success"})

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, creator_name, source, image_path, instagram_url, accurate_votes, inaccurate_votes, created_at FROM scans ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    table_rows = ""
    for r in rows:
        table_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b;">#{r[0]}</td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b;"><img src="{r[3]}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover;"></td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b; font-weight: bold; color: #38bdf8;">{r[1]}</td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b; font-size: 12px; color: #94a3b8;">{r[2]}</td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b;"><a href="{r[4]}" target="_blank" style="color: #60a5fa; text-decoration: none;">View Profile</a></td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b; color: #22c55e;">+{r[5]}</td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b; color: #ef4444;">-{r[6]}</td>
            <td style="padding: 10px; border-bottom: 1px solid #1e293b; font-size: 11px; color: #64748b;">{str(r[7])[:19]}</td>
        </tr>
        """
    
    admin_html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>SauceFinder AI - Admin Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #f1f5f9; padding: 30px; margin: 0; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
            h1 {{ font-size: 22px; margin: 0; }}
            .stats {{ background: #0f172a; border: 1px solid #1e293b; padding: 12px 20px; border-radius: 8px; font-size: 14px; }}
            table {{ width: 100%; border-collapse: collapse; background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid #1e293b; }}
            th {{ background: #1e293b; padding: 12px 10px; text-align: left; font-size: 13px; color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>SauceFinder Intelligence Panel</h1>
                <p style="color: #64748b; font-size: 13px; margin: 4px 0 0;">Live SQLite Database Overview & Poll Audits</p>
            </div>
            <div class="stats">
                Total Scans: <strong style="color: #38bdf8;">{len(rows)}</strong>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Image</th>
                    <th>Identified Creator</th>
                    <th>Detection Engine</th>
                    <th>Social</th>
                    <th>Accuracy (Yes)</th>
                    <th>Inaccurate (No)</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>"""
    return HTMLResponse(admin_html)
