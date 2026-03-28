"""
═══════════════════════════════════════════════════════════
   ملف الإعدادات الرئيسي - Crypto Whale Bot
═══════════════════════════════════════════════════════════
يحتوي على جميع الإعدادات القابلة للتعديل:
- بيانات البوت
- مصادر الأخبار
- كلمات التصفية
- إعدادات التحليل
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# ══════════════════════════════════════════════════════════
# 🔑 إعدادات البوت الأساسية
# ══════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID_HERE")

# ══════════════════════════════════════════════════════════
# 📰 مصادر الأخبار (RSS Feeds)
# ══════════════════════════════════════════════════════════

RSS_SOURCES = {
    # مواقع كريبتو متخصصة
    "CoinTelegraph": {
        "url": "https://cointelegraph.com/rss",
        "priority": 9,  # أولوية المصدر (1-10)
        "category": "crypto"
    },
    "Decrypt": {
        "url": "https://decrypt.co/feed",
        "priority": 8,
        "category": "crypto"
    },
    "CryptoPotato": {
        "url": "https://cryptopotato.com/feed/",
        "priority": 7,
        "category": "crypto"
    },
    "The Block": {
        "url": "https://www.theblock.co/rss.xml",
        "priority": 9,
        "category": "crypto"
    },
    "CoinDesk": {
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "priority": 8,
        "category": "crypto"
    },
    # وكالات عامة (للأخبار المؤثرة)
    "Reuters Tech": {
        "url": "https://www.reuters.com/technology/rss",
        "priority": 10,
        "category": "general"
    },
}

# ══════════════════════════════════════════════════════════
# 🔍 كلمات التصفية الأولية
# ══════════════════════════════════════════════════════════

# الكلمات التي يجب أن يحتويها الخبر للمرور
FILTER_KEYWORDS = [
    # عملات
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol",
    "bnb", "xrp", "cardano", "ada", "dogecoin", "doge",
    "ripple", "polygon", "matic", "avalanche", "avax",
    "polkadot", "dot", "chainlink", "link", "litecoin", "ltc",
    "crypto", "cryptocurrency", "blockchain", "defi", "nft",
    
    # جهات تنظيمية
    "sec", "cftc", "federal reserve", "fed", "us treasury",
    "el salvador", "binance", "coinbase", "ripple labs",
    
    # أحداث مهمة
    "hack", "exploit", "breach", "lawsuit", "regulation",
    "ban", "approve", "etf", "halving", "fork", "upgrade",
    "emergency", "crash", "pump", "dump", "bull", "bear",
    "inflation", "interest rate", "fomc", "powell",
    
    # تقنية
    "smart contract", "layer 2", "l2", "rollup", "bridge",
    "staking", "mining", "token burn", "airdrop",
]

# ══════════════════════════════════════════════════════════
# 🏷️ إعدادات التصنيف
# ══════════════════════════════════════════════════════════

CATEGORY_KEYWORDS = {
    "⚖️ تنظيمي": [
        "sec", "cftc", "regulation", "lawsuit", "ban", "approve",
        "compliance", "fine", "penalty", "legal", "court", "judge",
        "investigation", "enforcement", "subpoena", "indictment"
    ],
    "📊 اقتصادي": [
        "federal reserve", "fed", "interest rate", "inflation",
        "fomc", "powell", "gdp", "employment", "unemployment",
        "recession", "stimulus", "quantitative", "treasury",
        "monetary policy", "rate cut", "rate hike"
    ],
    "🔒 أمني": [
        "hack", "exploit", "breach", "vulnerability", "attack",
        "malware", "phishing", "rug pull", "scam", "theft",
        "drain", "compromised", "security", "audit"
    ],
    "🌍 جيوسياسي": [
        "war", "sanction", "china", "russia", "ukraine",
        "el salvador", "middle east", "geopolitical", "conflict",
        "tension", "embargo", "trade war", "tariff"
    ],
    "💻 تقني": [
        "upgrade", "fork", "halving", "smart contract", "layer 2",
        "rollup", "bridge", "staking", "mining", "token burn",
        "airdrop", "mainnet", "testnet", "protocol", "integration"
    ],
    "📈 سوقي": [
        "etf", "institutional", "whale", "bull", "bear",
        "pump", "dump", "crash", "rally", "correction",
        "resistance", "support", "volume", "market cap",
        "all-time high", "ath", "price", "trading"
    ],
}

# ══════════════════════════════════════════════════════════
# 😊 إعدادات تحليل المشاعر
# ══════════════════════════════════════════════════════════

POSITIVE_WORDS = [
    "surge", "jump", "rally", "bull", "gain", "profit", "grow",
    "adoption", "approve", "win", "success", "breakthrough",
    "upgrade", "innovation", "partnership", "launch", "milestone",
    "recovery", "soar", "skyrocket", "boom", "positive", "optimistic",
    "bullish", "outperform", "exceed", "record", "high", "boost"
]

NEGATIVE_WORDS = [
    "crash", "drop", "fall", "decline", "bear", "loss", "risk",
    "ban", "reject", "fail", "hack", "exploit", "scam", "fraud",
    "lawsuit", "investigation", "fine", "penalty", "warning",
    "concern", "fear", "panic", "dump", "plunge", "slump",
    "negative", "pessimistic", "bearish", "underperform", "breach"
]

# ══════════════════════════════════════════════════════════
# ⭐ إعدادات تقييم الأهمية
# ══════════════════════════════════════════════════════════

# كلمات تزيد الأهمية بقوة
HIGH_IMPACT_WORDS = [
    "emergency", "flash crash", "sec approves", "sec rejects",
    "etf approved", "ban", "hack", "exploit", "breach",
    "lawsuit", "federal reserve", "interest rate", "fomc",
    "halving", "fork", "china ban", "el salvador",
]

# عتبة الأهمية للإرسال (فقط الأخبار ≥ هذا الرقم تُرسل)
MIN_IMPORTANCE_TO_SEND = 7

# ══════════════════════════════════════════════════════════
# 🪙 خريطة العملات
# ══════════════════════════════════════════════════════════

CRYPTO_MAP = {
    #BTC
    "bitcoin": "BTC", "btc": "BTC",
    # ETH
    "ethereum": "ETH", "eth": "ETH",
    # SOL
    "solana": "SOL", "sol": "SOL",
    # BNB
    "binance coin": "BNB", "bnb": "BNB",
    # XRP
    "ripple": "XRP", "xrp": "XRP",
    # ADA
    "cardano": "ADA", "ada": "ADA",
    # DOGE
    "dogecoin": "DOGE", "doge": "DOGE",
    # DOT
    "polkadot": "DOT", "dot": "DOT",
    # LINK
    "chainlink": "LINK", "link": "LINK",
    # LTC
    "litecoin": "LTC", "ltc": "LTC",
    # MATIC/POL
    "polygon": "POL", "matic": "POL", "pol": "POL",
    # AVAX
    "avalanche": "AVAX", "avax": "AVAX",
    # UNI
    "uniswap": "UNI", "uni": "UNI",
    # ATOM
    "cosmos": "ATOM", "atom": "ATOM",
    # NEAR
    "near protocol": "NEAR", "near": "NEAR",
    # APT
    "aptos": "APT", "apt": "APT",
    # SUI
    "sui": "SUI",
    # ARB
    "arbitrum": "ARB", "arb": "ARB",
    # OP
    "optimism": "OP", "op": "OP",
}

# رموز العملات (للعرض)
CRYPTO_EMOJIS = {
    "BTC": "₿", "ETH": "⟠", "SOL": "◎", "BNB": "🔶",
    "XRP": "✕", "ADA": "🔵", "DOGE": "🐕", "DOT": "⬡",
    "LINK": "⬡", "LTC": "Ł", "POL": "🟣", "AVAX": "🔺",
    "UNI": "🦄", "ATOM": "⚛️", "NEAR": "🔵", "APT": "🟢",
    "SUI": "💧", "ARB": "🔵", "OP": "🔴",
}

# ══════════════════════════════════════════════════════════
# ⚙️ إعدادات عامة
# ══════════════════════════════════════════════════════════

# فترة الفحص (بالثواني)
CHECK_INTERVAL = 60

# مهلة طلبات HTTP (بالثواني)
REQUEST_TIMEOUT = 15

# الحد الأقصى للأخبار المرسلة في المرة الواحدة
MAX_NEWS_PER_CHECK = 5

# ملف تخزين الأخبار المرسلة
SENT_NEWS_FILE = "sent_news.json"

# منفذ خادم الويب الوهمي
KEEP_ALIVE_PORT = 5000
