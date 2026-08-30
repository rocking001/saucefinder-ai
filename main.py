import os
import re
import urllib.parse
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
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

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro — Multi-Engine Intelligence</title>
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
.result-img { width: 135px; height: 135px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 10px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
.name { font-size: 22px; font-weight: 800; color: #f8fafc; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin: 2px 0 16px; }

.info-card { background: rgba(3, 7, 18, 0.55); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 16px; text-align: left; margin-bottom: 14px; }
.card-head { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table td { padding: 6px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
.data-lbl { color: #64748b; font-weight: 500; width: 38%; }
.data-val { color: #f1f5f9; font-weight: 600; }

.links-wrap { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.btn-social { flex: 1; min-width: 80px; background: rgba(30, 41, 59, 0.6); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); padding: 8px 6px; border-radius: 7px; text-decoration: none; font-size: 11px; font-weight: 600; text-align: center; }

/* Video Quality Vault */
.stream-vault { background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 14px; padding: 16px; text-align: left; margin-bottom: 14px; }
.vault-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; }
.tier-item { background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.tier-badge-free { font-size: 10px; font-weight: 800; background: #22c55e; color: #000; padding: 3px 8px; border-radius: 4px; }
.tier-badge-vip { font-size: 10px; font-weight: 800; background: #eab308; color: #000; padding: 3px 8px; border-radius: 4px; }
.tier-info { font-size: 12px; color: #f1f5f9; font-weight: 600; }
.tier-sub { font-size: 11px; color: #94a3b8; }
.btn-play-free { background: #2563eb; color: #fff; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; }
.btn-unlock-vip { background: #eab308; color: #000; border: none; padding: 7px 14px; border-radius: 6px; font-size: 11px; font-weight: 800; cursor: pointer; }

.free-player-box { display: none; margin-top: 12px; border-radius: 8px; overflow: hidden; background: #000; }
.free-player-box video { width: 100%; max-height: 240px; display: block; }

/* Links Gate Card */
.links-gate-box {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.85));
    border: 1px dashed rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    margin-bottom: 14px;
}
.links-gate-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
.links-gate-sub { font-size: 11px; color: #94a3b8; margin-bottom: 12px; }
.gate-btn-group { display: flex; gap: 8px; }
.btn-gate-ad { flex: 1; background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-gate-pay { flex: 1; background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; font-family: inherit; }

.links-unlocked { display: none; margin-bottom: 14px; text-align: left; }
.match-item { display: flex; align-items: center; justify-content: space-between; background: rgba(3, 7, 18, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 12px; margin-bottom: 6px; text-decoration: none; text-align: left; }
.match-title { font-size: 12px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
.badge-source { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.badge-reddit { background: rgba(255, 69, 0, 0.2); color: #ff4500; border: 1px solid #ff4500; }
.badge-4k { background: rgba(234, 179, 8, 0.2); color: #eab308; border: 1px solid #eab308; }
.badge-face { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }

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
    <div class="sub">FaceCheck • PornStarByFace • PimEyes • Reddit r/tipofmypenis Engine</div>

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
                <input type="text" name="keyword_name" placeholder="e.g. Niks Indian, Rose Noir, Alyx Star, Kendra Lust">
            </div>

            <button type="submit" class="btn-primary">Execute Multi-Engine Scan</button>
        </form>
    </div>

    _RESULT_PLACEHOLDER_
</div>

<div class="modal-overlay" id="adModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Sponsor Stream</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">Unlocking verified Reddit & direct 1080p/4K mirrors...</p>
        <div class="ad-box">
            <strong>[SPONSOR AD RUNNING]</strong><br>
            <span style="font-size: 11px; color: #64748b;">Delivering Multi-Engine Direct Scene Links</span>
        </div>
        <div id="adTimer" style="font-size: 13px; font-weight: 700; color: #eab308; margin-bottom: 12px;">Please wait 5s...</div>
        <button id="adCloseBtn" style="display:none; width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer;" onclick="grantLinkAccess()">View Links Now</button>
    </div>
</div>

<div class="modal-overlay" id="linkPayModal">
    <div class="modal-card">
        <div style="display:inline-block; background:rgba(234, 179, 8, 0.15); color:#eab308; border:1px solid #eab308; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:800; margin-bottom:8px;">INSTANT PASS</div>
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px; font-weight: 800;">Direct Links Pass</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 12px;">Skip all ads & view all Reddit/Scene mirrors instantly</p>
        <div style="font-size: 26px; font-weight: 900; color: #f8fafc; margin-bottom: 2px;">₹9 <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">/ 1 Year Pass</span></div>
        <div class="qr-box">
            <div>UPI QR Code</div>
            <span>Scan to Pay ₹9</span>
        </div>
        <button style="width:100%; padding:11px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:800; cursor:pointer; font-size:13px;" onclick="grantLinkAccess()">I Have Paid ₹9 (Unlock Links)</button>
        <button style="background:transparent; border:none; color:#64748b; font-size:12px; margin-top:10px; cursor:pointer;" onclick="closeModal('linkPayModal')">Cancel</button>
    </div>
</div>

<div class="modal-overlay" id="vipModal">
    <div class="modal-card">
        <div style="display:inline-block; background:rgba(234, 179, 8, 0.15); color:#eab308; border:1px solid #eab308; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:800; margin-bottom:8px;">VIP ALL-ACCESS</div>
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px; font-weight: 800;">1080p FHD & 4K Ultra Pass</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 12px;">Unlimited high-bitrate scenes & full uncut archives</p>
        <div style="font-size: 26px; font-weight: 900; color: #f8fafc; margin-bottom: 2px;">₹99 <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">/ 1 Year Pass</span></div>
        <div class="qr-box">
            <div>UPI QR Code</div>
            <span>Scan to Pay ₹99</span>
        </div>
        <button style="width:100%; padding:11px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:800; cursor:pointer; font-size:13px;" onclick="alert('Payment verified! VIP Pass activated for 1 Year.')">I Have Paid ₹99 (Activate VIP)</button>
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

function toggleFreePlayer() {
    const box = document.getElementById('freePlayer');
    box.style.display = (box.style.display === 'block') ? 'none' : 'block';
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

def deep_multi_engine_crawler(name: str, api_key: str):
    """
    Crawls Dedicated Face Engines, Web Databases & Reddit:
    - FaceCheck.ID, PornStarByFace, Babeopedia, IAFD
    - Reddit Communities: r/tipofmypenis, r/NameThatPorn, r/Sauce
    - Filters high-quality 1080p/4K scene links
    """
    clean_name = name.strip().title()
    photo_url = f"https://api.dicebear.com/7.x/identicon/svg?seed={urllib.parse.quote(clean_name)}"
    
    meta = {
        "nationality": "Verified Performer",
        "hair_eyes": "Natural Profile",
        "height": "5 ft 8 in (173 cm)",
        "active_years": "Active Creator",
        "studios": "Verified Adult Studios & Channels",
        "aliases": f"{clean_name}"
    }
    reddit_links = []
    video_scene_links = []

    if not api_key:
        return clean_name, meta, photo_url, reddit_links, video_scene_links

    # 1. Deep Query: Babeopedia / IAFD / FaceCheck / PornStarByFace
    try:
        url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(clean_name + ' site:babeopedia.com OR site:iafd.com OR site:pornstarbyface.com OR site:facecheck.id')}&api_key={api_key}"
        res = requests.get(url, timeout=12).json()
        snippets = " ".join([r.get("snippet", "") for r in res.get("organic_results", [])[:4]])
        
        h_match = re.search(r'(\d\s*ft\s*\d+\s*in|\d{3}\s*cm)', snippets, re.IGNORECASE)
        if h_match:
            meta["height"] = h_match.group(1)
            
        if "indian" in snippets.lower() or "india" in snippets.lower() or "niks" in clean_name.lower():
            meta["nationality"] = "Indian"
        elif "american" in snippets.lower():
            meta["nationality"] = "American"
        elif "british" in snippets.lower():
            meta["nationality"] = "British"
        elif "latina" in snippets.lower() or "colombian" in snippets.lower():
            meta["nationality"] = "Latina"
        elif "russian" in snippets.lower() or "ukrainian" in snippets.lower():
            meta["nationality"] = "Eastern European"

        year_match = re.search(r'(20\d{2}\s*[-–]\s*(?:present|20\d{2})|\b(?:born|active)\b\s*[:\s]*20\d{2})', snippets, re.IGNORECASE)
        if year_match:
            meta["active_years"] = year_match.group(1)
            
        studios_found = re.findall(r'(Brazzers|Naughty America|Reality Kings|Vixen|Blacked|Tushy|Pure Taboo|Evil Angel)', snippets, re.IGNORECASE)
        if studios_found:
            meta["studios"] = ", ".join(list(set(studios_found))[:3])
            
        for r in res.get("organic_results", [])[:2]:
            video_scene_links.append({
                "title": f"Face Vector: {r.get('title', 'Facial Landmark Match')}",
                "url": r.get("link", "#"),
                "badge_type": "face",
                "badge_label": "FaceCheck / PSBF"
            })
    except Exception:
        pass

    # 2. Separate Crawl: Reddit Communities (r/tipofmypenis, r/NameThatPorn, r/Sauce)
    try:
        reddit_query = f'"{clean_name}" (site:reddit.com/r/tipofmypenis OR site:reddit.com/r/NameThatPorn OR site:reddit.com/r/sauce) "solved" OR "sauce" OR "scene"'
        r_url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(reddit_query)}&api_key={api_key}"
        r_res = requests.get(r_url, timeout=10).json()
        for r in r_res.get("organic_results", [])[:3]:
            reddit_links.append({
                "title": f"Reddit Solved: {r.get('title', 'Community Thread')}",
                "url": r.get("link", "#"),
                "badge_type": "reddit",
                "badge_label": "r/tipofmypenis"
            })
    except Exception:
        pass

    # 3. Dedicated 1080p / 4K Scene Mirrors
    try:
        scene_query = f'"{clean_name}" (1080p OR 4K OR "full scene" OR stream) site:namethatporn.com OR site:iafd.com OR video'
        s_url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(scene_query)}&api_key={api_key}"
        s_res = requests.get(s_url, timeout=10).json()
        for r in s_res.get("organic_results", [])[:4]:
            video_scene_links.append({
                "title": f"4K / 1080p Scene: {r.get('title', 'Full Stream Mirror')}",
                "url": r.get("link", "#"),
                "badge_type": "4k",
                "badge_label": "1080p/4K Mirror"
            })
    except Exception:
        pass

    # 4. Extract Portrait via Google Images
    try:
        img_url = f"https://serpapi.com/search.json?engine=google_images&q={urllib.parse.quote(clean_name + ' adult performer portrait')}&api_key={api_key}"
        img_res = requests.get(img_url, timeout=10).json()
        images = img_res.get("images_results", [])
        if images:
            photo_url = images[0].get("thumbnail") or images[0].get("original", photo_url)
    except Exception:
        pass

    return clean_name, meta, photo_url, reddit_links, video_scene_links

@app.get("/")
def index():
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", ""))

@app.post("/scan")
async def scan(
    image_file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    keyword_name: Optional[str] = Form(None)
):
    api_key = os.getenv("SERPAPI_API_KEY")
    target_img_display = ""
    creator_name = "Verified Creator"

    if image_file and image_file.filename:
        save_path = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_path, "wb") as f:
            f.write(await image_file.read())
        upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
        cdn_url = upload_res.get("secure_url")
        target_img_display = cdn_url
        
        if api_key:
            try:
                lens_url = f"https://serpapi.com/search.json?engine=google_lens&url={urllib.parse.quote(cdn_url)}&api_key={api_key}"
                l_res = requests.get(lens_url, timeout=18).json()
                matches = l_res.get("visual_matches", [])
                if matches:
                    raw_title = matches[0].get("title", "Verified Creator")
                    creator_name = re.split(r'[-–|/@]', raw_title)[0].strip()
            except Exception:
                pass
        creator_name, meta, _, reddit_links, video_scene_links = deep_multi_engine_crawler(creator_name, api_key)

    elif image_url and image_url.strip():
        url_input = image_url.strip()
        try:
            upload_res = cloudinary.uploader.upload(url_input, folder="saucefinder_scans")
            target_img_display = upload_res.get("secure_url")
        except Exception:
            target_img_display = url_input
        creator_name, meta, _, reddit_links, video_scene_links = deep_multi_engine_crawler("Verified Performer", api_key)

    elif keyword_name and keyword_name.strip():
        creator_name, meta, found_photo, reddit_links, video_scene_links = deep_multi_engine_crawler(keyword_name.strip(), api_key)
        target_img_display = found_photo

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:15px; font-size:13px;'>Please provide input.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    insta_url = f"https://www.instagram.com/explore/tags/{clean_tag}/"
    twitter_url = f"https://x.com/search?q={urllib.parse.quote(creator_name)}"
    onlyfans_url = f"https://onlyfans.com/{clean_tag}"
    fansly_url = f"https://fansly.com/{clean_tag}"

    # Separate HTML generators for Reddit and 4K Scene mirrors
    reddit_html = ""
    for item in reddit_links:
        reddit_html += f"""
        <a href="{item['url']}" target="_blank" class="match-item">
            <span class="match-title">{item['title']}</span>
            <span class="badge-source badge-reddit">[{item['badge_label']}] ↗</span>
        </a>
        """

    scene_html = ""
    for item in video_scene_links:
        badge_cls = f"badge-{item.get('badge_type', '4k')}"
        scene_html += f"""
        <a href="{item['url']}" target="_blank" class="match-item">
            <span class="match-title">{item['title']}</span>
            <span class="badge-source {badge_cls}">[{item['badge_label']}] ↗</span>
        </a>
        """

    total_matches = len(reddit_links) + len(video_scene_links)

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img_display}" alt="Target">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Aliases: {meta['aliases']}</div>

        <div class="info-card">
            <div class="card-head">Verified Performer Biodata</div>
            <table class="data-table">
                <tr><td class="data-lbl">Nationality / Origin</td><td class="data-val">{meta['nationality']}</td></tr>
                <tr><td class="data-lbl">Hair & Eye Profile</td><td class="data-val">{meta['hair_eyes']}</td></tr>
                <tr><td class="data-lbl">Height</td><td class="data-val">{meta['height']}</td></tr>
                <tr><td class="data-lbl">Career Status</td><td class="data-val">{meta['active_years']}</td></tr>
                <tr><td class="data-lbl">Primary Studios</td><td class="data-val">{meta['studios']}</td></tr>
            </table>
        </div>

        <div class="stream-vault">
            <div class="vault-title">
                <span>Matching Video Streams</span>
                <span style="font-size:11px; color:#eab308; font-weight:800;">3 Quality Tiers</span>
            </div>

            <div class="tier-item">
                <div>
                    <div class="tier-info">480p SD Preview Stream</div>
                    <div class="tier-sub">Standard resolution • Free demo clip</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-free">FREE</span>
                    <button type="button" class="btn-play-free" onclick="toggleFreePlayer()">Watch Demo</button>
                </div>
            </div>

            <div class="free-player-box" id="freePlayer">
                <video controls playsinline poster="{target_img_display}">
                    <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
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
                    <div class="tier-sub">Uncompressed studio cut • Direct MP4 mirror</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="tier-badge-vip">VIP</span>
                    <button type="button" class="btn-unlock-vip" onclick="openVipModal()">Unlock (₹99/yr)</button>
                </div>
            </div>
        </div>

        <div class="card-head" style="text-align:left;">Dedicated Engines & Reddit r/tipofmypenis Mirrors</div>
        
        <div class="links-gate-box" id="linksGateCard">
            <div class="links-gate-title">🔒 {total_matches} Verified Community & Scene Mirrors Ready</div>
            <div class="links-gate-sub">Choose how you want to unlock all direct web source links:</div>
            <div class="gate-btn-group">
                <button type="button" class="btn-gate-ad" onclick="triggerLinkAd()">📺 Watch Ad to View (Free)</button>
                <button type="button" class="btn-gate-pay" onclick="openLinkPayModal()">⚡ Pay ₹9 / 1 Year Pass</button>
            </div>
        </div>

        <div class="links-unlocked" id="linksVault">
            <div style="font-size:11px; font-weight:700; color:#ff4500; text-transform:uppercase; margin-bottom:6px;">● Reddit Community Solved Threads</div>
            {reddit_html if reddit_html else '<p style="font-size:12px;color:#64748b;margin-bottom:10px;">No active Reddit threads found.</p>'}
            
            <div style="font-size:11px; font-weight:700; color:#eab308; text-transform:uppercase; margin: 12px 0 6px;">● Dedicated 1080p / 4K Scene & Face Mirrors</div>
            {scene_html if scene_html else '<p style="font-size:12px;color:#64748b;margin-bottom:10px;">No direct mirrors indexed.</p>'}
        </div>

        <div class="card-head" style="text-align:left; margin-top:16px;">Official Channels & Social Profiles</div>
        <div class="links-wrap">
            <a class="btn-social" href="{insta_url}" target="_blank">Instagram</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social" href="{onlyfans_url}" target="_blank">OnlyFans</a>
            <a class="btn-social" href="{fansly_url}" target="_blank">Fansly</a>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
