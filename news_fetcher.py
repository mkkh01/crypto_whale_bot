import feedparser
import hashlib
import random
import time

# مصادر RSS موثوقة (تعمل من Render)
SOURCES = [
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    "https://www.newsbtc.com/feed/",
    "https://cryptoslate.com/feed/",
]

# كلمات مفتاحية واسعة لتغطية معظم الأخبار المؤثرة
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance", "coinbase",
    "sec", "etf", "fed", "inflation", "recession", "economy", "dollar",
    "regulation", "lawsuit", "hack", "breach", "war", "sanctions", "trump", "biden",
    "solana", "xrp", "dogecoin", "ripple"
]

def fetch_news(limit=8):
    """جلب أخبار حقيقية فقط من المصادر المحددة"""
    news_list = []
    for url in SOURCES:
        try:
            feed = feedparser.parse(url, timeout=8)
            for entry in feed.entries[:3]:
                title = entry.title
                title_lower = title.lower()
                # تصفية خفيفة: يجب أن تحتوي على كلمة من KEYWORDS
                if any(kw in title_lower for kw in KEYWORDS):
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': title,
                        'link': entry.link,
                        'source': url.split('/')[2]
                    })
        except Exception as e:
            print(f"خطأ في {url}: {e}")
            continue

    # إزالة التكرارات
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news

    result = list(unique.values())
    random.shuffle(result)
    return result[:limit]

fetch_all_news = fetch_news
