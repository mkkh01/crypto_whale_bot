import hashlib
import random
import time
import feedparser

# أخبار تجريبية متنوعة
TEST_NEWS_BASE = [
    {'title': '🚨 SEC Files Lawsuit Against Binance, BNB Drops 8%', 'source': 'cointelegraph.com'},
    {'title': '💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record', 'source': 'cointelegraph.com'},
    {'title': '🏦 Federal Reserve Signals Rate Cuts, Crypto Markets Rally', 'source': 'reuters.com'},
    {'title': '🔒 Major Exchange Hack: $200 Million in ETH Stolen', 'source': 'thehackernews.com'},
    {'title': '📈 Ethereum ETF Approval Expected Next Week', 'source': 'decrypt.co'},
    {'title': '⚡ Solana Network Suffers Outage, SOL Drops 5%', 'source': 'cryptoslate.com'},
    {'title': '🇺🇸 Trump Announces Pro-Crypto Policy, Bitcoin Jumps', 'source': 'politico.com'},
    {'title': '🌍 IMF Warns of Global Recession Risk', 'source': 'reuters.com'},
    {'title': '🔐 New Quantum Computing Threatens Bitcoin Security', 'source': 'wired.com'},
    {'title': '📊 MicroStrategy Buys Another 10,000 BTC', 'source': 'newsbtc.com'},
]

def fetch_news(limit=8):
    """
    جلب أخبار جديدة باستمرار (تتغير كل دورة)
    """
    # طابع زمني يتغير كل 15 ثانية
    timestamp = int(time.time() / 15)
    
    # اختيار أخبار عشوائية مع تغيير الترتيب
    random.seed(timestamp)
    shuffled_news = random.sample(TEST_NEWS_BASE, min(limit, len(TEST_NEWS_BASE)))
    
    # إنشاء أخبار بـ IDs متغيرة
    news_list = []
    for i, item in enumerate(shuffled_news):
        # ID يعتمد على العنوان + الوقت + رقم عشوائي
        unique_string = f"{item['title']}_{timestamp}_{i}_{random.randint(1, 1000)}"
        news_id = hashlib.md5(unique_string.encode()).hexdigest()
        
        news_list.append({
            'id': news_id,
            'title': item['title'],
            'link': f"https://{item['source']}/news/{news_id}",
            'source': item['source']
        })
    
    return news_list

fetch_all_news = fetch_news
