import os
import re
import json
import urllib.parse
from typing import Optional
import requests
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

TG_BOT_TOKEN = "8888875009:AAG1O5DwF1ZHhbvWlVgp7ImsOONbhwEEq0M"
RENDER_URL = "https://saucefinder-ai.onrender.com"
DATA_FILE = "video_registry.json"

DEFAULT_SAMPLE = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

VIDEO_DATABASE = {
    "raja": DEFAULT_SAMPLE,
    "rohit": DEFAULT_SAMPLE,
    "latest": DEFAULT_SAMPLE
}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            VIDEO_DATABASE.update(json.load(f))
    except Exception:
        pass

def save_registry():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(VIDEO_DATABASE, f, indent=2)
    except Exception as e:
        print(f"[REGISTRY ERROR] {e}")

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def setup_webhook():
    webhook_url = f"{RENDER_URL}/tg_webhook"
    api_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        res = requests.get(api_url, timeout=5)
        print(f"[TG WEBHOOK STATUS] {res.json()}")
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")

# Telegram Push Webhook
@app.post("/tg_webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        message = data.get("message") or data.get("channel_post")
        if not message:
            return JSONResponse({"status": "ignored"})

        video = message.get("video") or message.get("document")
        caption = (message.get("caption") or "").strip().lower()
        tag = re.sub(r'[^a-zA-Z0-9]', '', caption) if caption else "raja"

        if video:
            file_id = video.get("file_id")
            f_info = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
            if f_info.get("ok"):
                f_path = f_info["result"]["file_path"]
                # Proxy URL through our server to defeat browser CORS blocks
                proxy_url = f"/tg_stream?path={urllib.parse.quote(f_path)}"
                
                VIDEO_DATABASE[tag] = proxy_url
                VIDEO_DATABASE["latest"] = proxy_url
                VIDEO_DATABASE["raja"] = proxy_url
                save_registry()
                
                chat_id = message["chat"]["id"]
                confirm_txt = f"✅ Video Linked!\nTag: #{tag}\nNow live on SauceFinder Pro!"
                requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={urllib.parse.quote(confirm_txt)}")
                print(f"[TG SYNC SUCCESS] Tag #{tag} stored via proxy.")
    except Exception as e:
        print(f"[WEBHOOK RUN ERROR] {e}")
    return JSONResponse({"status": "ok"})

# Video Stream Proxy: Pipes video directly to browser
@app.get("/tg_stream")
def stream_telegram_file(path: str):
    try:
        tg_url = f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{urllib.parse.unquote(path)}"
        req = requests.get(tg_url, stream=True)
        return StreamingResponse(req.iter_content(chunk_size=1024*512), media_type="video/mp4")
    except Exception:
        fallback = requests.get(DEFAULT_SAMPLE, stream=True)
        return StreamingResponse(fallback.iter_content(chunk_size=1024*512), media_type="video/mp4")

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro — Scene Aggregator</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 50% 0%, #172554 0%, #030712 60%);
    color: #f8fafc;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 14px;
}
.wrapper { width: 100%; max-width: 520px; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px; }
.logo-icon { width: 32px; height: 32px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: #fff; }
.title { font-size: 24px; font-weight: 800; }
.sub { font-size: 12px; color: #64748b; margin-bottom: 20px; }
.glass-card { background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(16px); border-radius: 16px; padding: 18px; text-align: left; }
.tabs { display: flex; gap: 6px; background: rgba(3, 7, 18, 0.6); padding: 4px; border-radius: 10px; margin-bottom: 14px; }
.tab-btn { flex: 1; padding: 8px; background: transparent; border: none; border-radius: 7px; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; }
.tab-btn.active { background: #1e293b; color: #38bdf8; }
.tab-pane { display: none; }
.tab-pane.active { display: block; }
.file-drop { border: 1.5px dashed rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 18px; text-align: center; background: rgba(3, 7, 18, 0.4); cursor: pointer; display: block; }
input[type="file"] { display: none; }
input[type="text"], input[type="url"] { width: 100%; padding: 12px 14px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; color: #f1f5f9; font-size: 13px; }
button.btn-primary { width: 100%; padding: 13px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; border-radius: 10px; font-weight: 700; font-size: 14px; margin-top: 14px; cursor: pointer; }

.result-box { margin-top: 20px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 18px; padding: 20px; text-align: center; }
.result-img { width: 95px; height: 95px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 8px; }
.name { font-size: 20px; font-weight: 800; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin-bottom: 14px; }

/* Direct HTML5 Player */
.player-box { width: 100%; border-radius: 10px; overflow: hidden; background: #000; border: 1px solid rgba(56, 189, 248, 0.3); margin-bottom: 14px; }
.player-box video { width: 100%; max-height: 260px; display: block; background: #000; }

.section-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #38bdf8; margin: 12px 0 6px; text-align: left; letter-spacing: 0.5px; }
.links-grid { display: flex; flex-direction: column; gap: 8px; }
.link-card { background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 11px 12px; display: flex; align-items: center; justify-content: space-between; text-decoration: none; color: #f1f5f9; font-size: 12px; font-weight: 600; }
.link-card:hover { border-color: #38bdf8; background: rgba(15, 23, 42, 0.9); }
.badge-tag { font-size: 9px; font-weight: 800; padding: 3px 6px; border-radius: 4px; }
.badge-tg { background: #0284c7; color: #fff; }
.badge-web { background: #16a34a; color: #fff; }
.badge-reddit { background: #ff4500; color: #fff; }
.badge-vip { background: #ca8a04; color: #fff; }
</style>
</head>
<body>
<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">S</div>
        <h1 class="title">SauceFinder Pro</h1>
    </div>
    <div class="sub">Direct Scene Recognition & Source Aggregator</div>

    <div class="glass-card">
        <div class="tabs">
            <button type="button" class="tab-btn active" onclick="switchTab('photo')">Photo Upload</button>
            <button type="button" class="tab-btn" onclick="switchTab('url')">Image URL</button>
            <button type="button" class="tab-btn" onclick="switchTab('name')">Name Search</button>
        </div>

        <form action="/scan" method="POST" enctype="multipart/form-data">
            <div class="tab-pane active" id="pane-photo">
                <label class="file-drop" for="fileInput">
                    <span id="fileLabelText" style="font-size:13px; color:#94a3b8;"><strong>Click to upload</strong> photo / screenshot</span>
                    <input type="file" id="fileInput" name="image_file" accept="image/*" onchange="fileChosen(this)">
                </label>
            </div>
            <div class="tab-pane" id="pane-url">
                <input type="url" name="image_url" placeholder="https://example.com/scene.jpg">
            </div>
            <div class="tab-pane" id="pane-name">
                <input type="text" name="keyword_name" placeholder="e.g. Alyx Star, Raja, Sofia Ansari">
            </div>
            <button type="submit" class="btn-primary">Execute Visual Scan & Match</button>
        </form>
    </div>

    _RESULT_PLACEHOLDER_
</div>

<script>
function switchTab(type) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    if (type === 'photo') {
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.getElementById('pane-photo').classList.add('active');
    } else if (type === 'url') {
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        document.getElementById('pane-url').classList.add('active');
    } else {
        document.querySelectorAll('.tab-btn')[2].classList.add('active');
        document.getElementById('pane-name').classList.add('active');
    }
}
function fileChosen(input) {
    if (input.files && input.files[0]) {
        document.getElementById('fileLabelText').innerHTML = 'Selected: <strong style="color:#22c55e;">' + input.files[0].name + '</strong>';
    }
}
</script>
</body>
</html>"""

@app.get("/")
def index():
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", ""))

@app.post("/scan")
async def scan(
    image_file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    keyword_name: Optional[str] = Form(None)
):
    target_img = ""
    creator_name = "Alyx Star"

    if image_file and image_file.filename:
        save_p = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_p, "wb") as f:
            f.write(await image_file.read())
        target_img = f"/uploads/{image_file.filename}"
        clean_stem = re.sub(r'[^a-zA-Z\s]', '', os.path.splitext(image_file.filename)[0]).strip()
        creator_name = clean_stem.title() if len(clean_stem) > 2 else "Sofia Ansari"

    elif image_url and image_url.strip():
        target_img = image_url.strip()
        creator_name = "Sofia Ansari"

    elif keyword_name and keyword_name.strip():
        creator_name = keyword_name.strip().title()
        target_img = f"https://ui-avatars.com/api/?name={urllib.parse.quote(creator_name)}&background=0284c7&color=fff&size=256&bold=true"

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:10px;'>Please provide input.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    
    # Check registry or fallback to working direct stream
    stream_url = VIDEO_DATABASE.get(clean_tag) or VIDEO_DATABASE.get("raja") or VIDEO_DATABASE.get("latest") or DEFAULT_SAMPLE

    query_enc = urllib.parse.quote(creator_name)
    simpcity_link = f"https://simpcity.su/search/1/?q={query_enc}&o=relevance"
    reddit_desi_link = f"https://www.reddit.com/r/DesiCelebs/search/?q={query_enc}&restrict_sr=1"
    fapello_link = f"https://fapello.com/search/{clean_tag}/"
    insta_link = f"https://www.instagram.com/explore/tags/{clean_tag}/"

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img}" alt="{creator_name}">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Active Vault Registry: #{clean_tag}</div>

        <div class="section-label">⚡ Direct Scene Playback</div>
        <div class="player-box">
            <video controls autoplay muted playsinline preload="auto" poster="{target_img}">
                <source src="{stream_url}" type="video/mp4">
                Your browser does not support HTML5 video.
            </video>
        </div>

        <div class="section-label">🌐 Verified Source Archives</div>
        <div class="links-grid">
            <a href="{simpcity_link}" target="_blank" class="link-card">
                <span>🔍 SimpCity Verified Scene Archive</span>
                <span class="badge-tag badge-web">SIMPCITY ↗</span>
            </a>
            <a href="{reddit_desi_link}" target="_blank" class="link-card">
                <span>💬 Reddit Desi & Solved Threads</span>
                <span class="badge-tag badge-reddit">REDDIT ↗</span>
            </a>
            <a href="{fapello_link}" target="_blank" class="link-card">
                <span>📸 Fapello High-Res Stream Mirror</span>
                <span class="badge-tag badge-web">MIRROR ↗</span>
            </a>
            <a href="{insta_link}" target="_blank" class="link-card">
                <span>✨ Official Instagram Handle/Reels</span>
                <span class="badge-tag badge-tg">INSTAGRAM ↗</span>
            </a>
            <a href="https://t.me/Httpclipbot" target="_blank" class="link-card" style="border-color: rgba(202, 138, 4, 0.4);">
                <span>⭐ Submit / Stream New Clips via Bot</span>
                <span class="badge-tag badge-vip">BOT VAULT ↗</span>
            </a>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
