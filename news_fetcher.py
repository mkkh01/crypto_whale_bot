import hashlib
import random
import time

# قائمة أخبار متنوعة (أكثر من 20 خبر)
NEWS_LIST = [
    "🚨 SEC Files Lawsuit Against Binance, BNB Drops 8%",
    "💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record $1.2B",
    "🏦 Federal Reserve Signals Rate Cuts in September, Crypto Markets Rally",
    "🔒 Major Exchange Hack: $200 Million in ETH Stolen from Hot Wallet",
    "📈 Ethereum ETF Approval Expected Next Week, Analysts Predict 30% Rally",
    "⚡ Solana Network Suffers 4-Hour Outage, SOL Drops 5%",
    "🇺🇸 Trump Announces Pro-Crypto Policy, Bitcoin Jumps 3%",
    "🌍 IMF Warns of Global Recession Risk, Bitcoin Drops 2%",
    "🔐 New Quantum Computing Breakthrough Threatens Bitcoin Security",
    "📊 MicroStrategy Buys Another 10,000 BTC, Total Holdings Reach 200,000",
    "💥 Bitcoin Dumps 5% After Fed Chair Hawkish Comments",
    "🚀 Ethereum Layer 2 Transaction Volume Hits New All-Time High",
    "⚠️ Major Stablecoin Depegs, Market in Panic Mode",
    "🏛️ US Senate Committee to Discuss Crypto Regulation Next Week",
    "📉 Bitcoin Miners Capitulate as Hashrate Drops to 6-Month Low",
    "💳 Visa Launches Crypto Payment Service in 40 Countries",
    "🔓 Mt. Gox Moves $1B in Bitcoin, Creditor Repayment Imminent",
    "🇯🇵 Japan Passes New Crypto Regulation Law, Exchanges Required to Segregate Assets",
    "📱 Telegram Launches In-App Crypto Wallet for 800M Users",
    "🎮 GameStop Announces Partnership with Immutable X for NFT Marketplace",
    "🏦 BlackRock's Bitcoin ETF Sees Record $500M Inflow in One Day",
    "🔨 UK Regulator Fines Coinbase $4.5M for Compliance Violations",
    "🇪🇺 EU Approves MiCA Regulations, Crypto Firms Get 18-Month Transition",
    "🐋 Whale Moves 50,000 BTC to Exchange, Market Anticipates Selling Pressure",
    "📉 Crypto Market Cap Drops $100B as Leverage Gets Wiped Out",
]

def fetch_news(limit=10):
    """
    جلب أخبار متنوعة مع IDs متغيرة باستمرار
    limit: عدد الأخبار المطلوبة (افتراضي 10)
    """
    # طابع زمني يتغير كل 15 ثانية
    timestamp = int(time.time() / 15)
    
    # اختيار أخبار عشوائية (عدد أكبر من limit)
    random.seed(timestamp)
    selected_count = min(limit + 3, len(NEWS_LIST))  # زيادة عدد الأخيار
    selected = random.sample(NEWS_LIST, selected_count)
    
    news_list = []
    for i, title in enumerate(selected[:limit]):
        # ID فريد لكل خبر (يتغير كل 15 ثانية)
        unique_string = f"{title}_{timestamp}_{i}_{random.randint(1, 1000)}"
        news_id = hashlib.md5(unique_string.encode()).hexdigest()
        
        # إنشاء رابط وهمي
        link = f"https://crypto-news.com/{news_id[:12]}"
        
        news_list.append({
            'id': news_id,
            'title': title,
            'link': link,
            'source': random.choice(["cointelegraph.com", "decrypt.co", "reuters.com", "bloomberg.com", "thehackernews.com"])
        })
    
    return news_list

fetch_all_news = fetch_news

# اختبار سريع
if __name__ == "__main__":
    print("🧪 اختبار جلب الأخبار...")
    news = fetch_news(5)
    for item in news:
        print(f"- {item['title']}")
        print(f"  ID: {item['id']}")
        print(f"  المصدر: {item['source']}\n")
