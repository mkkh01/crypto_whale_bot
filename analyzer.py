import re
import requests

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
    '🏛️ تنظيمي': ['sec', 'regulation', 'law', 'ban', 'legal', 'congress', 'senate', 'lawsuit'],
    '💰 اقتصادي': ['fed', 'inflation', 'rate', 'dollar', 'recession', 'economy', 'interest', 'jobs'],
    '🔒 أمني': ['hack', 'breach', 'scam', 'theft', 'exploit', 'vulnerability'],
    '📡 تقني': ['upgrade', 'network', 'protocol', 'layer2', 'mainnet', 'launch'],
    '🌍 جيوسياسي': ['war', 'iran', 'russia', 'china', 'sanctions', 'attack', 'crisis']
}

# نظام تقييم متطور
IMPACT_WORDS = {
    'catastrophic': ['war', 'nuclear', 'collapse', 'emergency', 'bank run', 'default'],
    'very_high': ['sec', 'fed', 'lawsuit', 'hack', 'ban', 'critical'],
    'high': ['regulation', 'inflation', 'recession', 'crash', 'surge', 'pump'],
    'medium': ['etf', 'rate cut', 'partnership', 'adoption', 'milestone'],
    'low': ['update', 'launch', 'event', 'conference', 'podcast']
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
    positive = ['surge', 'pump', 'bull', 'gain', 'up', 'positive', '新高', 'ارتفع', 'soar', 'rally']
    negative = ['crash', 'dump', 'bear', 'down', 'loss', 'negative', 'هبط', 'انخفض', 'plunge', 'slump']
    score = sum(1 for w in positive if w in text_lower) - sum(1 for w in negative if w in text_lower)
    if score > 0:
        return '🟢 إيجابي'
    elif score < 0:
        return '🔴 سلبي'
    return '⚪ محايد'

def get_importance(text):
    """
    حساب أهمية الخبر من 1 إلى 10
    """
    text_lower = text.lower()
    score = 3  # أساس أقل لظهور المزيد من الأخبار
    
    # كلمات كارثية
    for word in IMPACT_WORDS['catastrophic']:
        if word in text_lower:
            score += 5
    
    # كلمات عالية جداً
    for word in IMPACT_WORDS['very_high']:
        if word in text_lower:
            score += 4
    
    # كلمات عالية
    for word in IMPACT_WORDS['high']:
        if word in text_lower:
            score += 3
    
    # كلمات متوسطة
    for word in IMPACT_WORDS['medium']:
        if word in text_lower:
            score += 2
    
    # كلمات منخفضة
    for word in IMPACT_WORDS['low']:
        if word in text_lower:
            score += 1
    
    # حد أقصى 10
    return min(score, 10)

def analyze_news(title):
    title_ar = translate_to_arabic(title)
    
    return {
        'title_ar': title_ar,
        'title_en': title,
        'coins': extract_coins(title),
        'category': detect_category(title),
        'sentiment': analyze_sentiment(title),
        'importance': get_importance(title)  # الآن من 3 إلى 10
    }
    
