import hashlib
import random
import time
import feedparser

# المصادر الموثوقة (مثل سابقاً)
SOURCES = [
    "https://www.bloomberg.com/feed",
    "https://www.reuters.com/rss",
    "https://www.ft.com/?format=rss",
    "https://www.wsj.com/feed",
    "https://www.federalreserve.gov/feeds/press_all.xml",
    "https://www.sec.gov/news/pressreleases.rss",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

KEYWORDS = [
    "fed", "federal reserve", "interest rate", "inflation", "recession",
    "sec", "lawsuit", "ban", "regulation", "congress", "senate",
    "trump", "biden", "white house", "treasury", "sanctions", "war",
    "hack", "breach", "scam", "theft", "bank run", "default",
    "bitcoin", "ethereum", "crypto", "blockchain", "binance", "coinbase",
    "etf", "spot etf", "bitcoin etf", "ethereum etf"
]

# أخبار تجريبية احتياطية (ثابتة العناوين والروابط)
DEMO_NEWS = [
    ("🚨 SEC Files Lawsuit Against Binance, BNB Drops 8%", "https://cointelegraph.com/news/sec-sues-binance", "cointelegraph.com"),
    ("💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record", "https://cointelegraph.com/news/bitcoin-etf-record", "cointelegraph.com"),
    ("🏦 Federal Reserve Signals Rate Cuts, Crypto Markets Rally", "https://reuters.com/fed-rate-cuts", "reuters.com"),
    ("🔒 Major Exchange Hack: $200 Million in ETH Stolen", "https://thehackernews.com/crypto-hack", "thehackernews.com"),
    ("📈 Ethereum ETF Approval Expected Next Week", "https://decrypt.co/ethereum-etf-approval", "decrypt.co"),
]

def fetch_news(limit=8):
    news_list = []
    # 1. محاولة جلب أخبار حقيقية
    for url in SOURCES:
        try:
            feed = feedparser.parse(url, timeout=8)
            for entry in feed.entries[:3]:
                title = entry.title
                title_lower = title.lower()
                if any(kw in title_lower for kw in KEYWORDS):
                    # ID ثابت يعتمد على الرابط (أو الرابط + العنوان لو أردت)
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()
                    news_list.append({
                        'id': news_id,
                        'title': title,
                        'link': entry.link,
                        'source': url.split('/')[2]
                    })
        except:
            continue

    # 2. إذا لم نحصل على أخبار كافية، نضيف أخباراً تجريبية
    if len(news_list) < limit:
        for title, link, source in DEMO_NEWS:
            news_id = hashlib.md5(link.encode()).hexdigest()
            news_list.append({
                'id': news_id,
                'title': title,
                'link': link,
                'source': source
            })

    # إزالة التكرارات (نفس الرابط)
    unique = {}
    for news in news_list:
        if news['id'] not in unique:
            unique[news['id']] = news

    result = list(unique.values())
    random.shuffle(result)
    return result[:limit]

fetch_all_news = fetch_news
