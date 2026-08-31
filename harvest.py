import os
import re
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

DATA_FILE = "video_registry.json"
DEFAULT_STREAM = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Current database load karein
db = {}
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception:
        db = {}

# Indian Desi communities
subreddits = ["DesiCelebs", "IndianBabes", "IndianInstaSobhitas"]
discovered_models = set()

print("[ACTIONS HARVESTER] Crawling Desi Subreddits...")
for sub in subreddits:
    try:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            posts = r.json().get("data", {}).get("children", [])
            for p in posts:
                title = p.get("data", {}).get("title", "")
                clean = re.split(r'[\[\(\-\|\:]', title)[0].strip()
                words = clean.split()
                if 1 <= len(words) <= 3 and words[0].lower() not in ["the", "my", "desi", "indian", "viral", "hot", "anyone", "link"]:
                    discovered_models.add(clean.title())
    except Exception as e:
        print(f"Error fetching {sub}: {e}")

print(f"[ACTIONS HARVESTER] Found {len(discovered_models)} candidate creators.")

# Stream trailer extraction
new_added = 0
for name in discovered_models:
    clean_tag = re.sub(r'[^a-zA-Z0-9]', '', name.lower()).strip()
    if clean_tag and (clean_tag not in db or db[clean_tag] == DEFAULT_STREAM):
        stream_link = DEFAULT_STREAM
        try:
            query = f"{name} official scene trailer video stream mp4"
            q_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            res = requests.get(q_url, headers=HEADERS, timeout=6)
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(ext in href.lower() for ext in [".mp4", "preview", "stream"]):
                    stream_link = href
                    break
        except Exception:
            pass

        db[clean_tag] = stream_link
        new_added += 1
        print(f"Added: {name} (#{clean_tag})")

# Save back to database
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2)

print(f"[ACTIONS HARVESTER COMPLETE] {new_added} new creators saved to {DATA_FILE}")
