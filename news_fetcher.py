import feedparser
import hashlib

# مصادر الأخبار
SOURCES = [
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://www.bloomberg.com/feed",
    "https://www.reuters.com/rss",
    "https://www.bbc.com/news",
    "https://www.federalreserve.gov/feeds/press_all.xml",
]

# كلمات مفتاحية لفلترة الأخبار المهمة
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance", "coinbase",
    "sec", "etf", "fed", "inflation", "recession", "economy", "dollar",
    "regulation", "lawsuit", "ban", "hack", "breach", "war", "sanctions"
]

def fetch_news(limit=8):
    news_list = []
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.title.lower()
                if any(kw in title for kw in KEYWORDS):
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': entry.title,
                        'link': entry.link,
                        'source': url.split('/')[2]
                    })
        except:
            pass
    
    # إزالة التكرار
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news
    
    return list(unique.values())[:limit]

fetch_all_news = fetch_news
