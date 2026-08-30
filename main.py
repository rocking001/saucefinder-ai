import os
import urllib.parse
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cloudinary
import cloudinary.uploader

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
<title>SauceFinder AI Engine</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #f8fafc; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.wrapper { max-width: 520px; width: 100%; padding: 20px; text-align: center; }
.title { font-size: 26px; font-weight: 800; margin-bottom: 6px; color: #38bdf8; }
.sub { font-size: 13px; color: #64748b; margin-bottom: 25px; }
.scan-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 22px; text-align: left; }
input[type="file"] { width: 100%; padding: 11px; background: #080d1a; border: 1px solid #334155; border-radius: 8px; color: #cbd5e1; }
button.btn-primary { width: 100%; padding: 13px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-weight: 700; margin-top: 15px; cursor: pointer; }
button.btn-primary:hover { background: #1d4ed8; }
.result-box { margin-top: 25px; background: #0f172a; border: 1px solid #3b82f6; border-radius: 12px; padding: 22px; }
.result-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 3px solid #3b82f6; margin-bottom: 12px; }
.action-box { background: #080d1a; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 16px 0; text-align: left; }
.btn-launch { display: block; width: 100%; padding: 12px; background: #0ea5e9; color: #fff; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; box-sizing: border-box; }
.btn-launch:hover { background: #0284c7; }
.video-box { margin-top: 20px; background: #000; border: 1px dashed #eab308; border-radius: 10px; overflow: hidden; height: 220px; position: relative; }
.video-elem { width: 100%; height: 100%; object-fit: cover; filter: blur(14px) brightness(0.4); }
.lock-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.6); }
.lock-btn { background: #eab308; color: #000; border: none; padding: 10px 20px; font-weight: 800; border-radius: 6px; cursor: pointer; }
</style>
</head>
<body>
<div class="wrapper">
<div class="title">SauceFinder AI</div>
<div class="sub">Zero-Limit Client Bridge Search</div>
<div class="scan-card">
<form action="/scan" method="POST" enctype="multipart/form-data">
<input type="file" name="image_file" required accept="image/*">
<button type="submit" class="btn-primary">Deep Sauce Scan</button>
</form>
</div>
_RESULT_PLACEHOLDER_
</div>
</body>
</html>"""

@app.get("/")
def index():
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", ""))

@app.post("/scan")
async def scan(image_file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, image_file.filename)
    with open(save_path, "wb") as f:
        f.write(await image_file.read())

    # Upload to Cloudinary for public reachable URL
    upload_res = cloudinary.uploader.upload(save_path, folder="saucefinder_scans")
    cdn_url = upload_res.get("secure_url")

    lens_url = f"https://lens.google.com/uploadbyurl?url={urllib.parse.quote(cdn_url)}"
    yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={urllib.parse.quote(cdn_url)}"

    result_html = f"""
    <div class="result-box">
        <img class="result-img" src="{cdn_url}" alt="Target">
        <h3 style="margin: 0; color: #38bdf8;">Visual Target Ready</h3>
        
        <div class="action-box">
            <span style="font-size: 13px; color: #94a3b8;">Click below to load matching creator data without server limits:</span>
            <a href="{lens_url}" target="_blank" class="btn-launch">Open Google Lens Match Window</a>
            <a href="{yandex_url}" target="_blank" class="btn-launch" style="background:#475569; margin-top:6px;">Open Yandex Face Match</a>
        </div>

        <div class="video-box">
            <video class="video-elem" autoplay loop muted playsinline>
                <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
            </video>
            <div class="lock-overlay">
                <div style="font-size: 13px; font-weight: 700; color: #fef08a; margin-bottom: 8px;">Full Video Sauce Stream</div>
                <button type="button" class="lock-btn" onclick="alert('Payment Demo Complete')">Unlock Full Video (₹49)</button>
            </div>
        </div>
    </div>
    """
    return HTMLResponse(HTML_LAYOUT.replace("_RESULT_PLACEHOLDER_", result_html))
