"""
═══════════════════════════════════════════════════════════
   ملف الإعدادات الرئيسي - Crypto Whale Bot
═══════════════════════════════════════════════════════════
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════
# 🔑 إعدادات البوت الأساسية
# ══════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID_HERE")

# ══════════════════════════════════════════════════════════
# 📰 مصادر الأخبار (RSS Feeds) - محدثة
# ══════════════════════════════════════════════════════════

RSS_SOURCES = {
    "CoinTelegraph": {
        "url": "https://cointelegraph.com/rss",
        "priority": 9,
        "category": "crypto"
    },
    "CryptoPotato": {
        "url": "https://cryptopotato.com/feed/",
        "priority": 8,
        "category": "crypto"
    },
    "CoinDesk": {
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "priority": 8,
        "category": "crypto"
    },
    "The Block": {
        "url": "https://www.theblock.co/rss.xml?format=xml",
        "priority": 9,
        "category": "crypto"
    },
    "Bitcoinist": {
        "url": "https://bitcoinist.com/feed/",
        "priority": 7,
        "category": "crypto"
    },
    "CryptoSlate": {
        "url": "https://cryptoslate.com/feed/",
        "priority": 7,
        "category": "crypto"
    },
}

# ══════════════════════════════════════════════════════════
# 🔍 كلمات التصفية الأولية
# ══════════════════════════════════════════════════════════

FILTER_KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol",
    "bnb", "xrp", "cardano", "ada", "dogecoin", "doge",
    "ripple", "polygon", "matic", "avalanche", "avax",
    "polkadot", "dot", "chainlink", "link", "litecoin", "ltc",
    "crypto", "cryptocurrency", "blockchain", "defi", "nft",
    "sec", "cftc", "federal reserve", "fed", "us treasury",
    "el salvador", "binance", "coinbase", "ripple labs",
    "hack", "exploit", "breach", "lawsuit", "regulation",
    "ban", "approve", "etf", "halving", "fork", "upgrade",
    "emergency", "crash", "pump", "dump", "bull", "bear",
    "inflation", "interest rate", "fomc", "powell",
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

HIGH_IMPACT_WORDS = [
    "emergency", "flash crash", "sec approves", "sec rejects",
    "etf approved", "ban", "hack", "exploit", "breach",
    "lawsuit", "federal reserve", "interest rate", "fomc",
    "halving", "fork", "china ban", "el salvador",
]

MIN_IMPORTANCE_TO_SEND = 7

# ══════════════════════════════════════════════════════════
# 🪙 خريطة العملات
# ══════════════════════════════════════════════════════════

CRYPTO_MAP = {
    "bitcoin": "BTC", "btc": "BTC",
    "ethereum": "ETH", "eth": "ETH",
    "solana": "SOL", "sol": "SOL",
    "binance coin": "BNB", "bnb": "BNB",
    "ripple": "XRP", "xrp": "XRP",
    "cardano": "ADA", "ada": "ADA",
    "dogecoin": "DOGE", "doge": "DOGE",
    "polkadot": "DOT", "dot": "DOT",
    "chainlink": "LINK", "link": "LINK",
    "litecoin": "LTC", "ltc": "LTC",
    "polygon": "POL", "matic": "POL", "pol": "POL",
    "avalanche": "AVAX", "avax": "AVAX",
    "uniswap": "UNI", "uni": "UNI",
    "cosmos": "ATOM", "atom": "ATOM",
    "near protocol": "NEAR", "near": "NEAR",
    "aptos": "APT", "apt": "APT",
    "sui": "SUI",
    "arbitrum": "ARB", "arb": "ARB",
    "optimism": "OP", "op": "OP",
}

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

CHECK_INTERVAL = 60
REQUEST_TIMEOUT = 15
MAX_NEWS_PER_CHECK = 5
SENT_NEWS_FILE = "sent_news.json"
KEEP_ALIVE_PORT = 5000
