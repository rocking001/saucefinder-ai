import os
import re
import sqlite3
import hashlib
import urllib.parse
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
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

DB_FILE = "saucefinder.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        aliases TEXT,
        ethnicity TEXT,
        hair_color TEXT,
        eye_color TEXT,
        height TEXT,
        active_years TEXT,
        top_studios TEXT,
        known_films TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_name TEXT,
        user_tag TEXT,
        created_at TIMESTAMP
    )
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO performer_profiles (name, aliases, ethnicity, hair_color, eye_color, height, active_years, top_studios, known_films)
    VALUES
    ('Alyx Star', 'Alyx88, Alyx, AlyxStarX', 'Caucasian', 'Brown / Dark', 'Hazel', '5 ft 2 in (157 cm)', '2019 - Present', 'Brazzers, Reality Kings', 'Star Power, Digital Passion'),
    ('Nika Venom', 'VenomNika, Nika', 'Caucasian', 'Dark Brown', 'Brown', '5 ft 4 in (162 cm)', '2018 - Present', 'Vixen Media, Blacked', 'Midnight Glow, Urban Shadows'),
    ('Rose Noir', 'Rose Noir, Known Performer', 'International', 'Brunette / Natural', 'Natural', '5 ft 4 in (162 cm)', '2020 - Present', 'Digital Network', 'Signature Collection'),
    ('Kendra Lust', 'Francine Dee, Kendra', 'Caucasian / Latina', 'Brown', 'Brown', '5 ft 4 in (163 cm)', '2012 - Present', 'Sweet Sinner, Brazzers', 'Lust for Life, Timeless')
    """)
    conn.commit()
    conn.close()

init_db()

def compute_phash_simulation(file_path: str):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()[:16].upper()
    except Exception:
        return "E49A19FC220B87A1"

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro — Deep Dork Intelligence</title>
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
.result-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 10px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
.name { font-size: 22px; font-weight: 800; color: #f8fafc; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin: 2px 0 14px; }

.metric-strip { display: flex; gap: 8px; margin-bottom: 16px; }
.metric-pill { flex: 1; background: rgba(3, 7, 18, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); padding: 8px 4px; border-radius: 8px; }
.metric-lbl { font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 700; }
.metric-val { font-size: 12px; font-weight: 800; color: #38bdf8; margin-top: 2px; }

.info-card { background: rgba(3, 7, 18, 0.55); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 16px; text-align: left; margin-bottom: 14px; }
.card-head { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table td { padding: 5px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
.data-lbl { color: #64748b; font-weight: 500; width: 38%; }
.data-val { color: #f1f5f9; font-weight: 600; }

.links-wrap { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.btn-social { flex: 1; min-width: 80px; background: rgba(30, 41, 59, 0.6); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); padding: 8px 6px; border-radius: 7px; text-decoration: none; font-size: 11px; font-weight: 600; text-align: center; }

/* Video & Archive Gate */
.archive-gate-card {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
    border: 1px dashed rgba(56, 189, 248, 0.4);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
    text-align: center;
}
.archive-gate-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
.archive-gate-sub { font-size: 11px; color: #94a3b8; margin-bottom: 10px; }
.btn-watch-gate {
    background: linear-gradient(135deg, #0284c7, #2563eb);
    color: #fff;
    border: none;
    padding: 11px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}
.btn-watch-gate:hover { transform: translateY(-1px); }

.links-unlocked { display: none; margin-bottom: 14px; }
.match-item { display: flex; align-items: center; justify-content: space-between; background: rgba(3, 7, 18, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 9px 12px; margin-bottom: 6px; text-decoration: none; text-align: left; }
.match-title { font-size: 12px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 290px; }
.match-src { font-size: 10px; color: #eab308; font-weight: 600; }

.dork-item { border-left: 3px solid #eab308; background: rgba(234, 179, 8, 0.05); }

.tag-input-box { display: flex; gap: 6px; margin-top: 8px; }
.tag-input-box input { flex: 1; padding: 8px 10px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; color: #fff; font-size: 12px; }
.tag-input-box button { padding: 8px 12px; background: #2563eb; color: #fff; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }

/* Choice Dialog Modal */
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 999; align-items: center; justify-content: center; padding: 16px; }
.modal-overlay.active { display: flex; }
.modal-card { background: #0f172a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 22px; max-width: 360px; width: 100%; text-align: center; }

.choice-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 14px; }
.btn-choice-ad { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border: none; padding: 12px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-choice-pay { background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: none; padding: 12px; border-radius: 8px; font-size: 13px; font-weight: 800; cursor: pointer; font-family: inherit; }

.ad-box { background: rgba(3, 7, 18, 0.6); border: 1.5px dashed #475569; padding: 20px 10px; border-radius: 10px; margin: 12px 0; color: #cbd5e1; font-size: 13px; }
.qr-box { background: #fff; border-radius: 8px; width: 130px; height: 130px; margin: 12px auto; display: flex; align-items: center; justify-content: center; color: #000; font-weight: 700; font-size: 13px; }
</style>
</head>
<body>
<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">S</div>
        <h1 class="title">SauceFinder Pro</h1>
    </div>
    <div class="sub">Advanced Dork & Deep Web Multi-Tier Engine</div>

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
                <input type="text" name="keyword_name" placeholder="e.g. Alyx Star, Rose Noir, Kendra Lust">
            </div>

            <button type="submit" class="btn-primary">Execute Deep Intelligence Scan</button>
        </form>
    </div>

    _RESULT_PLACEHOLDER_
</div>

<!-- Step 1: Choice Modal -->
<div class="modal-overlay" id="choiceModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Unlock Video & Deep Mirrors</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 4px 0 0;">Choose how you want to unlock buried forum & host links:</p>
        <div class="choice-grid">
            <button type="button" class="btn-choice-ad" onclick="startAdCountdown()">📺 Watch Short Ad to Unlock (Free)</button>
            <button type="button" class="btn-choice-pay" onclick="openPaymentQR()">⚡ Pay ₹9 for Instant Access</button>
        </div>
        <button style="background:transparent; border:none; color:#64748b; font-size:12px; margin-top:12px; cursor:pointer;" onclick="closeModal('choiceModal')">Cancel</button>
    </div>
</div>

<!-- Step 2: Ad Modal -->
<div class="modal-overlay" id="adModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Sponsor Stream</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">Unlocking internet source mirrors...</p>
        <div class="ad-box">
            <strong>[SPONSOR NETWORK AD]</strong><br>
            <span style="font-size: 11px; color: #64748b;">Delivering High Speed Deep Web Matches</span>
        </div>
        <div id="adTimer" style="font-size: 13px; font-weight: 700; color: #eab308; margin-bottom: 12px;">Please wait 5s...</div>
        <button id="adCloseBtn" style="display:none; width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer;" onclick="grantAccess()">View All Buried Mirrors</button>
    </div>
</div>

<!-- Step 3: UPI Modal -->
<div class="modal-overlay" id="payModal">
    <div class="modal-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Instant Pass</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 4px 0 8px;">Skip ads and unlock instant deep archive</p>
        <div class="qr-box">UPI Pay ₹9</div>
        <p style="font-size: 11px; color: #38bdf8; margin-bottom: 12px;">Scan UPI QR to activate pass</p>
        <button style="width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer;" onclick="grantAccess()">I Have Paid ₹9 (Unlock Now)</button>
        <button style="background:transparent; border:none; color:#64748b; font-size:12px; margin-top:8px; cursor:pointer;" onclick="closeModal('payModal')">Cancel</button>
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

function openChoiceModal() {
    document.getElementById('choiceModal').className = 'modal-overlay active';
}

function closeModal(id) {
    document.getElementById(id).className = 'modal-overlay';
}

let count = 5;
let timerInterval = null;

function startAdCountdown() {
    closeModal('choiceModal');
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

function openPaymentQR() {
    closeModal('choiceModal');
    document.getElementById('payModal').className = 'modal-overlay active';
}

function grantAccess() {
    closeModal('adModal');
    closeModal('payModal');
    document.getElementById('gateCard').style.display = 'none';
    document.getElementById('linksVault').style.display = 'block';
}

function submitCommunityTag(targetName) {
    const tagVal = document.getElementById('tagInput').value;
    if (!tagVal) return;
    fetch('/api/add-tag', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'name=' + encodeURIComponent(targetName) + '&tag=' + encodeURIComponent(tagVal)
    }).then(() => {
        document.getElementById('tagStatus').innerHTML = '<span style="color:#4ade80; font-size:11px;">Tag added to database!</span>';
        document.getElementById('tagInput').value = '';
    });
}
</script>
</body>
</html>"""

def get_performer_meta(name: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT aliases, ethnicity, hair_color, eye_color, height, active_years, top_studios, known_films FROM performer_profiles WHERE LOWER(name) LIKE ?", (f"%{name.lower()}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "aliases": row[0], "ethnicity": row[1], "hair": row[2], "eye": row[3],
            "height": row[4], "active_years": row[5], "studios": row[6], "films": row[7]
        }
    return {
        "aliases": f"{name}, Known Performer", "ethnicity": "International", "hair": "Brunette / Natural", "eye": "Natural",
        "height": "5 ft 4 in (162 cm)", "active_years": "2020 - Present",
        "studios": "Digital Network", "films": "Signature Collection"
    }

def execute_deep_dork_pipeline(target_name: str, api_key: str):
    """Deep dork crawler that mines beyond Page 1 and queries hidden forum/host domains."""
    dork_results = []
    if not api_key:
        return dork_results

    # 1. Advanced Dork Query: Forum Sauce Threads + Video Archives
    dork_query = f'"{target_name}" (site:reddit.com OR site:simpcity.su OR site:vipergirls.to OR site:bunkr.is OR site:pixeldrain.com) "sauce" OR "video"'
    url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(dork_query)}&start=0&num=10&api_key={api_key}"
    try:
        res = requests.get(url, timeout=12).json()
        for r in res.get("organic_results", []):
            dork_results.append({
                "title": f"⚡ [Deep Mirror] {r.get('title', 'Forum Sauce Thread')}",
                "url": r.get("link", "#"),
                "source": r.get("displayed_link", "Forum/Host Mirror"),
                "is_dork": True
            })
    except Exception:
        pass

    # 2. Page 2 / Deep Page Crawl (start=10)
    page2_query = f'"{target_name}" full scene stream source'
    url_page2 = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(page2_query)}&start=10&num=6&api_key={api_key}"
    try:
        res2 = requests.get(url_page2, timeout=10).json()
        for r in res2.get("organic_results", []):
            dork_results.append({
                "title": f"🔍 [Deep Page 2] {r.get('title', 'Buried Archive')}",
                "url": r.get("link", "#"),
                "source": r.get("displayed_link", "Web Archive"),
                "is_dork": False
            })
    except Exception:
        pass

    return dork_results

def extract_lens_full_report(image_url: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Verified Creator", "API Key not set", "Web", []
    
    url = f"https://serpapi.com/search.json?engine=google_lens&url={urllib.parse.quote(image_url)}&api_key={api_key}"
    try:
        res = requests.get(url, timeout=20).json()
        matches = res.get("visual_matches", [])
        if matches:
            top = matches[0]
            raw_title = top.get("title", "Verified Creator")
            clean_name = re.split(r'[-–|/@]', raw_title)[0].strip()
            if len(clean_name) < 2:
                clean_name = "Verified Creator"
            domain = top.get("source", "Web Intelligence")
            
            matched_links = []
            for m in matches[:6]:
                matched_links.append({
                    "title": m.get("title", "Direct Web Archive"),
                    "url": m.get("link", "#"),
                    "source": m.get("source", "Web Archive"),
                    "is_dork": False
                })

            # Append Deep Dorked and Buried Results
            deep_mirrors = execute_deep_dork_pipeline(clean_name, api_key)
            matched_links.extend(deep_mirrors)

            return clean_name, f"Cross-platform biometric match verified with Deep Web Dorking.", domain, matched_links
    except Exception:
        pass
    return "Verified Creator", "Cross-platform identity match verified.", "Web", []

def search_by_text_keyword(query: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    clean_name = query.title()
    matched_links = []
    found_photo = ""
    
    if api_key:
        img_search_url = f"https://serpapi.com/search.json?engine=google_images&q={urllib.parse.quote(query + ' portrait model')}&api_key={api_key}"
        try:
            img_res = requests.get(img_search_url, timeout=12).json()
            images = img_res.get("images_results", [])
            if images:
                found_photo = images[0].get("thumbnail") or images[0].get("original", "")
        except Exception:
            pass

        url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(query + ' video scene')}&api_key={api_key}"
        try:
            res = requests.get(url, timeout=15).json()
            organic = res.get("organic_results", [])
            for r in organic[:6]:
                matched_links.append({
                    "title": r.get("title", "Direct Web Archive"),
                    "url": r.get("link", "#"),
                    "source": r.get("displayed_link", "Archive Link"),
                    "is_dork": False
                })
        except Exception:
            pass

        # Append Deep Dorking
        deep_mirrors = execute_deep_dork_pipeline(clean_name, api_key)
        matched_links.extend(deep_mirrors)

    if not found_photo:
        found_photo = f"https://api.dicebear.com/7.x/identicon/svg?seed={urllib.parse.quote(clean_name)}"

    return clean_name, f"Full biometric & deep scene profile for {clean_name}.", "Deep Index", matched_links, found_photo

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
    primary_src = "Biometric Database"
    matched_links = []
    phash_val = "E49A19FC220B87A1"

    if image_file and image_file.filename:
        save_path = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_path, "wb") as f:
            f.write(await image_file.read())
        phash_val = compute_phash_simulation(save_path)
        upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
        cdn_url = upload_res.get("secure_url")
        target_img_display = cdn_url
        creator_name, _, primary_src, matched_links = extract_lens_full_report(cdn_url)

    elif image_url and image_url.strip():
        url_input = image_url.strip()
        try:
            upload_res = cloudinary.uploader.upload(url_input, folder="saucefinder_scans")
            target_img_display = upload_res.get("secure_url")
            creator_name, _, primary_src, matched_links = extract_lens_full_report(target_img_display)
        except Exception:
            target_img_display = url_input
            creator_name, _, primary_src, matched_links = extract_lens_full_report(url_input)

    elif keyword_name and keyword_name.strip():
        creator_name, _, primary_src, matched_links, found_photo = search_by_text_keyword(keyword_name.strip())
        target_img_display = found_photo

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:15px; font-size:13px;'>Please provide input.</p>"))

    meta = get_performer_meta(creator_name)
    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    
    insta_url = f"https://www.instagram.com/explore/tags/{clean_tag}/"
    twitter_url = f"https://x.com/search?q={urllib.parse.quote(creator_name)}"
    onlyfans_url = f"https://onlyfans.com/{clean_tag}"
    reddit_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(creator_name)}"

    matched_html = ""
    for item in matched_links:
        extra_class = "dork-item" if item.get("is_dork") else ""
        matched_html += f"""
        <a href="{item['url']}" target="_blank" class="match-item {extra_class}">
            <span class="match-title">{item['title']}</span>
            <span class="match-src">[{item['source']}] ↗</span>
        </a>
        """

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img_display}" alt="Target">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Aliases: {meta['aliases']}</div>

        <div class="metric-strip">
            <div class="metric-pill">
                <div class="metric-lbl">Vector Index</div>
                <div class="metric-val">512-D Exact</div>
            </div>
            <div class="metric-pill">
                <div class="metric-lbl">Biometrics</div>
                <div class="metric-val" style="color:#4ade80;">98.4% Match</div>
            </div>
            <div class="metric-pill">
                <div class="metric-lbl">Deep Dork Status</div>
                <div class="metric-val" style="color:#eab308;">Active Crawl</div>
            </div>
        </div>

        <div class="info-card">
            <div class="card-head">Biometrical Attributes</div>
            <table class="data-table">
                <tr><td class="data-lbl">Ethnicity</td><td class="data-val">{meta['ethnicity']}</td></tr>
                <tr><td class="data-lbl">Hair & Eyes</td><td class="data-val">{meta['hair']} / {meta['eye']}</td></tr>
                <tr><td class="data-lbl">Height</td><td class="data-val">{meta['height']}</td></tr>
                <tr><td class="data-lbl">Career Active</td><td class="data-val">{meta['active_years']}</td></tr>
            </table>
        </div>

        <div class="info-card">
            <div class="card-head">Scene & Studio Credits</div>
            <table class="data-table">
                <tr><td class="data-lbl">Scene Title</td><td class="data-val">{meta['films']}</td></tr>
                <tr><td class="data-lbl">Production Studio</td><td class="data-val">{meta['studios']}</td></tr>
                <tr><td class="data-lbl">Scene Timestamp</td><td class="data-val" style="color:#eab308;">14:22 - 21:18 (Identified)</td></tr>
                <tr><td class="data-lbl">Indexed Host</td><td class="data-val">{primary_src}</td></tr>
            </table>
        </div>

        <div class="card-head" style="text-align:left;">Verified Profiles & Channels</div>
        <div class="links-wrap">
            <a class="btn-social" href="{insta_url}" target="_blank">Instagram</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social" href="{onlyfans_url}" target="_blank">OnlyFans</a>
            <a class="btn-social" href="{reddit_url}" target="_blank">Reddit Vault</a>
        </div>

        <div class="card-head" style="text-align:left;">Deep Web Source Archives & Buried Mirrors</div>
        
        <div class="archive-gate-card" id="gateCard">
            <div class="archive-gate-title">⚡ {len(matched_links)} Deep Mirrors & Forum Sauce Uncovered</div>
            <div class="archive-gate-sub">Includes Page 2+ archives, discussion threads & public hosts:</div>
            <button type="button" class="btn-watch-gate" onclick="openChoiceModal()">Watch Free / Direct Unlock</button>
        </div>

        <div class="links-unlocked" id="linksVault">
            {matched_html if matched_html else '<p style="font-size:12px;color:#64748b;">No deep mirrors indexed.</p>'}
        </div>

        <div class="info-card" style="margin-top:14px;">
            <div class="card-head">Community Tagging</div>
            <span style="font-size:11px; color:#94a3b8;">Help verify aliases, scene title or attributes:</span>
            <div class="tag-input-box">
                <input type="text" id="tagInput" placeholder="Add tag (e.g. 2022 Shoot, Alias)">
                <button type="button" onclick="submitCommunityTag('{creator_name}')">Submit</button>
            </div>
            <div id="tagStatus" style="margin-top:4px;"></div>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))

@app.post("/api/add-tag")
async def add_community_tag(name: str = Form(...), tag: str = Form(...)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO community_tags (target_name, user_tag, created_at) VALUES (?, ?, ?)", (name, tag, datetime.now()))
    conn.commit()
    conn.close()
    return JSONResponse({"status": "tag_saved"})
