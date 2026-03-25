import re
import requests

# دالة الترجمة
def translate_to_arabic(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en',
            'tl': 'ar',
            'dt': 't',
            'q': text
        }
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        return result[0][0][0]
    except:
        return text

COINS = {
    'BTC': ['bitcoin', 'btc'],
    'ETH': ['ethereum', 'eth'],
    'SOL': ['solana', 'sol'],
    'XRP': ['ripple', 'xrp'],
    'DOGE': ['dogecoin', 'doge'],
    'BNB': ['binance', 'bnb']
}

CATEGORIES = {
    '🏛️ تنظيمي': ['sec', 'regulation', 'law', 'ban', 'legal', 'congress', 'senate'],
    '💰 اقتصادي': ['fed', 'inflation', 'rate', 'dollar', 'recession', 'economy'],
    '🔒 أمني': ['hack', 'breach', 'scam', 'theft', 'exploit'],
    '📡 تقني': ['upgrade', 'network', 'protocol', 'layer2', 'mainnet']
}

def extract_coins(text):
    text_lower = text.lower()
    found = []
    for coin, keywords in COINS.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(coin)
                break
    return found if found else ['عام']

def detect_category(text):
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return '🌐 عام'

def analyze_sentiment(text):
    text_lower = text.lower()
    positive = ['surge', 'pump', 'bull', 'gain', 'up', 'positive']
    negative = ['crash', 'dump', 'bear', 'down', 'loss', 'negative']
    score = sum(1 for w in positive if w in text_lower) - sum(1 for w in negative if w in text_lower)
    if score > 0:
        return '🟢 إيجابي'
    elif score < 0:
        return '🔴 سلبي'
    return '⚪ محايد'

def get_importance(text):
    score = 5
    high_impact = ['sec', 'fed', 'hack', 'lawsuit', 'emergency', 'breaking']
    for w in high_impact:
        if w in text.lower():
            score += 3
    return min(score, 10)

def analyze_news(title):
    # ترجمة العنوان للعربية
    title_ar = translate_to_arabic(title)
    
    return {
        'title_ar': title_ar,           # العنوان بالعربية
        'title_en': title,               # العنوان الأصلي
        'coins': extract_coins(title),
        'category': detect_category(title),
        'sentiment': analyze_sentiment(title),
        'importance': get_importance(title)
    }
