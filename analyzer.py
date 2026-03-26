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
    '🌍 جيوسياسي': ['war', 'iran', 'russia', 'china', 'sanctions', 'attack', 'crisis', 'conflict']
}

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
    positive = ['surge', 'pump', 'bull', 'gain', 'up', 'positive', 'soar', 'rally', '新高', 'ارتفع']
    negative = ['crash', 'dump', 'bear', 'down', 'loss', 'negative', 'plunge', 'slump', 'هبط', 'انخفض']
    score = sum(1 for w in positive if w in text_lower) - sum(1 for w in negative if w in text_lower)
    if score > 0:
        return '🟢 إيجابي'
    elif score < 0:
        return '🔴 سلبي'
    return '⚪ محايد'

def get_importance(text):
    text_lower = text.lower()
    score = 3
    
    for word in IMPACT_WORDS['catastrophic']:
        if word in text_lower:
            score += 5
    for word in IMPACT_WORDS['very_high']:
        if word in text_lower:
            score += 4
    for word in IMPACT_WORDS['high']:
        if word in text_lower:
            score += 3
    for word in IMPACT_WORDS['medium']:
        if word in text_lower:
            score += 2
    for word in IMPACT_WORDS['low']:
        if word in text_lower:
            score += 1
    
    return min(score, 10)

def get_signal_explanation(signal, analysis):
    """
    إرجاع تفسير مفصل للإشارة
    """
    action = signal['action']
    sentiment = analysis['sentiment']
    category = analysis['category']
    coins = ', '.join(analysis['coins'])
    importance = analysis['importance']
    
    if 'بيع' in action:
        return (f"🔻 **لماذا نبيع/نتجنب؟**\n\n"
                f"• الخبر {sentiment} في مجال {category}\n"
                f"• التأثير المتوقع: {importance}/10 (قوي)\n"
                f"• العملات المتأثرة: {coins}\n\n"
                f"📌 **التوصية:** تقليل المراكز في {coins}، وضع أوامر وقف خسارة، تجنب الدخول بصفقات شراء جديدة حتى يتضح الموقف.")
    
    elif 'شراء' in action:
        return (f"🟢 **لماذا نشتري؟**\n\n"
                f"• الخبر {sentiment} في مجال {category}\n"
                f"• التأثير المتوقع: {importance}/10 (قوي)\n"
                f"• العملات المتأثرة: {coins}\n\n"
                f"📌 **التوصية:** فرصة شراء محتملة، انتظر تأكيد السعر ثم دخول تدريجي، حدد وقف خسارة 3-5%.")
    
    elif 'ترقب' in action:
        return (f"🟡 **لماذا نترقب؟**\n\n"
                f"• الخبر {sentiment} في مجال {category}\n"
                f"• التأثير المتوقع: {importance}/10 (متوسط)\n"
                f"• العملات المتأثرة: {coins}\n\n"
                f"📌 **التوصية:** راقب السعر خلال الساعات القادمة، لا تدخل صفقات جديدة، انتظر تأكيد الاتجاه.")
    
    else:
        return (f"⚪ **لماذا نراقب فقط؟**\n\n"
                f"• الخبر {sentiment} في مجال {category}\n"
                f"• التأثير المتوقع: {importance}/10 (ضعيف)\n\n"
                f"📌 **التوصية:** لا تأثير فوري، استمر في مراقبة السوق بشكل عام.")

def analyze_news(title):
    title_ar = translate_to_arabic(title)
    
    return {
        'title_ar': title_ar,
        'title_en': title,
        'coins': extract_coins(title),
        'category': detect_category(title),
        'sentiment': analyze_sentiment(title),
        'importance': get_importance(title)
    }
