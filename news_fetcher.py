import feedparser
import hashlib

SOURCES = [
    # أخبار كريبتو متخصصة
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cryptoslate.com/feed/",
    "https://www.newsbtc.com/feed/",
    
    # أخبار اقتصادية عالمية (تؤثر على الأسواق)
    "https://www.bloomberg.com/feed",
    "https://www.reuters.com/rss",
    "https://www.ft.com/?format=rss",
    "https://www.wsj.com/feed",
    "https://www.economist.com/feeds/print-sections/77/finance-and-economics.xml",
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    
    # أخبار سياسية (تؤثر على الاستقرار)
    "https://www.politico.com/rss",
    "https://www.bbc.com/news",
    "https://www.theguardian.com/world/rss",
    "https://www.washingtonpost.com/feed",
    "https://www.cnn.com/rss",
    
    # أخبار البنك الفيدرالي والاحتياطي
    "https://www.federalreserve.gov/feeds/press_all.xml",
    "https://www.ecb.europa.eu/rss/",
    
    # أخبار عسكرية وجيوسياسية
    "https://www.defensenews.com/feed/",
    "https://www.aljazeera.com/xml/rss.xml",
    "https://www.reuters.com/rss/world",
    
    # أخبار تقنية وأمنية
    "https://www.wired.com/feed/rss",
    "https://thehackernews.com/feeds/posts/default",
    "https://www.bleepingcomputer.com/feed/",
    
    # أخبار الأسواق المالية
    "https://www.marketwatch.com/feed",
    "https://seekingalpha.com/feed.xml"
]

# كلمات مفتاحية لفلترة الأخبار المهمة
KEYWORDS = [
    # كلمات كريبتو
    "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "binance", "coinbase",
    "solana", "xrp", "dogecoin", "ripple", "sec", "etf", "spot etf",
    
    # كلمات اقتصادية
    "fed", "federal reserve", "interest rate", "inflation", "recession", "economy",
    "dollar", "usd", "liquidity", "stimulus", "quantitative easing", "jobs report",
    "unemployment", "gdp", "bond yield", "treasury", "banking", "credit",
    
    # كلمات سياسية وتنظيمية
    "sec", "regulation", "lawsuit", "ban", "legal", "congress", "senate", "house",
    "trump", "biden", "white house", "treasury", "tax", "sanctions",
    
    # كلمات جيوسياسية وعسكرية
    "war", "conflict", "iran", "russia", "china", "ukraine", "israel", "oil price",
    "sanctions", "military", "attack", "crisis", "emergency",
    
    # كلمات أمنية
    "hack", "breach", "scam", "theft", "exploit", "security", "vulnerability"
]

def fetch_news(limit=10):
    """
    جلب الأخبار من جميع المصادر وتصفيتها حسب الكلمات المفتاحية
    """
    news_list = []
    
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # 3 أخبار من كل مصدر
                title = entry.title.lower()
                # تصفية: فقط الأخبار التي تحتوي كلمات مفتاحية مهمة
                if any(kw in title for kw in KEYWORDS):
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': entry.title,
                        'link': entry.link,
                        'source': url.split('/')[2]
                    })
        except Exception as e:
            # تجاهل الأخطاء واستمر
            pass
    
    # إزالة التكرارات بناءً على ID
    unique_news = {}
    for news in news_list:
        if news['id'] not in unique_news:
            unique_news[news['id']] = news
    
    return list(unique_news.values())[:limit]

fetch_all_news = fetch_news
