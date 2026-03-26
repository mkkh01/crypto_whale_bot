import feedparser
import hashlib
import time

# مصادر بسيطة ومضمونة
SOURCES = [
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    "https://www.newsbtc.com/feed/",
    "https://cryptoslate.com/feed/",
]

# كلمات مفتاحية لفلترة الأخبار المهمة (اختياري، يمكن تعطيلها)
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance",
    "sec", "etf", "fed", "inflation", "recession", "economy", "dollar",
    "regulation", "lawsuit", "ban", "hack", "breach", "war", "sanctions"
]

def fetch_news(limit=5, filter_keywords=False):
    """
    جلب الأخبار من مصادر بسيطة
    
    Args:
        limit: عدد الأخبار المطلوبة
        filter_keywords: True لفلترة حسب الكلمات المفتاحية، False لجلب الكل
    
    Returns:
        list: قائمة بالأخبار
    """
    news_list = []
    
    for url in SOURCES:
        try:
            print(f"جاري جلب: {url}")
            feed = feedparser.parse(url, timeout=10)
            
            for entry in feed.entries[:5]:  # 5 أخبار من كل مصدر
                title = entry.title
                
                # فلترة اختيارية
                if filter_keywords:
                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in KEYWORDS):
                        continue
                
                news_id = hashlib.md5(entry.link.encode()).hexdigest()
                news_list.append({
                    'id': news_id,
                    'title': title,
                    'link': entry.link,
                    'source': url.split('/')[2]
                })
            print(f"تم جلب {len(feed.entries[:5])} خبر من {url}")
        except Exception as e:
            print(f"خطأ في {url}: {e}")
            continue
    
    # إزالة التكرارات
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news
    
    result = list(unique.values())
    print(f"إجمالي الأخبار بعد إزالة التكرار: {len(result)}")
    return result[:limit]

# للتوافق مع الكود القديم
fetch_all_news = fetch_news

# اختبار سريع عند التشغيل المباشر
if __name__ == "__main__":
    print("=== اختبار جلب الأخبار ===\n")
    news = fetch_news(3, filter_keywords=False)
    print(f"\n=== النتائج ({len(news)} خبر) ===\n")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
        print(f"   المصدر: {item['source']}")
        print(f"   الرابط: {item['link']}\n")
