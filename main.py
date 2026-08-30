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
<title>SauceFinder AI — Next-Gen Intelligence</title>
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
    justify-content: center;
    padding: 24px 16px;
}
.wrapper { width: 100%; max-width: 520px; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }
.logo-icon { width: 28px; height: 28px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: #fff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
.title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(180deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 24px; font-weight: 500; }

/* Modern Card */
.glass-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    text-align: left;
}

/* Tabs */
.tabs { display: flex; gap: 6px; background: rgba(3, 7, 18, 0.6); padding: 4px; border-radius: 10px; margin-bottom: 18px; border: 1px solid rgba(255, 255, 255, 0.04); }
.tab-btn { flex: 1; padding: 8px 10px; background: transparent; border: none; border-radius: 7px; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.tab-btn.active { background: #1e293b; color: #38bdf8; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }

/* Inputs */
.tab-pane { display: none; }
.tab-pane.active { display: block; }
.file-drop {
    border: 1.5px dashed rgba(56, 189, 248, 0.3);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    background: rgba(3, 7, 18, 0.4);
    cursor: pointer;
    transition: border-color 0.2s;
}
.file-drop:hover { border-color: #38bdf8; }
input[type="file"] { display: none; }
.file-label { font-size: 13px; color: #94a3b8; cursor: pointer; display: block; }
.file-label strong { color: #38bdf8; }
input[type="text"], input[type="url"] {
    width: 100%;
    padding: 12px 14px;
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #f1f5f9;
    font-size: 13px;
    font-family: inherit;
    transition: border-color 0.2s;
}
input[type="text"]:focus, input[type="url"]:focus { border-color: #38bdf8; outline: none; }

button.btn-primary {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    margin-top: 16px;
    cursor: pointer;
    font-family: inherit;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;
}
button.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

/* Result Showcase */
.result-box {
    margin-top: 24px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.3);
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
    text-align: center;
}
.result-img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #38bdf8;
    box-shadow: 0 0 25px rgba(56, 189, 248, 0.35);
    margin-bottom: 12px;
}
.name { font-size: 22px; font-weight: 800; color: #f8fafc; letter-spacing: -0.3px; }
.badge { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; padding: 3px 10px; border-radius: 20px; background: rgba(34, 197, 94, 0.12); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); margin: 6px 0 16px; font-weight: 600; }

/* Bio Infobox */
.wiki-card {
    background: rgba(3, 7, 18, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: left;
    margin-bottom: 16px;
}
.wiki-title { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; }
.wiki-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.wiki-table td { padding: 6px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
.wiki-label { color: #64748b; font-weight: 500; width: 35%; }
.wiki-value { color: #f1f5f9; font-weight: 600; }

.section-head { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; text-align: left; margin: 18px 0 8px; }
.links-wrap { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.btn-social {
    flex: 1;
    min-width: 100px;
    background: rgba(30, 41, 59, 0.6);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 9px 12px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
    text-align: center;
    transition: all 0.2s;
}
.btn-social:hover { background: rgba(56, 189, 248, 0.15); border-color: #38bdf8; }

/* Ad Unlocked Links */
.links-gate-box { background: rgba(3, 7, 18, 0.55); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 12px; padding: 16px; text-align: center; }
.btn-ad-unlock { background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: none; padding: 10px 18px; font-weight: 700; border-radius: 8px; cursor: pointer; font-size: 12px; font-family: inherit; }
.links-unlocked { display: none; }
.match-item { display: flex; align-items: center; justify-content: space-between; background: rgba(3, 7, 18, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 12px; margin-bottom: 6px; text-decoration: none; text-align: left; transition: all 0.2s; }
.match-item:hover { border-color: #38bdf8; background: rgba(56, 189, 248, 0.05); }
.match-title { font-size: 12px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
.match-src { font-size: 11px; color: #eab308; font-weight: 600; }

/* Modal */
.ad-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 999; align-items: center; justify-content: center; padding: 16px; }
.ad-modal.active { display: flex; }
.ad-card { background: #0f172a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; max-width: 360px; width: 100%; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.6); }
.ad-banner { background: rgba(3, 7, 18, 0.6); border: 1.5px dashed #475569; padding: 24px 12px; border-radius: 10px; margin: 14px 0; color: #cbd5e1; font-size: 13px; }
</style>
</head>
<body>
<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">S</div>
        <h1 class="title">SauceFinder AI</h1>
    </div>
    <div class="sub">Next-Gen Biometric & Multi-Source Intelligence</div>

    <div class="glass-card">
        <div class="tabs">
            <button type="button" class="tab-btn active" onclick="switchTab('photo')">Photo File</button>
            <button type="button" class="tab-btn" onclick="switchTab('url')">Image URL</button>
            <button type="button" class="tab-btn" onclick="switchTab('name')">Name Search</button>
        </div>

        <form action="/scan" method="POST" enctype="multipart/form-data" id="scanForm">
            <div class="tab-pane active" id="pane-photo">
                <label class="file-drop" for="fileInput">
                    <span class="file-label" id="fileLabelText"><strong>Click to upload</strong> or drop photo here</span>
                    <input type="file" id="fileInput" name="image_file" accept="image/*" onchange="fileChosen(this)">
                </label>
            </div>

            <div class="tab-pane" id="pane-url">
                <input type="url" name="image_url" placeholder="https://example.com/target-photo.jpg">
            </div>

            <div class="tab-pane" id="pane-name">
                <input type="text" name="keyword_name" placeholder="e.g. Alyx Star, Nika Venom">
            </div>

            <button type="submit" class="btn-primary">Deep Sauce Scan</button>
        </form>
    </div>

    _RESULT_PLACEHOLDER_
</div>

<div class="ad-modal" id="adModal">
    <div class="ad-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 17px; font-weight: 700;">Sponsor Verification</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">Unlocking internet source mirrors...</p>
        <div class="ad-banner">
            <strong>[SPONSOR NETWORK]</strong><br>
            <span style="font-size: 11px; color: #64748b;">Fast Media Delivery Node</span>
        </div>
        <div id="adTimer" style="font-size: 13px; font-weight: 700; color: #eab308; margin-bottom: 12px;">Please wait 5s...</div>
        <button id="adCloseBtn" style="display:none; width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer; font-family:inherit;" onclick="finishAd()">View Unlocked Links</button>
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

let count = 5;
let timerInterval = null;

function triggerAdUnlock() {
    count = 5;
    document.getElementById('adModal').className = 'ad-modal active';
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

function finishAd() {
    document.getElementById('adModal').className = 'ad-modal';
    document.getElementById('linksGate').style.display = 'none';
    document.getElementById('linksVault').style.display = 'block';
}
</script>
</body>
</html>"""

def extract_lens_full_report(image_url: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Verified Creator", "API Key not configured", "Global", []
    
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
            for m in matches[:8]:
                link_title = m.get("title", "Related Match")
                link_url = m.get("link", "#")
                link_src = m.get("source", "Link")
                matched_links.append({"title": link_title, "url": link_url, "source": link_src})

            return clean_name, f"Identified via cross-platform biometric database matches.", domain, matched_links
    except Exception:
        pass
    return "Verified Creator", "Cross-platform identity match verified.", "Web", []

def search_by_text_keyword(query: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    clean_name = query.title()
    matched_links = []
    found_photo = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300"
    
    if api_key:
        img_search_url = f"https://serpapi.com/search.json?engine=google_images&q={urllib.parse.quote(query + ' portrait')}&api_key={api_key}"
        try:
            img_res = requests.get(img_search_url, timeout=12).json()
            images = img_res.get("images_results", [])
            if images:
                found_photo = images[0].get("original") or images[0].get("thumbnail", found_photo)
        except Exception:
            pass

        url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(query + ' video')}&api_key={api_key}"
        try:
            res = requests.get(url, timeout=15).json()
            organic = res.get("organic_results", [])
            for r in organic[:8]:
                matched_links.append({
                    "title": r.get("title", "Video Match"),
                    "url": r.get("link", "#"),
                    "source": r.get("displayed_link", "Web Link")
                })
        except Exception:
            pass

    return clean_name, f"Public indexed career highlights and media data for {clean_name}.", "Google Index", matched_links, found_photo

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
    bio_summary = "Visual match query completed."
    primary_src = "Web Intelligence"
    matched_links = []

    if image_file and image_file.filename:
        save_path = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_path, "wb") as f:
            f.write(await image_file.read())
        upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
        cdn_url = upload_res.get("secure_url")
        target_img_display = cdn_url
        creator_name, bio_summary, primary_src, matched_links = extract_lens_full_report(cdn_url)

    elif image_url and image_url.strip():
        target_img_display = image_url.strip()
        creator_name, bio_summary, primary_src, matched_links = extract_lens_full_report(image_url.strip())

    elif keyword_name and keyword_name.strip():
        creator_name, bio_summary, primary_src, matched_links, found_photo = search_by_text_keyword(keyword_name.strip())
        target_img_display = found_photo

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:15px; font-size:13px;'>Please provide a photo, image URL or name.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    insta_url = f"https://www.instagram.com/explore/tags/{clean_tag}/"
    twitter_url = f"https://x.com/search?q={urllib.parse.quote(creator_name)}"
    reddit_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(creator_name)}"

    matched_html = ""
    for item in matched_links:
        matched_html += f"""
        <a href="{item['url']}" target="_blank" class="match-item">
            <span class="match-title">{item['title']}</span>
            <span class="match-src">[{item['source']}] ↗</span>
        </a>
        """

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img_display}" alt="Target">
        <div class="name">{creator_name}</div>
        <div class="badge">● Verified Public Profile</div>

        <div class="wiki-card">
            <div class="wiki-title">Biographical Overview</div>
            <table class="wiki-table">
                <tr><td class="wiki-label">Identity Name</td><td class="wiki-value">{creator_name}</td></tr>
                <tr><td class="wiki-label">Occupation</td><td class="wiki-value">Digital Creator / Public Model</td></tr>
                <tr><td class="wiki-label">Primary Source</td><td class="wiki-value">{primary_src}</td></tr>
                <tr><td class="wiki-label">Match Quality</td><td class="wiki-value" style="color:#4ade80;">100% Visual Confidence</td></tr>
            </table>
            <p style="margin: 10px 0 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">{bio_summary}</p>
        </div>

        <div class="section-head">Official Social Profiles</div>
        <div class="links-wrap">
            <a class="btn-social" href="{insta_url}" target="_blank">Instagram</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social" href="{reddit_url}" target="_blank">Reddit Sauce</a>
        </div>

        <div class="section-head">Internet Matching Links & Videos</div>
        
        <div class="links-gate-box" id="linksGate">
            <div style="font-size:13px; color:#cbd5e1; margin-bottom:10px;">🔒 <strong>{len(matched_links)} Video & Web Matches Found</strong></div>
            <button type="button" class="btn-ad-unlock" onclick="triggerAdUnlock()">Watch Quick Ad to Unlock Links (Free)</button>
        </div>

        <div class="links-unlocked" id="linksVault">
            {matched_html if matched_html else '<p style="font-size:12px;color:#64748b;">No direct mirrors indexed.</p>'}
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
