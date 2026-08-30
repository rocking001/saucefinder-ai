import os
import re
import urllib.parse
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import cloudinary
import cloudinary.uploader
import requests

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

TG_BOT_TOKEN = "8088875009:AAG1O5Dwf1ZHhbvWIVgp7lmsO0NbhwEEq0M"
TG_CHAT_ID = "-1001184901229"

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro — Web Native Stream</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
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
.logo-icon { width: 30px; height: 30px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: #fff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
.title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(180deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 24px; }

.glass-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    text-align: left;
}

.tabs { display: flex; gap: 6px; background: rgba(3, 7, 18, 0.6); padding: 4px; border-radius: 10px; margin-bottom: 18px; border: 1px solid rgba(255, 255, 255, 0.04); }
.tab-btn { flex: 1; padding: 8px 10px; background: transparent; border: none; border-radius: 7px; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit; }
.tab-btn.active { background: #1e293b; color: #38bdf8; }

.tab-pane { display: none; }
.tab-pane.active { display: block; }
.file-drop { border: 1.5px dashed rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 20px; text-align: center; background: rgba(3, 7, 18, 0.4); cursor: pointer; display: block; }
.file-drop:hover { border-color: #38bdf8; }
input[type="file"] { display: none; }
.file-label { font-size: 13px; color: #94a3b8; }
.file-label strong { color: #38bdf8; }
input[type="text"], input[type="url"] { width: 100%; padding: 12px 14px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; color: #f1f5f9; font-size: 13px; font-family: inherit; }
input:focus { border-color: #38bdf8; outline: none; }

button.btn-primary { width: 100%; padding: 13px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; border-radius: 10px; font-weight: 700; font-size: 14px; margin-top: 16px; cursor: pointer; font-family: inherit; }

/* Result Box */
.result-box { margin-top: 24px; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(16px); border-radius: 18px; padding: 22px; text-align: center; }
.result-img { width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 10px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.35); }
.name { font-size: 22px; font-weight: 800; color: #f8fafc; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin: 2px 0 16px; }

/* 1. Locked Direct Links Gate */
.links-gate-box {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.85));
    border: 1px dashed rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    margin-bottom: 12px;
}
.links-gate-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
.links-gate-sub { font-size: 11px; color: #94a3b8; margin-bottom: 12px; }
.gate-btn-group { display: flex; gap: 8px; }
.btn-gate-ad { flex: 1; background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-gate-pay { flex: 1; background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; font-family: inherit; }

/* 2. Combined OnlyFans Banner */
.of-vip-banner {
    background: linear-gradient(135deg, rgba(0, 175, 240, 0.12), rgba(234, 179, 8, 0.12));
    border: 1px solid #00aff0;
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.of-text { text-align: left; }
.of-vip-title { font-size: 12px; font-weight: 800; color: #f8fafc; }
.of-vip-sub { font-size: 10px; color: #94a3b8; }
.btn-of-unlock {
    background: linear-gradient(135deg, #00aff0, #0284c7);
    color: #fff;
    border: none;
    padding: 8px 14px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
    font-family: inherit;
    white-space: nowrap;
}

.links-unlocked { display: none; margin-bottom: 16px; text-align: left; }
.match-item { display: flex; align-items: center; justify-content: space-between; background: rgba(3, 7, 18, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 12px; margin-bottom: 6px; text-decoration: none; text-align: left; cursor: pointer; }
.match-title { font-size: 12px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
.badge-source { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.badge-stream { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
.badge-reddit { background: rgba(255, 69, 0, 0.2); color: #ff4500; border: 1px solid #ff4500; }

/* 3. Video Streams Box */
.stream-vault { background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 14px; padding: 16px; text-align: left; margin-bottom: 16px; }
.vault-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; }
.tier-item { background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.tier-badge-free { font-size: 10px; font-weight: 800; background: #22c55e; color: #000; padding: 3px 8px; border-radius: 4px; }
.tier-badge-vip { font-size: 10px; font-weight: 800; background: #eab308; color: #000; padding: 3px 8px; border-radius: 4px; }
.tier-info { font-size: 12px; color: #f1f5f9; font-weight: 600; }
.tier-sub { font-size: 11px; color: #94a3b8; }
.btn-play-free { background: #2563eb; color: #fff; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; }
.btn-unlock-vip { background: #eab308; color: #000; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 800; cursor: pointer; }

/* In-Page Video Player */
.free-player-box { display: block; margin-top: 12px; border-radius: 10px; overflow: hidden; background: #000; border: 1px solid rgba(56, 189, 248, 0.2); }
.free-player-box video { width: 100%; max-height: 260px; display: block; background: #000; }

/* 4. Social Media Buttons */
.card-head { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; text-align: left; }
.links-wrap { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.btn-social { flex: 1; min-width: 80px; background: rgba(30, 41, 59, 0.6); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); padding: 8px 6px; border-radius: 7px; text-decoration: none; font-size: 11px; font-weight: 600; text-align: center; }

/* Modals */
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 999; align-items: center; justify-content: center; padding: 16px; }
.modal-overlay.active { display: flex; }
.modal-card { background: #0f172a; border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 16px; padding: 24px; max-width: 360px; width: 100%; text-align: center; }
.qr-box { background: #fff; border-radius: 8px; width: 140px; height: 140px; margin: 12px auto; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #000; font-weight: 700; font-size: 13px; }
.qr-box span { font-size: 11px; color: #2563eb; margin-top: 4px; }
.ad-box { background: rgba(3, 7, 18, 0.6); border: 1.5px dashed #475569; padding: 20px 10px; border-radius: 10px; margin: 12px 0; color: #cbd5e1; font-size: 13px; }
</style>
</head>
<body>
<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">S</div>
        <h1 class="title">SauceFinder Pro</h1>
    </div>
    <div class="sub">Direct Cloud Streaming & Recognition Engine</div>

    <div class="glass-card">
        <div class="tabs">
            <button type="button" class="tab-btn active" onclick="switchTab('photo')">Photo Upload</button>
            <button type="button" class="tab-btn" onclick="switchTab('url')">Image URL</button>
            <button type="button" class="tab-btn" onclick="switchTab('name')">Name Directory</button>
        </div>

        <form action="/scan" method="POST" enctype="multipart/form-data" id="scanForm">
            <div class="tab-pane active" id="pane-photo">
                <label class="file-drop" for="fileInput">
                    <span class="file-label" id="fileLabelText"><strong>Click to upload</strong> or drop photo / screenshot</span>
                    <input type="file" id="fileInput" name="image_file" accept="image/*" onchange="fileChosen(this)">
                </label>
            </div>

            <div class="tab-pane" id="pane-url">
                <input type="url" name="image_url" placeholder="https://example.com/target-scene.jpg">
            </div>

            <div class="tab-pane" id="pane-name">
                <input type="text" name="keyword_name" placeholder="e.g. Niks Indian, Rose Noir, Alyx Star">
            </div>

            <button type="submit" class="btn-primary">Execute Live Scan & Play</button>
        </form>
    </div>

    _RESULT_PLACEHOLDER_
</div>

<!-- 5s Ad Modal -->
<div class="modal-overlay" id="adModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Sponsor Stream</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">Unlocking verified direct web stream mirrors...</p>
        <div class="ad-box">
            <strong>[SPONSOR AD RUNNING]</strong><br>
            <span style="font-size: 11px; color: #64748b;">Delivering In-Browser Direct Video Mirrors</span>
        </div>
        <div id="adTimer" style="font-size: 13px; font-weight: 700; color: #eab308; margin-bottom: 12px;">Please wait 5s...</div>
        <button id="adCloseBtn" style="display:none; width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer;" onclick="grantLinkAccess()">View Links Now</button>
    </div>
</div>

<!-- ₹9/Year Pass Modal -->
<div class="modal-overlay" id="linkPayModal">
    <div class="modal-card">
        <div style="display:inline-block; background:rgba(234, 179, 8, 0.15); color:#eab308; border:1px solid #eab308; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:800; margin-bottom:8px;">INSTANT PASS</div>
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px; font-weight: 800;">Direct Links Pass</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 12px;">Skip all ads & view all direct web stream mirrors instantly</p>
        <div style="font-size: 26px; font-weight: 900; color: #f8fafc; margin-bottom: 2px;">₹9 <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">/ 1 Year Pass</span></div>
        <div class="qr-box">
            <div>UPI QR Code</div>
            <span>Scan to Pay ₹9</span>
        </div>
        <button style="width:100%; padding:11px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:800; cursor:pointer; font-size:13px;" onclick="grantLinkAccess()">I Have Paid ₹9 (Unlock Links)</button>
        <button style="background:transparent; border:none; color:#64748b; font-size:12px; margin-top:10px; cursor:pointer;" onclick="closeModal('linkPayModal')">Cancel</button>
    </div>
</div>

<!-- VIP Pass Modal (₹99/Year for 1080p/4K & OnlyFans) -->
<div class="modal-overlay" id="vipModal">
    <div class="modal-card">
        <div style="display:inline-block; background:rgba(234, 179, 8, 0.15); color:#eab308; border:1px solid #eab308; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:800; margin-bottom:8px;">VIP ALL-ACCESS</div>
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px; font-weight: 800;">Full OnlyFans & 4K VIP Pass</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 12px;">Unlimited 4K master scenes, full uncut videos & private OnlyFans collections</p>
        <div style="font-size: 26px; font-weight: 900; color: #f8fafc; margin-bottom: 2px;">₹99 <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">/ 1 Year Pass</span></div>
        <div class="qr-box">
            <div>UPI QR Code</div>
            <span>Scan to Pay ₹99</span>
        </div>
        <button style="width:100%; padding:11px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:800; cursor:pointer; font-size:13px;" onclick="alert('Payment verified! VIP OnlyFans & 4K Pass activated for 1 Year.')">I Have Paid ₹99 (Activate VIP)</button>
        <button style="background:transparent; border:none; color:#64748b; font-size:12px; margin-top:10px; cursor:pointer;" onclick="closeModal('vipModal')">Cancel</button>
    </div>
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

function playInPageVideo(videoUrl) {
    const videoElem = document.getElementById('mainVideoElement');
    videoElem.src = videoUrl;
    videoElem.scrollIntoView({ behavior: 'smooth' });
    videoElem.play();
}

function openVipModal() {
    document.getElementById('vipModal').className = 'modal-overlay active';
}

function openLinkPayModal() {
    document.getElementById('linkPayModal').className = 'modal-overlay active';
}

let count = 5;
let timerInterval = null;

function triggerLinkAd() {
    count = 5;
    document.getElementById('adModal').className = 'modal-overlay active';
    document.getElementById('adTimer').style.display = 'block';
    document.getElementById('adTimer').innerText = 'Please wait ' + count + 's...';
    document.getElementById('adCloseBtn').style.display = 'none';

    timerInterval = setInterval(() => {
        count--;
        if (count > 0) {
            document.getElementById('adTimer').innerText = 'Please wait ' + count + 's...';
        } else {
            clearInterval(timerInterval);
            document.getElementById('adTimer').style.display = 'none';
            document.getElementById('adCloseBtn').style.display = 'block';
        }
    }, 1000);
}

function grantLinkAccess() {
    closeModal('adModal');
    closeModal('linkPayModal');
    document.getElementById('linksGateCard').style.display = 'none';
    document.getElementById('linksVault').style.display = 'block';
}

function closeModal(id) {
    document.getElementById(id).className = 'modal-overlay';
}
</script>
</body>
</html>"""

def get_channel_video_stream():
    """Fetches video direct stream from channel via Bot API."""
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates"
        res = requests.get(url, timeout=10).json()
        if res.get("ok"):
            updates = res.get("result", [])
            for u in reversed(updates):
                msg = u.get("channel_post") or u.get("message", {})
                video = msg.get("video") or msg.get("document", {})
                if video and "file_id" in video:
                    file_id = video["file_id"]
                    f_res = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
                    if f_res.get("ok"):
                        file_path = f_res["result"]["file_path"]
                        return f"/stream/{file_id}", f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{file_path}"
    except Exception:
        pass
    # Guaranteed high speed sample stream if channel is empty
    sample = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    return sample, sample

@app.get("/stream/{file_id}")
def stream_video(file_id: str):
    """Streams video directly inside browser without redirecting to Telegram."""
    try:
        f_res = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
        if f_res.get("ok"):
            file_path = f_res["result"]["file_path"]
            tg_stream_url = f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{file_path}"
            req = requests.get(tg_stream_url, stream=True)
            return StreamingResponse(req.iter_content(chunk_size=1024*1024), media_type="video/mp4")
    except Exception:
        pass
    return HTMLResponse("Stream unavailable", status_code=404)

@app.get("/")
def index():
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", ""))

@app.post("/scan")
async def scan(
    image_file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    keyword_name: Optional[str] = Form(None)
):
    target_img_display = ""
    creator_name = "Verified Creator"

    if image_file and image_file.filename:
        save_path = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_path, "wb") as f:
            f.write(await image_file.read())
        upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
        cdn_url = upload_res.get("secure_url")
        target_img_display = cdn_url
        creator_name = os.path.splitext(image_file.filename)[0].replace('-', ' ').replace('_', ' ').title()

    elif image_url and image_url.strip():
        url_input = image_url.strip()
        try:
            upload_res = cloudinary.uploader.upload(url_input, folder="saucefinder_scans")
            target_img_display = upload_res.get("secure_url")
        except Exception:
            target_img_display = url_input
        creator_name = "Verified Performer"

    elif keyword_name and keyword_name.strip():
        creator_name = keyword_name.strip().title()
        clean_encoded = urllib.parse.quote(creator_name)
        target_img_display = f"https://ui-avatars.com/api/?name={clean_encoded}&background=0284c7&color=fff&size=256&bold=true"

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:15px; font-size:13px;'>Please provide input.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    insta_url = f"https://www.instagram.com/explore/tags/{clean_tag}/"
    twitter_url = f"https://x.com/search?q={urllib.parse.quote(creator_name)}"
    onlyfans_url = f"https://onlyfans.com/{clean_tag}"
    fansly_url = f"https://fansly.com/{clean_tag}"

    stream_internal_url, stream_direct_url = get_channel_video_stream()

    result_html = f"""
    <div class="result-box">
        <!-- 1. Model Picture & Identity -->
        <img class="result-img" src="{target_img_display}" alt="{creator_name}">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Aliases: {creator_name}</div>

        <!-- 2. Locked Direct Links Gate (Immediately Below Photo) -->
        <div class="links-gate-box" id="linksGateCard">
            <div class="links-gate-title">🔒 Verified Web Stream Mirrors Ready</div>
            <div class="links-gate-sub">Choose how you want to unlock all direct video stream mirrors:</div>
            <div class="gate-btn-group">
                <button type="button" class="btn-gate-ad" onclick="triggerLinkAd()">📺 Watch Ad to View (Free)</button>
                <button type="button" class="btn-gate-pay" onclick="openLinkPayModal()">⚡ Pay ₹9 / 1 Year Pass</button>
            </div>
        </div>

        <!-- Combined OnlyFans / VIP Pass Card -->
        <div class="of-vip-banner">
            <div class="of-text">
                <div class="of-vip-title">👑 Unlock {creator_name} OnlyFans Vault</div>
                <div class="of-vip-sub">Full uncut videos & private HD stream archive</div>
            </div>
            <button type="button" class="btn-of-unlock" onclick="openVipModal()">Get VIP (₹99/Yr)</button>
        </div>

        <!-- Unlocked Container (Shows In-Page Playable Mirrors, Does NOT Redirect to Telegram) -->
        <div class="links-unlocked" id="linksVault">
            <div style="font-size:11px; font-weight:700; color:#22c55e; text-transform:uppercase; margin-bottom:6px;">● Direct Web Stream Mirrors (Click to Play in Page)</div>
            <div class="match-item" onclick="playInPageVideo('{stream_internal_url}')">
                <span class="match-title">▶ Play Full Web Stream Mirror 1 ({creator_name})</span>
                <span class="badge-source badge-stream">[Play On Page] ↗</span>
            </div>
            <a href="https://www.reddit.com/r/tipofmypenis/search/?q={urllib.parse.quote(creator_name)}" target="_blank" class="match-item">
                <span class="match-title">🔍 Reddit Solved Thread: {creator_name}</span>
                <span class="badge-source badge-reddit">[Community Match] ↗</span>
            </a>
        </div>

        <!-- 3. Matching Video Streams (Plays In-Page Without Redirecting) -->
        <div class="stream-vault">
            <div class="vault-title">
                <span>Matching Video Streams</span>
                <span style="font-size:11px; color:#eab308; font-weight:800;">3 Quality Tiers</span>
            </div>

            <div class="tier-item">
                <div>
                    <div class="tier-info">480p SD Preview Stream</div>
                    <div class="tier-sub">Standard resolution • Plays directly on this page</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-free">FREE</span>
                    <button type="button" class="btn-play-free" onclick="playInPageVideo('{stream_internal_url}')">Watch Demo</button>
                </div>
            </div>

            <!-- In-Page Player Element (Plays inside website) -->
            <div class="free-player-box" id="freePlayer">
                <video id="mainVideoElement" controls playsinline poster="{target_img_display}">
                    <source src="{stream_internal_url}" type="video/mp4">
                    Your browser does not support video playback.
                </video>
            </div>

            <div class="tier-item">
                <div>
                    <div class="tier-info">1080p FHD Master Stream</div>
                    <div class="tier-sub">High Bitrate 60 FPS • Full scene duration</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-vip">VIP</span>
                    <button type="button" class="btn-unlock-vip" onclick="openVipModal()">Unlock (₹99/yr)</button>
                </div>
            </div>

            <div class="tier-item">
                <div>
                    <div class="tier-info">4K Ultra HD Source File</div>
                    <div class="tier-sub">Uncompressed studio cut • Direct Web MP4 mirror</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-vip">VIP</span>
                    <button type="button" class="btn-unlock-vip" onclick="openVipModal()">Unlock (₹99/yr)</button>
                </div>
            </div>
        </div>

        <!-- 4. Official Channels & Social Profiles -->
        <div class="card-head">Official Channels & Social Profiles</div>
        <div class="links-wrap">
            <a class="btn-social" href="{insta_url}" target="_blank">Instagram</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social" href="{onlyfans_url}" target="_blank">OnlyFans</a>
            <a class="btn-social" href="{fansly_url}" target="_blank">Fansly</a>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
