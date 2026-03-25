def generate_signal(analysis, news):
    importance = analysis['importance']
    sentiment = analysis['sentiment']
    category = analysis['category']
    
    confidence = importance * 7
    
    if '🟢' in sentiment and importance >= 7:
        action = "شراء"
        emoji = "🟢🚀"
        reason = f"خبر إيجابي قوي في {category} بأهمية {importance}/10"
    elif '🔴' in sentiment and importance >= 7:
        action = "بيع/تجنب"
        emoji = "🔴⚠️"
        reason = f"خبر سلبي قوي في {category} قد يضغط على السعر"
    elif '🟢' in sentiment and importance >= 5:
        action = "ترقب إيجابي"
        emoji = "🟡👀"
        reason = f"خبر إيجابي متوسط الأهمية، راقب السعر"
    elif '🔴' in sentiment and importance >= 5:
        action = "ترقب سلبي"
        emoji = "🟡👀"
        reason = f"خبر سلبي متوسط، كن حذراً"
    else:
        action = "مراقبة"
        emoji = "⚪📊"
        reason = "خبر محايد أو ضعيف، لا تأثير فوري"
    
    return {
        'action': action,
        'emoji': emoji,
        'confidence': min(confidence, 95),
        'reason': reason
    }
