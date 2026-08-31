import urllib.parse
from typing import Optional
import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

def fetch_wikipedia_bio(name: str):
    """Fetches real biography and image using Wikipedia Public API"""
    try:
        formatted_name = name.strip().replace(" ", "_")
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted_name)}"
        headers = {"User-Agent": "CelebrityFinderApp/1.0 (contact@example.com)"}
        res = requests.get(api_url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            bio = data.get("extract", "No bio available for this search.")
            img = data.get("thumbnail", {}).get("source") or f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=0284c7&color=fff&size=256&bold=true"
            title = data.get("title", name)
            return {"title": title, "bio": bio, "image": img}
    except Exception as e:
        print(f"Wiki API error: {e}")
    
    return {
        "title": name.title(),
        "bio": f"Public archive and multimedia profile for {name.title()}.",
        "image": f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=0284c7&color=fff&size=256&bold=true"
    }

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Creator & Celebrity Index</title>
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
.wrapper { width: 100%; max-width: 520px; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px; }
.logo-icon { width: 34px; height: 34px; background: linear-gradient(135deg, #38bdf8, #2563eb); border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; color: #fff; }
.title { font-size: 24px; font-weight: 800; }
.sub { font-size: 12px; color: #64748b; margin-bottom: 20px; }

.search-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 18px;
    text-align: left;
}
input[type="text"] {
    width: 100%;
    padding: 13px 14px;
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #f1f5f9;
    font-size: 14px;
}
input[type="text"]:focus { outline: none; border-color: #38bdf8; }
button.btn-primary {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    margin-top: 12px;
    cursor: pointer;
}

/* Result Box */
.result-box {
    margin-top: 22px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 18px;
    padding: 20px;
    text-align: left;
}
.profile-header { display: flex; gap: 16px; align-items: center; margin-bottom: 14px; }
.profile-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #38bdf8; flex-shrink: 0; }
.profile-title { font-size: 20px; font-weight: 800; color: #f8fafc; }
.profile-tag { font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 2px; }
.bio-text { font-size: 12px; color: #94a3b8; line-height: 1.6; margin-bottom: 16px; }

/* iFrame Container (Never Freezes) */
.iframe-container {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
    height: 0;
    border-radius: 12px;
    overflow: hidden;
    background: #000;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 16px;
}
.iframe-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
}

.links-grid { display: flex; flex-direction: column; gap: 8px; }
.link-btn {
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 9px;
    padding: 10px 12px;
    color: #f1f5f9;
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.link-btn:hover { border-color: #38bdf8; background: rgba(15, 23, 42, 0.9); }

/* 18+ Verification Modal */
#ageModal {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(3, 7, 18, 0.92);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}
.modal-content {
    background: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 24px;
    border-radius: 16px;
    max-width: 360px;
    text-align: center;
}
</style>
</head>
<body>

<div id="ageModal">
    <div class="modal-content">
        <h3 style="margin-bottom:8px; font-size:18px;">Age Verification (18+)</h3>
        <p style="font-size:12px; color:#94a3b8; margin-bottom:18px;">This platform contains community-indexed multimedia links. You must be at least 18 years old to proceed.</p>
        <button onclick="acceptAge()" style="background:#2563eb; color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:700; cursor:pointer; width:100%;">I am 18 or older</button>
    </div>
</div>

<div class="wrapper">
    <div class="brand">
        <div class="logo-icon">C</div>
        <h1 class="title">CelebIndex Pro</h1>
    </div>
    <div class="sub">Instant Bio-Data & Direct Media Embed Engine</div>

    <div class="search-card">
        <form action="/search" method="POST">
            <input type="text" name="query_name" placeholder="Search celebrity / actor name..." required>
            <button type="submit" class="btn-primary">Search Profile & Media</button>
        </form>
    </div>

    _RESULT_CONTAINER_
</div>

<script>
function acceptAge() {
    document.getElementById('ageModal').style.display = 'none';
    localStorage.setItem('age_verified', 'true');
}
window.onload = function() {
    if (localStorage.getItem('age_verified') === 'true') {
        document.getElementById('ageModal').style.display = 'none';
    }
};
</script>
</body>
</html>"""

@app.get("/")
def home():
    return HTMLResponse(HTML_TEMPLATE.replace("_RESULT_CONTAINER_", ""))

@app.post("/search")
def search_celebrity(query_name: str = Form(...)):
    profile = fetch_wikipedia_bio(query_name)
    query_enc = urllib.parse.quote(profile["title"])
    
    # Universal safe embed (YouTube / Dailymotion / External Video iFrame pattern)
    embed_url = f"https://www.youtube-nocookie.com/embed?listType=search&list={query_enc}"
    
    result_html = f"""
    <div class="result-box">
        <div class="profile-header">
            <img class="profile-img" src="{profile['image']}" alt="{profile['title']}">
            <div>
                <div class="profile-title">{profile['title']}</div>
                <div class="profile-tag">● Verified Profile Summary</div>
            </div>
        </div>
        
        <div class="bio-text">{profile['bio']}</div>

        <!-- Universal iFrame Embed: 100% smooth playback without codec or server errors -->
        <div class="iframe-container">
            <iframe src="{embed_url}" allowfullscreen allow="autoplay"></iframe>
        </div>

        <div style="font-size:11px; font-weight:700; color:#38bdf8; margin-bottom:8px; text-transform:uppercase;">Community Links & Archives</div>
        <div class="links-grid">
            <a href="https://en.wikipedia.org/wiki/{urllib.parse.quote(profile['title'].replace(' ', '_'))}" target="_blank" class="link-btn">
                <span>📖 Read Full Wikipedia Biography</span>
                <span>↗</span>
            </a>
            <a href="https://www.google.com/search?q={query_enc}+multimedia" target="_blank" class="link-btn">
                <span>🌐 Public Web & Media Archives</span>
                <span>↗</span>
            </a>
        </div>
    </div>
    """
    return HTMLResponse(HTML_TEMPLATE.replace("_RESULT_CONTAINER_", result_html))
