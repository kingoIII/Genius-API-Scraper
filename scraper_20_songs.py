
#!/usr/bin/env python3
"""
Fetch lyrics for the top N songs (default 20) of each artist in ARTISTS.
Outputs JSONL rows: {"instruction": "...", "output": "..."}.
"""
import sys, os, json, re, time, unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GENIUS_TOKEN") or sys.exit("Missing GENIUS_TOKEN in env")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE_URL = "https://api.genius.com"

ARTISTS = [
    "Peso Pluma", "Billie Eilish", "Bad Bunny"
]
TOTAL_PER_ARTIST = 20  # change freely

def search_songs(artist, max_songs):
    out, page = [], 1
    while len(out) < max_songs and page <= 5:
        r = requests.get(f"{BASE_URL}/search",
                         params={"q": artist, "per_page": 20, "page": page},
                         headers=HEADERS)
        r.raise_for_status()
        hits = [h["result"] for h in r.json()["response"]["hits"] if h["type"] == "song"]
        out.extend(hits)
        page += 1
        time.sleep(0.6)
    seen, uniq = set(), []
    for s in out:
        if s["id"] not in seen:
            seen.add(s["id"]); uniq.append(s)
    return uniq[:max_songs]

def scrape_lyrics(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    parts = soup.select("div[data-lyrics-container='true']")
    text = "\n".join(p.get_text("\n") for p in parts)
    text = re.sub(r"\[.*?]", "", text)
    return unicodedata.normalize("NFKC", text).strip()

def main():
    out_path = Path("merged_lyrics_all.jsonl")
    with out_path.open("w", encoding="utf-8") as fout:
        for artist in ARTISTS:
            for song in tqdm(search_songs(artist, TOTAL_PER_ARTIST), desc=artist):
                try:
                    lyric = scrape_lyrics(song["url"])
                except Exception:
                    continue
                json.dump({"instruction": f"Write a full song in the style of {artist}",
                           "output": lyric}, fout, ensure_ascii=False)
                fout.write("\n")
    print(f"✅  Saved → {out_path}")

if __name__ == "__main__":
    main()
