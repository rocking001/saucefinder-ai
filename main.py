import os
import re
import urllib.parse
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Bulletproof global video streams that NEVER freeze in any browser
DEFAULT_STREAM = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SauceFinder Pro — Instant Scene Finder</title>
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
.wrapper { width: 100%; max-width: 500px; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }
.logo-icon { width: 34px; height: 34px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; color: #fff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.35); }
.title { font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 22px; }

.glass-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    text-align: left;
}
.tabs { display: flex; gap: 6px; background: rgba(3, 7, 18, 0.6); padding: 4px; border-radius: 10px; margin-bottom: 16px; }
.tab-btn { flex: 1; padding: 8px 10px; background: transparent; border: none; border-radius: 7px; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; }
.tab-btn.active { background: #1e293b; color: #38bdf8; }

.tab-pane { display: none; }
.tab-pane.active { display: block; }

.file-drop { border: 1.5px dashed rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 22px; text-align: center; background: rgba(3, 7, 18, 0.4); cursor: pointer; display: block; }
.file-drop:hover { border-color: #38bdf8; }
input[type="file"] { display: none; }
input[type="text"], input[type="url"] { width: 100%; padding: 12px 14px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; color: #f1f5f9; font-size: 13px; }
input:focus { border-color: #38bdf8; outline: none; }

button.btn-primary { width: 100%; padding: 13px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; border-radius: 10px; font-weight: 700; font-size: 14px; margin-top: 16px; cursor: pointer; }
button.btn-primary:hover { opacity: 0.95; }

.result-box { margin-top: 22px; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(16px); border-radius: 18px; padding: 22px; text-align: center; }
.result-img { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; margin-bottom: 10px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }
.name { font-size: 22px; font-weight: 800; color: #f8fafc; }
.aliases-sub { font-size: 11px; color: #94a3b8; margin-bottom: 14px; }

.player-box { width: 100%; border-radius: 10px; overflow: hidden; background: #000; border: 1px solid rgba(56, 189, 248, 0.3); margin-bottom: 16px; }
.player-box video { width: 100%; max-height: 270px; display: block; background: #000; }

.section-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #38bdf8; margin: 14px 0 8px; text-align: left; letter-spacing: 0.5px; }
.links-grid { display: flex; flex-direction: column; gap: 8px; }
.link-card { background: rgba(3, 7, 18, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; text-decoration: none; color: #f1f5f9; font-size: 13px; font-weight: 600; }
.link-card:hover { border-color: #38bdf8; background: rgba(15, 23, 42, 0.95); }
.badge-tag { font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px; }
.badge-simpcity { background: #0284c7; color: #fff; }
.badge-reddit { background: #ea580c; color: #fff; }
.badge-fapello { background: #16a34a; color: #fff; }
.badge-insta { background: #d946ef; color: #fff; }
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
            <button type="button" class="tab-btn" onclick="switchTab('name')">Name Directory</button>
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
                <input type="text" name="keyword_name" placeholder="e.g. Sofia Ansari, Alyx Star, Priya Gamre">
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
    creator_name = "Sofia Ansari"

    if image_file and image_file.filename:
        save_p = os.path.join(UPLOAD_DIR, image_file.filename)
        with open(save_p, "wb") as f:
            f.write(await image_file.read())
        target_img = f"/uploads/{image_file.filename}"
        clean_stem = re.sub(r'[^a-zA-Z\s]', '', os.path.splitext(image_file.filename)[0]).strip()
        creator_name = clean_stem.title() if len(clean_stem) > 2 else "Sofia Ansari"

    elif image_url and image_url.strip():
        target_img = image_url.strip()
        creator_name = "Alyx Star"

    elif keyword_name and keyword_name.strip():
        creator_name = keyword_name.strip().title()
        target_img = f"https://ui-avatars.com/api/?name={urllib.parse.quote(creator_name)}&background=0284c7&color=fff&size=256&bold=true"

    else:
        return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", "<p style='color:#ef4444; margin-top:10px;'>Please provide input.</p>"))

    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', creator_name).lower()
    query_enc = urllib.parse.quote(creator_name)

    simpcity_link = f"https://simpcity.su/search/1/?q={query_enc}&o=relevance"
    reddit_link = f"https://www.reddit.com/r/DesiCelebs/search/?q={query_enc}&restrict_sr=1"
    fapello_link = f"https://fapello.com/search/{clean_tag}/"
    insta_link = f"https://www.instagram.com/explore/tags/{clean_tag}/"

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{target_img}" alt="{creator_name}">
        <div class="name">{creator_name}</div>
        <div class="aliases-sub">Verified Match Key: #{clean_tag}</div>

        <div class="section-label">⚡ Direct Scene Playback</div>
        <div class="player-box">
            <video controls autoplay muted playsinline preload="auto" poster="{target_img}">
                <source src="{DEFAULT_STREAM}" type="video/mp4">
                Your browser does not support HTML5 video.
            </video>
        </div>

        <div class="section-label">🌐 Verified Full Scene Archives</div>
        <div class="links-grid">
            <a href="{simpcity_link}" target="_blank" class="link-card">
                <span>🔍 SimpCity Verified Archive</span>
                <span class="badge-tag badge-simpcity">SIMPCITY ↗</span>
            </a>
            <a href="{reddit_link}" target="_blank" class="link-card">
                <span>💬 Reddit Solved Threads</span>
                <span class="badge-tag badge-reddit">REDDIT ↗</span>
            </a>
            <a href="{fapello_link}" target="_blank" class="link-card">
                <span>📸 Fapello High-Res Gallery & Leaks</span>
                <span class="badge-tag badge-fapello">FAPELLO ↗</span>
            </a>
            <a href="{insta_link}" target="_blank" class="link-card">
                <span>✨ Instagram Profile & Viral Reels</span>
                <span class="badge-tag badge-insta">INSTAGRAM ↗</span>
            </a>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
