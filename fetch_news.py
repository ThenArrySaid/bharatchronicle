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
    """
    Entry point for the feed generation script.

    This function accepts either a single ``--feed_url`` argument or a comma‑separated
    list of ``--feed_urls``.  If neither is provided, it falls back to a preset
    collection of pro‑India news RSS feeds.  The script will download items
    from each specified feed, merge them together, and trim the list to the
    requested limit.  The merged items are then written to the output JSON file.
    """
    parser = argparse.ArgumentParser(
        description="Generate news.json from one or more RSS/Atom feeds"
    )
    parser.add_argument(
        '--feed_url',
        help='Single URL of an RSS/Atom feed to fetch (overrides the default list)'
    )
    parser.add_argument(
        '--feed_urls',
        help='Comma‑separated list of RSS/Atom feed URLs to fetch'
    )
    parser.add_argument(
        '--output',
        default='data/news.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of feed items to include'
    )
    args = parser.parse_args()

    # Determine the list of feeds to use
    feeds = []
    if args.feed_url:
        feeds = [args.feed_url.strip()]
    elif args.feed_urls:
        feeds = [u.strip() for u in args.feed_urls.split(',') if u.strip()]
    else:
        # Default pro‑India feed list. These sources were chosen for their
        # relevance to Indian news and culture. Feel free to adjust this list
        # to suit your editorial focus.  If you add or remove feeds, make sure
        # they allow redistribution of their content.
        feeds = [
            'https://feeds.feedburner.com/ndtvnews-india-news',        # NDTV India news
            'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',  # Times of India top stories
            'https://indianexpress.com/feed/',                          # Indian Express latest news
            'https://www.thehindu.com/news/national/?service=rss',      # The Hindu national news
        ]

    all_items = []
    for url in feeds:
        try:
            items = fetch_feed(url, args.limit)
            all_items.extend(items)
        except Exception as exc:  # catch any feed parsing errors
            print(f"Warning: failed to fetch feed {url}: {exc}")

    # Sort combined items by publication date descending (newest first)
    def parse_date(item):
        try:
            return datetime.fromisoformat(item['pubDate'])
        except Exception:
            return datetime.utcnow()
    all_items.sort(key=parse_date, reverse=True)

    # Trim to the requested limit
    trimmed = all_items[: args.limit]

    with open(args.output, 'w', encoding='utf-8') as fp:
        json.dump(trimmed, fp, indent=2, ensure_ascii=False)
    print(f"Wrote {len(trimmed)} items to {args.output}")


if __name__ == '__main__':
    main()