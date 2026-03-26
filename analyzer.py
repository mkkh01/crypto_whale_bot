import requests

# تقييم المصادر (مصداقية وتأثير)
SOURCE_IMPORTANCE = {
    "bloomberg.com": 9,
    "reuters.com": 9,
    "ft.com": 8,
    "wsj.com": 8,
    "federalreserve.gov": 10,
    "sec.gov": 10,
    "cointelegraph.com": 6,
    "decrypt.co": 5,
}

# كلمات تدل على أهمية قصوى
CRITICAL_WORDS = [
    "emergency", "breaking", "urgent", "lawsuit", "hack", "crash",
    "collapse", "default", "war", "attack", "ban", "sanctions"
]

def translate_to_arabic(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {'client': 'gtx', 'sl': 'en', 'tl': 'ar', 'dt': 't', 'q': text}
        r = requests.get(url, params=params, timeout=5)
        return r.json()[0][0][0]
    except:
        return text

def extract_coins(text):
    text_lower = text.lower()
    coins = []
    if any(w in text_lower for w in ["bitcoin", "btc"]): coins.append("BTC")
    if any(w in text_lower for w in ["ethereum", "eth"]): coins.append("ETH")
    if any(w in text_lower for w in ["solana", "sol"]): coins.append("SOL")
    if any(w in text_lower for w in ["binance", "bnb"]): coins.append("BNB")
    return coins if coins else ["عام"]

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

def get_importance(title, source):
    # الأساس 5
    importance = 5
    # إضافة حسب المصدر
    src_key = source.replace("www.", "")
    importance += SOURCE_IMPORTANCE.get(src_key, 0) // 2  # مثلاً 5+4=9
    # إضافة حسب الكلمات الحرجة
    title_lower = title.lower()
    for word in CRITICAL_WORDS:
        if word in title_lower:
            importance += 3
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

def analyze_news(title, source):
    title_ar = translate_to_arabic(title)
    importance = get_importance(title, source)
    return {
        'title_ar': title_ar,
        'title_en': title,
        'coins': extract_coins(title),
        'category': detect_category(title),
        'sentiment': analyze_sentiment(title),
        'importance': importance,
    }
