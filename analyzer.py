import requests

def translate_to_arabic(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {'client': 'gtx', 'sl': 'en', 'tl': 'ar', 'dt': 't', 'q': text}
        r = requests.get(url, params=params, timeout=5)
        return r.json()[0][0][0]
    except:
        return text

def extract_coins(news):
    """تستقبل كائن الخبر وتعيد قائمة العملات المستخرجة منه"""
    return news.get('coins', ['عام'])

def detect_category(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["sec", "regulation", "lawsuit", "ban"]):
        return "🏛️ تنظيمي"
    if any(w in text_lower for w in ["fed", "inflation", "rate", "recession"]):
        return "💰 اقتصادي"
    if any(w in text_lower for w in ["hack", "breach", "scam"]):
        return "🔒 أمني"
    if any(w in text_lower for w in ["war", "sanctions", "attack"]):
        return "🌍 جيوسياسي"
    return "🌐 عام"

def analyze_sentiment(text):
    text_lower = text.lower()
    pos = ["surge", "pump", "bull", "gain", "up", "rally"]
    neg = ["crash", "dump", "bear", "down", "loss", "plunge"]
    score = sum(1 for w in pos if w in text_lower) - sum(1 for w in neg if w in text_lower)
    if score > 0: return "🟢 إيجابي"
    if score < 0: return "🔴 سلبي"
    return "⚪ محايد"

def get_importance(title):
    importance = 5
    high_impact = ["sec", "fed", "hack", "lawsuit", "emergency", "breaking", "crash", "surge"]
    for w in high_impact:
        if w in title.lower():
            importance += 2
    return min(importance, 10)

def get_signal_explanation(signal, analysis):
    action = signal['action']
    coins = ', '.join(analysis['coins'])
    importance = analysis['importance']
    if 'بيع' in action:
        return (f"🔻 **لماذا؟**\n• خبر سلبي بأهمية {importance}/10\n• العملات: {coins}\n\n📌 قلل المراكز، ضع وقف خسارة.")
    elif 'شراء' in action:
        return (f"🟢 **لماذا؟**\n• خبر إيجابي بأهمية {importance}/10\n• العملات: {coins}\n\n📌 فرصة شراء، انتظر تأكيد السعر.")
    elif 'ترقب' in action:
        return (f"🟡 **لماذا؟**\n• خبر متوسط الأهمية {importance}/10\n• راقب السعر خلال الساعات القادمة.")
    else:
        return (f"⚪ **لماذا؟**\n• خبر ضعيف الأهمية {importance}/10\n• لا تأثير فوري.")

def analyze_news(title, coins):
    title_ar = translate_to_arabic(title)
    return {
        'title_ar': title_ar,
        'title_en': title,
        'coins': coins,
        'category': detect_category(title),
        'sentiment': analyze_sentiment(title),
        'importance': get_importance(title)
    }
