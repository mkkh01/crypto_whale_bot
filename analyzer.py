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

def extract_coins(text):
    text_lower = text.lower()
    coins = []
    if 'bitcoin' in text_lower or 'btc' in text_lower:
        coins.append('BTC')
    if 'ethereum' in text_lower or 'eth' in text_lower:
        coins.append('ETH')
    if 'solana' in text_lower or 'sol' in text_lower:
        coins.append('SOL')
    if 'binance' in text_lower or 'bnb' in text_lower:
        coins.append('BNB')
    return coins if coins else ['عام']

def detect_category(text):
    text_lower = text.lower()
    if 'sec' in text_lower or 'regulation' in text_lower or 'lawsuit' in text_lower:
        return '🏛️ تنظيمي'
    if 'fed' in text_lower or 'inflation' in text_lower or 'rate' in text_lower:
        return '💰 اقتصادي'
    if 'hack' in text_lower or 'breach' in text_lower or 'scam' in text_lower:
        return '🔒 أمني'
    if 'upgrade' in text_lower or 'network' in text_lower:
        return '📡 تقني'
    return '🌐 عام'

def analyze_sentiment(text):
    text_lower = text.lower()
    positive = ['surge', 'pump', 'bull', 'gain', 'up', 'positive', 'rally']
    negative = ['crash', 'dump', 'bear', 'down', 'loss', 'negative', 'plunge']
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
            score += 2
    return min(score, 10)

def get_signal_explanation(signal, analysis):
    action = signal['action']
    coins = ', '.join(analysis['coins'])
    importance = analysis['importance']
    
    if 'بيع' in action:
        return (f"🔻 **لماذا؟**\n"
                f"• خبر سلبي بأهمية {importance}/10\n"
                f"• العملات المتأثرة: {coins}\n\n"
                f"📌 قلل المراكز، ضع أوامر وقف خسارة.")
    elif 'شراء' in action:
        return (f"🟢 **لماذا؟**\n"
                f"• خبر إيجابي بأهمية {importance}/10\n"
                f"• العملات المتأثرة: {coins}\n\n"
                f"📌 فرصة شراء، انتظر تأكيد السعر.")
    elif 'ترقب' in action:
        return (f"🟡 **لماذا؟**\n"
                f"• خبر متوسط الأهمية {importance}/10\n"
                f"• راقب السعر خلال الساعات القادمة.")
    else:
        return (f"⚪ **لماذا؟**\n"
                f"• خبر ضعيف الأهمية {importance}/10\n"
                f"• لا تأثير فوري، استمر بالمراقبة.")

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
