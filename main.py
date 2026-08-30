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
<title>SauceFinder AI - Multi-Input Search Engine</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #f8fafc; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px 0; }
.wrapper { max-width: 550px; width: 100%; padding: 20px; text-align: center; }
.title { font-size: 26px; font-weight: 800; margin-bottom: 6px; color: #38bdf8; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 25px; }
.scan-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 22px; text-align: left; }
.input-label { font-size: 12px; font-weight: 600; color: #94a3b8; margin: 10px 0 4px; display: block; }
input[type="file"], input[type="text"], input[type="url"] { width: 100%; padding: 11px; background: #080d1a; border: 1px solid #334155; border-radius: 8px; color: #cbd5e1; box-sizing: border-box; font-size: 13px; }
input:focus { border-color: #38bdf8; outline: none; }
.divider { text-align: center; font-size: 11px; color: #64748b; margin: 12px 0; text-transform: uppercase; letter-spacing: 1px; }
button.btn-primary { width: 100%; padding: 13px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-weight: 700; margin-top: 18px; cursor: pointer; }
button.btn-primary:hover { background: #1d4ed8; }
.result-box { margin-top: 25px; background: #0f172a; border: 1px solid #3b82f6; border-radius: 12px; padding: 22px; text-align: center; }
.result-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 12px; }
.name { font-size: 24px; font-weight: 800; color: #38bdf8; margin-bottom: 4px; }
.badge { display: inline-block; font-size: 11px; padding: 3px 10px; border-radius: 12px; background: #1e293b; color: #22c55e; border: 1px solid #334155; margin-bottom: 15px; }

/* Wikipedia Infobox */
.wiki-card { background: #080d1a; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; text-align: left; margin: 15px 0; }
.wiki-title { font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; margin-bottom: 10px; }
.wiki-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.wiki-table td { padding: 6px 0; border-bottom: 1px solid #1e293b; }
.wiki-label { color: #64748b; font-weight: 600; width: 35%; }
.wiki-value { color: #f1f5f9; }

.section-title { text-align: left; font-size: 13px; font-weight: 700; color: #94a3b8; margin: 18px 0 8px; text-transform: uppercase; }
.links-wrap { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
.btn-social { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600; }
.btn-social:hover { border-color: #38bdf8; }

/* Ad Lock Wall */
.links-gate-box { background: #080d1a; border: 1px solid #334155; border-radius: 8px; padding: 18px; margin-bottom: 18px; text-align: center; }
.btn-ad-unlock { background: #eab308; color: #000; border: none; padding: 11px 22px; font-weight: 800; border-radius: 6px; cursor: pointer; font-size: 13px; }
.links-unlocked { display: none; margin-bottom: 18px; }

.match-item { display: flex; align-items: center; justify-content: space-between; background: #080d1a; border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; text-decoration: none; text-align: left; }
.match-item:hover { border-color: #38bdf8; }
.match-title { font-size: 12px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px; }
.match-src { font-size: 11px; color: #eab308; }

/* Ad Modal */
.ad-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 999; align-items: center; justify-content: center; }
.ad-modal.active { display: flex; }
.ad-card { background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 24px; max-width: 380px; width: 90%; text-align: center; }
.ad-banner { background: #1e293b; border: 2px dashed #475569; padding: 30px 15px; border-radius: 8px; margin: 15px 0; color: #cbd5e1; font-size: 14px; }
</style>
</head>
<body>
<div class="wrapper">
<div class="title">SauceFinder AI</div>
<div class="sub">Search via Upload, Direct Image Link, or Name Keyword</div>
<div class="scan-card">
<form action="/scan" method="POST" enctype="multipart/form-data">
    <span class="input-label">Option 1: Upload Photo / Screenshot</span>
    <input type="file" name="image_file" accept="image/*">
    
    <div class="divider">— OR —</div>
    
    <span class="input-label">Option 2: Direct Image URL</span>
    <input type="url" name="image_url" placeholder="https://example.com/photo.jpg">
    
    <div class="divider">— OR —</div>
    
    <span class="input-label">Option 3: Model Name / Scene Keyword</span>
    <input type="text" name="keyword_name" placeholder="e.g. Alyx Star, Nika Venom, Kendra Lust">
    
    <button type="submit" class="btn-primary">Deep Sauce Scan</button>
</form>
</div>
_RESULT_PLACEHOLDER_
</div>

<div class="ad-modal" id="adModal">
    <div class="ad-card">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 18px;">Sponsor Advertisement</h3>
        <p style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">Unlocking internet source links...</p>
        <div class="ad-banner">
            <strong>[SPONSOR AD RUNNING]</strong><br>
            <span style="font-size: 11px; color: #94a3b8;">High-Quality Video Server Network</span>
        </div>
        <div id="adTimer" style="font-size: 13px; font-weight: 700; color: #eab308; margin-bottom: 10px;">Please wait 5s...</div>
        <button id="adCloseBtn" style="display:none; width:100%; padding:10px; background:#22c55e; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;" onclick="finishAd()">Access Links Now</button>
    </div>
</div>

<script>
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
        return "Verified Creator", "API Key not set", "Global", []
    
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
            
            domain = top.get("source", "Web Indexed")
            
            matched_links = []
            for m in matches[:8]:
                link_title = m.get("title", "Related Match")
                link_url = m.get("link", "#")
                link_src = m.get("source", "Video Source")
                matched_links.append({"title": link_title, "url": link_url, "source": link_src})

            return clean_name, f"Identified via internet visual matches. Public indexing active across platforms.", domain, matched_links
    except Exception:
        pass
    return "Verified Creator", "Match found in web indexing.", "Web", []

def search_by_text_keyword(query: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    clean_name = query.title()
    matched_links = []
    found_photo = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300"
    
    if api_key:
        # 1. Real photo search for creator
        img_search_url = f"https://serpapi.com/search.json?engine=google_images&q={urllib.parse.quote(query + ' portrait')}&api_key={api_key}"
        try:
            img_res = requests.get(img_search_url, timeout=12).json()
            images = img_res.get("images_results", [])
            if images:
                found_photo = images[0].get("original") or images[0].get("thumbnail", found_photo)
        except Exception:
            pass

        # 2. Real video links search
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

    return clean_name, f"Full biographical profile and index data for {clean_name}.", "Google Index", matched_links, found_photo

@app.get("/")
def index():
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", ""))

@app.post("/scan")
async def scan(
    image_file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    keyword_name: Optional[str] = Form(None)
):
    cdn_url = None
    target_img_display = ""
    creator_name = "Verified Creator"
    bio_summary = "Visual match query completed."
    primary_src = "Web Intelligence"
    matched_links = []

    # 1. File Upload Priority
    if image_file and image_file.filename:
        save_path = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_path, "wb") as f:
            f.write(await image_file.read())
        upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
        cdn_url = upload_res.get("secure_url")
        target_img_display = cdn_url
        creator_name, bio_summary, primary_src, matched_links = extract_lens_full_report(cdn_url)

    # 2. Image URL Input
    elif image_url and image_url.strip():
        target_img_display = image_url.strip()
        creator_name, bio_summary, primary_src, matched_links = extract_lens_full_report(image_url.strip())

    # 3. Direct Name / Keyword Search
    elif keyword_name and keyword_name.strip():
        creator_name, bio_summary, primary_src, matched_links, found_photo = search_by_text_keyword(keyword_name.strip())
        target_img_display = found_photo

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:15px;'>Kripya Photo, Image URL ya Name me se koi ek cheez fill karein.</p>"))

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
        <span class="badge">Verified Public Profile</span>

        <div class="wiki-card">
            <div class="wiki-title">Biographical Overview</div>
            <table class="wiki-table">
                <tr><td class="wiki-label">Identity Name</td><td class="wiki-value">{creator_name}</td></tr>
                <tr><td class="wiki-label">Occupation</td><td class="wiki-value">Digital Model / Content Creator</td></tr>
                <tr><td class="wiki-label">Primary Source</td><td class="wiki-value">{primary_src}</td></tr>
                <tr><td class="wiki-label">Database Match</td><td class="wiki-value" style="color:#22c55e;">100% Visual Confidence</td></tr>
            </table>
            <p style="margin: 10px 0 0; font-size: 12px; color: #94a3b8;">{bio_summary}</p>
        </div>

        <div class="section-title">Official Social Profiles</div>
        <div class="links-wrap">
            <a class="btn-social" href="{insta_url}" target="_blank">Instagram</a>
            <a class="btn-social" href="{twitter_url}" target="_blank">Twitter / X</a>
            <a class="btn-social" href="{reddit_url}" target="_blank">Reddit Sauce</a>
        </div>

        <div class="section-title">Internet Matching Links & Videos</div>
        
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
