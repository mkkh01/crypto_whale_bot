import feedparser
import hashlib

SOURCES = [
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

def fetch_news(limit=5):
    news_list = []
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                news_id = hashlib.md5(entry.link.encode()).hexdigest()
                news_list.append({
                    'id': news_id,
                    'title': entry.title,
                    'link': entry.link,
                    'source': url.split('/')[2]
                })
        except:
            pass
    return news_list[:limit]

fetch_all_news = fetch_news
