import feedparser
import hashlib
import random
import requests
import time

SOURCES = [
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://cryptopotato.com/feed",
    "https://www.newsbtc.com/feed/",
    "https://cryptoslate.com/feed/",
]

# كلمات مفتاحية للعملات المدعومة
COIN_KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth"],
    "SOL": ["solana", "sol"],
    "XRP": ["ripple", "xrp"],
    "BNB": ["binance", "bnb"],
    "DOGE": ["dogecoin", "doge"],
}

# كلمات مفتاحية عامة للأخبار المؤثرة
GENERAL_KEYWORDS = [
    "sec", "etf", "fed", "inflation", "recession", "economy", "dollar",
    "regulation", "lawsuit", "hack", "breach", "war", "sanctions", "trump", "biden"
]

def extract_affected_coins(title):
    """استخراج العملات المتأثرة من عنوان الخبر"""
    title_lower = title.lower()
    affected = []
    for coin, keywords in COIN_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            affected.append(coin)
    return affected if affected else ["عام"]

def fetch_news(limit=10):
    news_list = []
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:3]:
                title = entry.title
                title_lower = title.lower()
                # الخبر مهم إذا ذكر عملة أو كلمة عامة مؤثرة
                is_important = any(
                    any(kw in title_lower for kw in keywords) for keywords in COIN_KEYWORDS.values()
                ) or any(kw in title_lower for kw in GENERAL_KEYWORDS)
                if is_important:
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': title,
                        'link': entry.link,
                        'source': url.split('/')[2],
                        'coins': extract_affected_coins(title)
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
