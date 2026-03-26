def generate_signal(analysis, news):
    importance = analysis['importance']
    sentiment = analysis['sentiment']
    category = analysis['category']
    
    confidence = importance * 8
    
    if '🟢' in sentiment and importance >= 6:
        action = "شراء"
        emoji = "🟢🚀"
        reason = f"خبر إيجابي قوي في {category} بأهمية {importance}/10"
    elif '🔴' in sentiment and importance >= 6:
        action = "بيع/تجنب"
        emoji = "🔴⚠️"
        reason = f"خبر سلبي قوي في {category} بأهمية {importance}/10"
    elif '🟢' in sentiment and importance >= 4:
        action = "ترقب إيجابي"
        emoji = "🟡👀"
        reason = f"خبر إيجابي متوسط، راقب السعر"
    elif '🔴' in sentiment and importance >= 4:
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
