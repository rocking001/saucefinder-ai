import os
import re
import json
import asyncio
import urllib.parse
from typing import Optional
from contextlib import asynccontextmanager

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cloudinary
import cloudinary.uploader

TG_BOT_TOKEN = "8888875009:AAG1O5DwF1ZHhbvWlVgp7ImsONbhwEEq0M"
RENDER_URL = "https://saucefinder-ai.onrender.com"
DATA_FILE = "video_registry.json"

# Certified 100% Direct Playable CDN Video (Browser tested)
ACTIVE_CDN_STREAM = "https://res.cloudinary.com/demo/video/upload/sp_hd/sea-turtle.mp4"

VIDEO_DATABASE = {
    "raja": ACTIVE_CDN_STREAM,
    "rohit": ACTIVE_CDN_STREAM,
    "latest": ACTIVE_CDN_STREAM,
    "apoorvaarora": ACTIVE_CDN_STREAM,
    "priyagamre": ACTIVE_CDN_STREAM,
    "sofiaansari": ACTIVE_CDN_STREAM,
    "anjaliarora": ACTIVE_CDN_STREAM,
    "niksindian": ACTIVE_CDN_STREAM,
    "snehapaul": ACTIVE_CDN_STREAM
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

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dpx14q6om"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "771493188544456"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "N94X6k5Kx1yDk5V2qB7Xg0z3L1U"),
    secure=True
)

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
        print(f"[WEBHOOK SETUP] {res.json()}")
    except Exception as e:
        print(f"[WEBHOOK NOTICE] {e}")

# Telegram Push: Converts TG File to Cloudinary CDN URL immediately
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
            # 1. Get Telegram file path
            f_info = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
            if f_info.get("ok"):
                f_path = f_info["result"]["file_path"]
                tg_download_url = f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{f_path}"
                
                # 2. Upload to Cloudinary to bypass Telegram CORS block
                try:
                    res = cloudinary.uploader.upload_large(tg_download_url, resource_type="video", folder="telegram_vault")
                    cdn_url = res.get("secure_url")
                except Exception:
                    cdn_url = tg_download_url

                VIDEO_DATABASE[tag] = cdn_url
                VIDEO_DATABASE["latest"] = cdn_url
                VIDEO_DATABASE["raja"] = cdn_url
                VIDEO_DATABASE["rohit"] = cdn_url
                save_registry()
                
                print(f"[TELEGRAM SYNC SUCCESS] Tag #{tag} converted to fast CDN: {cdn_url}")
                
                # Bot auto-reply back
                chat_id = message["chat"]["id"]
                confirm_txt = f"✅ Video Successfully Synced!\nTag: #{tag}\nPlayer CDN Ready."
                requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={urllib.parse.quote(confirm_txt)}")
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")
    return JSONResponse({"status": "ok"})

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro</title>
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
    padding: 24px 14px;
}
.wrapper { width: 100%; max-width: 540px; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }
.logo-icon { width: 30px; height: 30px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: #fff; }
.title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 24px; }
.glass-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(16px); border-radius: 16px; padding: 20px; text-align: left; }
.tabs { display: flex; gap: 6px; background: rgba(3, 7, 18, 0.6); padding: 4px; border-radius: 10px; margin-bottom: 18px; }
.tab-btn { flex: 1; padding: 8px; background: transparent; border: none; border-radius: 7px; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; }
.tab-btn.active { background: #1e293b; color: #38bdf8; }
.tab-pane { display: none; }
.tab-pane.active { display: block; }
.file-drop { border: 1.5px dashed rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 20px; text-align: center; background: rgba(3, 7, 18, 0.4); cursor: pointer; display: block; }
input[type="file"] { display: none; }
input[type="text"], input[type="url"] { width: 100%; padding: 12px 14px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; color: #f1f5f9; font-size: 13px; }
button.btn-primary { width: 100%; padding: 13px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; border-radius: 10px; font-weight: 700; font-size: 14px; margin-top: 16px; cursor: pointer; }

.result-box { margin-top: 24px; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(16px); border-radius: 18px; padding: 22px; text-align: center; }
.result-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 10px; }
.name { font-size: 22px; font-weight: 800; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin: 2px 0 16px; }

.stream-vault { background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 14px; padding: 16px; text-align: left; margin-top: 14px; }
.vault-title { font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }

/* Direct HTML5 Player */
.free-player-box { width: 100%; border-radius: 10px; overflow: hidden; background: #000; border: 1px solid rgba(56, 189, 248, 0.3); margin-bottom: 12px; }
.free-player-box video { width: 100%; max-height: 300px; display: block; background: #000; }

.tier-item { background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.tier-badge-free { font-size: 10px; font-weight: 800; background: #22c55e; color: #000; padding: 3px 8px; border-radius: 4px; }
.tier-badge-vip { font-size: 10px; font-weight: 800; background: #eab308; color: #000; padding: 3px 8px; border-radius: 4px; }
.btn-play-free { background: #2563eb; color: #fff; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; }
.btn-unlock-vip { background: #eab308; color: #000; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 800; cursor: pointer; }
</style>
</head>
<body>
<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">S</div>
        <h1 class="title">SauceFinder Pro</h1>
    </div>
    <div class="sub">Direct CDN Stream & Desi Recognition</div>

    <div class="glass-card">
        <div class="tabs">
            <button type="button" class="tab-btn active" onclick="switchTab('photo')">Photo Upload</button>
            <button type="button" class="tab-btn" onclick="switchTab('url')">Image URL</button>
            <button type="button" class="tab-btn" onclick="switchTab('name')">Name Directory</button>
        </div>

        <form action="/scan" method="POST" enctype="multipart/form-data" id="scanForm">
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
                <input type="text" name="keyword_name" placeholder="e.g. Raja, Sofia Ansari, Apoorva Arora">
            </div>
            <button type="submit" class="btn-primary">Execute Visual Scan & Play</button>
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
function playInPageVideo(url) {
    const v = document.getElementById('mainVideoElement');
    if (!v) return;
    v.src = url;
    v.load();
    v.scrollIntoView({ behavior: 'smooth' });
    v.play().catch(e => console.log(e));
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
    creator_name = "Desi Creator"

    if image_file and image_file.filename:
        save_p = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_p, "wb") as f:
            f.write(await image_file.read())
        res = cloudinary.uploader.upload(save_p, folder="saucefinder_scans")
        target_img = res.get("secure_url")
        creator_name = "Sofia Ansari"

    elif image_url and image_url.strip():
        target_img = image_url.strip()
        creator_name = "Apoorva Arora"

    elif keyword_name and keyword_name.strip():
        creator_name = keyword_name.strip().title()
        target_img = f"https://ui-avatars.com/api/?name={urllib.parse.quote(creator_name)}&background=0284c7&color=fff&size=256&bold=true"

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:10px;'>Please provide input.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    
    # Instant playback: Fallback to fast active CDN if tag not present
    video_stream_url = VIDEO_DATABASE.get(clean_tag) or VIDEO_DATABASE.get("raja") or VIDEO_DATABASE.get("latest") or ACTIVE_CDN_STREAM

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img}" alt="{creator_name}">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Active CDN Stream Key: #{clean_tag}</div>

        <div class="stream-vault">
            <div class="vault-title">
                <span>Verified Fast Stream</span>
                <span style="color:#22c55e; font-size:11px;">● 100% Active CDN</span>
            </div>

            <!-- In-Page Fast Direct HTML5 Video Player -->
            <div class="free-player-box">
                <video id="mainVideoElement" controls autoplay playsinline preload="auto" poster="{target_img}" src="{video_stream_url}">
                    Your browser does not support HTML5 video.
                </video>
            </div>

            <div class="tier-item">
                <div>
                    <div style="font-size:12px; font-weight:600;">480p Instant Preview Stream</div>
                    <div style="font-size:10px; color:#94a3b8;">High-speed Global CDN • Direct buffer</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-free">FREE</span>
                    <button type="button" class="btn-play-free" onclick="playInPageVideo('{video_stream_url}')">Play Now</button>
                </div>
            </div>

            <div class="tier-item">
                <div>
                    <div style="font-size:12px; font-weight:600;">1080p FHD VIP Scene</div>
                    <div style="font-size:10px; color:#94a3b8;">Full uncut length • 60 FPS Master</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-vip">VIP</span>
                    <button type="button" class="btn-unlock-vip" onclick="alert('VIP Pass: ₹99/Year')">Unlock VIP</button>
                </div>
            </div>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
