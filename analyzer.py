"""
═══════════════════════════════════════════════════════════
   وحدة التحليل - Analyzer (مترجم جوجل التلقائي الذكي)
═══════════════════════════════════════════════════════════
"""

import re
import logging
from typing import Dict, List, Tuple
from deep_translator import GoogleTranslator  # استيراد مترجم جوجل المجاني
from config import (
    CATEGORY_KEYWORDS,
    POSITIVE_WORDS,
    NEGATIVE_WORDS,
    HIGH_IMPACT_WORDS,
    CRYPTO_MAP,
    CRYPTO_EMOJIS,
)

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    
    def __init__(self):
        self.category_translations = {
            "⚖️ تنظيمي": "Regulatory",
            "📊 اقتصادي": "Economic",
            "🔒 أمني": "Security",
            "🌍 جيوسياسي": "Geopolitical",
            "💻 تقني": "Technical",
            "📈 سوقي": "Market",
            "📰 عام": "General",
        }
    
    def extract_cryptos(self, text: str) -> List[str]:
        text_lower = text.lower()
        found_cryptos = set()
        
        sorted_map = sorted(CRYPTO_MAP.items(), key=lambda x: -len(x[0]))
        for keyword, symbol in sorted_map:
            if keyword in text_lower:
                found_cryptos.add(symbol)
        
        if not found_cryptos and ("crypto" in text_lower or "blockchain" in text_lower):
            found_cryptos.add("CRYPTO")
        
        return sorted(list(found_cryptos))
    
    def classify_category(self, text: str) -> str:
        text_lower = text.lower()
        best_category = "📰 عام"
        best_score = 0
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for w in words if w in POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        
        if total == 0:
            return "neutral", 0.0
        
        score = (positive_count - negative_count) / total
        
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return sentiment, round(score, 2)
    
    def calculate_importance(self, text: str, source_priority: int) -> int:
        text_lower = text.lower()
        importance = 3
        importance += min(source_priority // 3, 3)
        
        high_impact_count = sum(1 for word in HIGH_IMPACT_WORDS if word in text_lower)
        importance += min(high_impact_count * 2, 4)
        
        major_cryptos = ["btc", "eth", "sol", "bnb"]
        for crypto in major_cryptos:
            if crypto in text_lower:
                importance += 1
                break
        
        if any(word in text_lower for word in ["billion", "million", "$", "trillion"]):
            importance += 1
        
        return min(importance, 10)
    
    def translate_title_ar(self, title: str) -> str:
        """ترجمة ذكية وسياقية باستخدام خدمة مترجم جوجل التلقائية"""
        try:
            # تنظيف العنوان بشكل بسيط قبل الإرسال للمترجم لضمان دقة أعلى
            clean_title = title.replace('|', ' - ').replace('  ', ' ').strip()
            translated = GoogleTranslator(source='en', target='ar').translate(clean_title)
            return translated
        except Exception as e:
            logger.error(f"⚠️ فشل الاتصال بمترجم جوجل، تم اعتماد العنوان الأصلي: {e}")
            return title
    
    def analyze(self, news: Dict) -> Dict:
        full_text = news["title"] + " " + news.get("description", "")
        
        cryptos = self.extract_cryptos(full_text)
        category = self.classify_category(full_text)
        sentiment, sentiment_score = self.analyze_sentiment(full_text)
        importance = self.calculate_importance(full_text, news["source_priority"])
        title_ar = self.translate_title_ar(news["title"])
        
        sentiment_emojis = {
            "positive": "🟢",
            "negative": "🔴",
            "neutral": "⚪"
        }
        
        crypto_display = []
        for c in cryptos:
            emoji = CRYPTO_EMOJIS.get(c, "🪙")
            crypto_display.append(f"{emoji}{c}")
        
        return {
            "id": news["id"],
            "title_en": news["title"],
            "title_ar": title_ar,
            "link": news["link"],
            "source": news["source"],
            "pub_date": news.get("pub_date", ""),
            "cryptos": cryptos,
            "crypto_display": " | ".join(crypto_display) if crypto_display else "🪙 CRYPTO",
            "category": category,
            "category_en": self.category_translations.get(category, "General"),
            "sentiment": sentiment,
            "sentiment_emoji": sentiment_emojis.get(sentiment, "⚪"),
            "sentiment_score": sentiment_score,
            "importance": importance,
            "importance_stars": "⭐" * importance + "☆" * (10 - importance),
        }


analyzer = NewsAnalyzer()
