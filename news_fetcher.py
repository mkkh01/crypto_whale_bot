import feedparser
import hashlib
import random
import time

# مصادر متنوعة (سياسية، اقتصادية، عسكرية، كريبتو)
SOURCES = [
    # أخبار كريبتو
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    
    # أخبار اقتصادية عالمية
    "https://www.bloomberg.com/feed",
    "https://www.reuters.com/rss",
    "https://www.ft.com/?format=rss",
    
    # أخبار سياسية وجيوسياسية
    "https://www.bbc.com/news",
    "https://www.aljazeera.com/xml/rss.xml",
    "https://www.politico.com/rss",
    
    # أخبار عسكرية وأمنية
    "https://www.defensenews.com/feed/",
    "https://thehackernews.com/feeds/posts/default",
]

# كلمات مفتاحية لفلترة الأخبار المؤثرة
KEYWORDS = [
    # كريبتو
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance", "coinbase", "sec", "etf",
    "solana", "xrp", "dogecoin", "ripple",
    # اقتصادي
    "fed", "federal reserve", "inflation", "recession", "interest rate", "economy", "dollar", "stimulus",
    "jobs report", "unemployment", "gdp", "banking", "credit",
    # سياسي
    "trump", "biden", "congress", "senate", "regulation", "sanctions", "war", "conflict",
    # جيوسياسي وعسكري
    "iran", "russia", "china", "ukraine", "israel", "oil price", "attack", "crisis", "emergency",
    # أمني
    "hack", "breach", "scam", "theft", "exploit", "security", "vulnerability"
]

def fetch_news(limit=8):
    """
    جلب أخبار حقيقية من مصادر متنوعة وتصفيتها حسب الكلمات المفتاحية
    """
    news_list = []
    
    for url in SOURCES:
        try:
            feed = feedparser.parse(url, timeout=8)
            for entry in feed.entries[:3]:
                title = entry.title.lower()
                # فلترة حسب الكلمات المفتاحية
                if any(kw in title for kw in KEYWORDS):
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': entry.title,
                        'link': entry.link,
                        'source': url.split('/')[2]
                    })
        except:
            continue
    
    # إزالة التكرارات
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news
    
    # خلط عشوائي
    result = list(unique.values())
    random.shuffle(result)
    
    return result[:limit]

fetch_all_news = fetch_news
