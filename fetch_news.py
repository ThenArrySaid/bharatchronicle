#!/usr/bin/env python3
"""
fetch_news.py
----------------
This utility script generates a `news.json` file from any RSS feed.  It is designed
to automate the content for the Bharat Chronicle website.  You can run this
script periodically on your own computer or server to refresh the news on your
site.  The resulting JSON file should be placed in the `data` directory so
that `script.js` can load it.

Usage:
    python fetch_news.py --feed_url https://feeds.bbci.co.uk/news/world/rss.xml --limit 20

Requirements:
    - Python 3.7 or later
    - feedparser package (install via `pip install feedparser`)

Note:
    Because this environment has restricted network access, the script cannot be
    executed here.  You should run it on your own machine with internet
    connectivity to fetch real news feeds.
"""

import argparse
import json
from datetime import datetime

try:
    import feedparser
except ImportError as e:
    raise SystemExit(
        "The feedparser library is required to run this script. "
        "Install it using `pip install feedparser` and try again."
    )


def fetch_feed(url: str, limit: int = 20):
    """Fetch and parse an RSS/Atom feed, returning a list of news items."""
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        # Construct a short description from the summary or description field
        summary = entry.get('summary') or entry.get('description') or ''
        # Trim summary to about 200 characters
        plain_summary = summary.replace('\n', ' ').replace('\r', ' ').strip()
        if len(plain_summary) > 200:
            plain_summary = plain_summary[:197] + '...'

        item = {
            "title": entry.get('title', 'Untitled'),
            "description": plain_summary,
            "link": entry.get('link', '#'),
            "pubDate": entry.get('published', datetime.utcnow().isoformat()),
            "image": None,
        }
        # Attempt to extract an image if provided
        if 'media_thumbnail' in entry:
            item['image'] = entry.media_thumbnail[0]['url']
        elif 'media_content' in entry:
            item['image'] = entry.media_content[0]['url']
        items.append(item)
    return items


def main():
    parser = argparse.ArgumentParser(description="Generate news.json from an RSS feed")
    parser.add_argument('--feed_url', required=True, help='URL of the RSS/Atom feed to fetch')
    parser.add_argument('--output', default='data/news.json', help='Output JSON file path')
    parser.add_argument('--limit', type=int, default=20, help='Maximum number of feed items to include')
    args = parser.parse_args()

    items = fetch_feed(args.feed_url, args.limit)
    with open(args.output, 'w', encoding='utf-8') as fp:
        json.dump(items, fp, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to {args.output}")


if __name__ == '__main__':
    main()