import feedparser
import hashlib
import time
import random

# مصادر محدودة ولكن قوية (12 مصدر فقط)
SOURCES = [
    # أخبار كريبتو أساسية
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    
    # أخبار اقتصادية عالمية
    "https://www.bloomberg.com/feed",
    "https://www.reuters.com/rss",
    
    # أخبار سياسية
    "https://www.bbc.com/news",
    "https://www.aljazeera.com/xml/rss.xml",
    
    # أخبار البنك الفيدرالي
    "https://www.federalreserve.gov/feeds/press_all.xml",
    
    # أخبار أمنية
    "https://thehackernews.com/feeds/posts/default",
]

# كلمات مفتاحية لفلترة الأخبار المهمة
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance",
    "sec", "etf", "fed", "inflation", "recession", "economy", "dollar",
    "regulation", "lawsuit", "ban", "hack", "breach", "war", "sanctions",
    "interest rate", "trump", "biden", "banking", "crash", "surge"
]

def fetch_news(limit=8):
    """
    جلب الأخبار مع مهلة زمنية وتجنب التوقف
    """
    news_list = []
    
    for url in SOURCES:
        try:
            # مهلة زمنية 5 ثواني لكل مصدر
            feed = feedparser.parse(url, timeout=5)
            
            for entry in feed.entries[:2]:
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
        except Exception as e:
            # تجاهل المصادر التي لا تستجيب بسرعة
            continue
    
    # إزالة التكرارات
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news
    
    # ترتيب عشوائي لتفادي نمط ثابت
    result = list(unique.values())
    random.shuffle(result)
    
    return result[:limit]

fetch_all_news = fetch_news
