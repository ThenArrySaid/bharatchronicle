import requests
import feedparser
import json
from datetime import datetime, timezone
import time

def _to_utc(dt):
    """Convert any datetime into a safe UTC datetime."""
    if dt is None:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    if isinstance(dt, time.struct_time):  # feedparser often gives this
        dt = datetime(*dt[:6])
    if getattr(dt, "tzinfo", None) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

# Example RSS feeds (replace/add your sources here)
FEEDS = [
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.thehindu.com/feeder/default.rss",
    "https://indianexpress.com/feed/",
]

def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            title = entry.get("title", "No title")
            link = entry.get("link", "#")
            summary = entry.get("summary", "")
            image_url = None

            # Try to get an image if available
            if "media_content" in entry:
                image_url = entry.media_content[0].get("url")
            elif "links" in entry:
                for l in entry.links:
                    if l.get("type", "").startswith("image"):
                        image_url = l.get("href")
                        break

            # Published date
            dt = None
            if hasattr(entry, "published_parsed"):
                dt = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed"):
                dt = datetime(*entry.updated_parsed[:6])

            dt = _to_utc(dt)

            items.append({
                "title": title,
                "link": link,
                "description": summary,
                "image": image_url,
                "date": dt
            })
        return items
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    all_items = []
    for url in FEEDS:
        all_items.extend(fetch_feed(url))

    # ✅ Sort by date safely (all UTC now)
    all_items.sort(key=lambda it: _to_utc(it.get("date")), reverse=True)

    # Convert datetime objects to ISO strings for JSON
    for it in all_items:
        if isinstance(it["date"], datetime):
            it["date"] = it["date"].isoformat()

    # Save to JSON
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
