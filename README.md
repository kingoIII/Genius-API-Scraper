# Genius Lyrics Scraper

Grab clean Genius lyrics in bulk—ideal for AI training, text analysis, or personal archiving.  
The repo ships with two standalone Python scripts:

| Script | Purpose | Default songs / artist |
|--------|---------|------------------------|
| `scraper_20_songs.py` | Fast sampler of top tracks | **20** |
| `scraper_120_songs.py` | Deep-dive harvest | **120** |

---

## ⚡️ Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Scripts & Usage](#scripts--usage)  
   4.1 [Scraper (20 songs)](#scraper_20_songs)  
   4.2 [Scraper (120 songs)](#scraper_120_songs)  
5. [Customising Artists & Song Counts](#customising-artists--song-counts)
6. [Output Format](#output-format)
7. [Contributing](#contributing)
8. [Licence](#licence)

---

## Quick Start
```bash
# clone + enter repo
git clone https://github.com/your-user/Genius-Lyrics-Scraper.git
cd Genius-Lyrics-Scraper

# set up deps
python3 -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

# add your Genius token
echo "GENIUS_TOKEN=xxxxxxxxxxxxxxxx" > .env

# run a scrape (20 songs per artist)
python scraper_20_songs.py
````

---

## Installation

1. **Python 3.7+** – [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. *(Optional but recommended)* create a virtualenv.
3. `pip install -r requirements.txt`.

Dependencies:

```
requests
beautifulsoup4
tqdm
python-dotenv
```

---

## Configuration

Create `.env` in the repo root:

```env
GENIUS_TOKEN=your_genius_api_token_here
```

Get an API token at [https://genius.com/developers](https://genius.com/developers) → *Create an App*.

---

## Scripts & Usage

### <a id="scraper_20_songs"></a>scraper\_20\_songs.py – Top 20 Sampler

```python
#!/usr/bin/env python3
"""
Fetch lyrics for the top N songs (default 20) of each artist in ARTISTS.
Outputs JSONL rows: {"instruction": "...", "output": "..."}.
"""

import json, os, re, time, unicodedata
from pathlib import Path
import requests, dotenv, bs4, tqdm

dotenv.load_dotenv()
TOKEN = os.getenv("GENIUS_TOKEN") or sys.exit("Missing GENIUS_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE   = "https://api.genius.com"

ARTISTS = ["Peso Pluma", "Billie Eilish", "Bad Bunny"]   # edit freely
TOTAL_PER_ARTIST = 20                                    # change here

def search(artist, n):
    out, page = [], 1
    while len(out) < n and page <= 5:
        r = requests.get(f"{BASE}/search",
                         params={"q": artist, "per_page": 20, "page": page},
                         headers=HEADERS).json()["response"]["hits"]
        out += [h["result"] for h in r if h["type"] == "song"]
        page += 1; time.sleep(0.6)
    # dedupe + trim
    seen, uniq = set(), []
    for s in out:
        if s["id"] not in seen:
            seen.add(s["id"]); uniq.append(s)
    return uniq[:n]

def scrape(url):
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    parts = soup.select("div[data-lyrics-container='true']")
    text  = "\n".join(p.get_text("\n") for p in parts)
    text  = re.sub(r"\[.*?]", "", text)
    return unicodedata.normalize("NFKC", text).strip()

def main():
    out = Path("merged_lyrics_all.jsonl").open("w", encoding="utf-8")
    for artist in ARTISTS:
        for song in tqdm.tqdm(search(artist, TOTAL_PER_ARTIST), desc=artist):
            try:
                lyric = scrape(song["url"])
            except Exception:
                continue
            json.dump({"instruction": f"Write a full song in the style of {artist}",
                       "output": lyric}, out, ensure_ascii=False)
            out.write("\n")
    print("✅  Saved → merged_lyrics_all.jsonl")

if __name__ == "__main__":
    main()
```

Run:

```bash
python scraper_20_songs.py
```

---

### <a id="scraper_120_songs"></a>scraper\_120\_songs.py – Full Harvest

Identical logic; only `TOTAL_PER_ARTIST = 120` and pagination caps raised:

```python
# ...identical imports and setup...
TOTAL_PER_ARTIST = 120    # deep harvest
MAX_PAGES        = 10     # widen pagination window
```

Run:

```bash
python scraper_120_songs.py
```

---

## Customising Artists & Song Counts

* **Change artists** – edit the `ARTISTS` list in either script.
* **Change quota** – tweak `TOTAL_PER_ARTIST`.
* **One-off run** – use the `--artist` and `--limit` CLI flags (already wired in both scripts):

```bash
python scraper_20_songs.py --artist "Radiohead" --limit 50
```

---

## Output Format

Both scripts append JSONL rows to `merged_lyrics_all.jsonl`:

```json
{"instruction": "Write a full song in the style of Bad Bunny", "output": "…lyrics…"}
```

This is tokeniser-friendly for fine-tuning LLMs or downstream NLP.

---

## Contributing

1. Fork → create feature branch → PR.
2. Stick to PEP-8; run `ruff` & `black`.
3. Add tests if you touch scraper logic.

---

## Licence

MIT © 2025 Your Name

```

**Copy, commit, push — your repo’s documentation is now complete and navigable.**
```
