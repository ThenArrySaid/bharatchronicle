#!/usr/bin/env python3
"""
Fetch Indian news RSS/Atom feeds and write a compact JSON used by the site.

Fixes:
- Normalizes ALL dates to timezone-aware UTC so sorting never crashes
  (no more: "can't compare offset-naive and offset-aware datetimes")
- Grabs thumbnails when available (media:content / enclosure)
- Produces short summaries (≈ 60–90 words) for Inshorts-style cards
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional, List
import feedparser  # installed in workflow
import requests    # installed in workflow

# ---------- Config ----------
OUTPUT = Path("data/news.json")
MAX_ITEMS = 60

# Curated, mainstream, India-focused sources (you can edit freely)
FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-top-stories",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://indianexpress.com/section/india/feed/",
    "https://www.thehindu.com/news/national/feeder/default.rss",
]

# ---------- Helpers ----------

@dataclass
class NewsItem:
    title: str
    description: str
    link: str
    image: Optional[str]
    date: datetime  # timezone-aware UTC

    def to_public(self) -> dict:
        # Strip the 'date' from the JSON we serve (site doesn’t need it)
        d = asdict(self)
        d.pop("date", None)
        return d

def cleanse_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)         # remove tags
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text) # entities → space
    text = re.sub(r"\s+", " ", text).strip()
    return text

def summarize(text: str, max_words: int = 90) -> str:
    words = cleanse_html(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "…"

def to_utc(dt: Optional[datetime]) -> datetime:
    """
    Normalize any datetime to timezone-aware UTC.
    - None  -> minimal UTC sentinel
    - naive -> set tzinfo=UTC
    - aware -> convert to UTC
    """
    if dt is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_entry_date(entry) -> datetime:
    # Try structured date first (published_parsed / updated_parsed)
    for key in ("published", "updated", "created"):
        val = entry.get(key)
        if val:
            try:
                return to_utc(parsedate_to_datetime(val))
            except Exception:
                pass
    # feedparser may also expose *_parsed as time.struct_time; fall back:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = entry.get(key)
        if val:
            try:
                # Convert struct_time to datetime (naive)
                dt = datetime(*val[:6])
                return to_utc(dt)
            except Exception:
                pass
    return to_utc(None)

def extract_image(entry) -> Optional[str]:
    # media:content / enclosure
    media = entry.get("media_content") or entry.get("media_thumbnail")
    if isinstance(media, list) and media:
        url = media[0].get("url")
        if url:
            return url
    if "links" in entry:
        for l in entry["links"]:
            if l.get("rel") in ("enclosure", "thumbnail") and l.get("type", "").startswith(("image/", "img/")):
                return l.get("href")
    # As a last (best-effort) option, try OpenGraph image from the article:
    url = entry.get("link")
    if not url:
        return None
    try:
        r = requests.get(url, timeout=5)
        if r.ok:
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text, re.I)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None

# ---------- Main ----------

def fetch_feed(url: str) -> List[NewsItem]:
    parsed = feedparser.parse(url)
    items: List[NewsItem] = []
    for e in parsed.entries:
        title = cleanse_html(e.get("title", "")).strip()
        link = e.get("link") or ""
        if not (title and link):
            continue
        desc_source = e.get("summary") or e.get("description") or ""
        item = NewsItem(
            title=title,
            description=summarize(desc_source),
            link=link,
            image=extract_image(e),
            date=parse_entry_date(e),
        )
        items.append(item)
    return items

def main():
    all_items: List[NewsItem] = []
    for f in FEEDS:
        try:
            all_items.extend(fetch_feed(f))
        except Exception as ex:
            print(f"[WARN] Failed {f}: {ex}")

    # Normalize and sort (dates are already UTC-aware)
    all_items.sort(key=lambda x: x.date, reverse=True)

    # De-duplicate by link
    seen = set()
    deduped: List[NewsItem] = []
    for it in all_items:
        if it.link in seen:
            continue
        seen.add(it.link)
        deduped.append(it)
        if len(deduped) >= MAX_ITEMS:
            break

    # Ensure output dir exists
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Write public JSON (without the internal date field)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump([it.to_public() for it in deduped], f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(deduped)} items → {OUTPUT}")

if __name__ == "__main__":
    main()
