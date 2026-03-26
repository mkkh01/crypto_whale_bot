import feedparser
import hashlib

# مصادر بديلة تعمل من أي مكان
SOURCES = [
    "https://cryptoslate.com/feed/",
    "https://www.newsbtc.com/feed/",
]

def fetch_news(limit=5):
    """
    جلب الأخبار من مصادر بديلة
    """
    news_list = []
    
    for url in SOURCES:
        try:
            feed = feedparser.parse(url, timeout=15)
            
            for entry in feed.entries[:5]:
                news_id = hashlib.md5(entry.link.encode()).hexdigest()
                news_list.append({
                    'id': news_id,
                    'title': entry.title,
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
    
    return list(unique.values())[:limit]

fetch_all_news = fetch_news
