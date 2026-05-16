"""
═══════════════════════════════════════════════════════════
   وحدة التحليل - Analyzer (قاموس أبسط محسّن)
═══════════════════════════════════════════════════════════
"""

import re
import logging
from typing import Dict, List, Tuple
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
        """ترجمة أبسط محسّن"""
        words = title.replace('-', ' ').replace('|', ' ').replace(':', ' ').replace('"', '').replace("'", "").split()
        
        word_map = {
            # عملات
            "bitcoin": "بيتكوين", "ethereum": "إيثريوم", "solana": "سولانا",
            "binance": "بينانس", "coinbase": "كوينبيس", "ripple": "ريبل",
            "cardano": "كاردانو", "dogecoin": "دوجكوين",
            "polkadot": "بولكادوت", "chainlink": "شينلينك",
            "litecoin": "لايتكوين", "polygon": "بوليجون",
            "avalanche": "أفالانش", "uniswap": "يونيسواب",
            "sec": "هيئة الأوراق المالية", "fed": "الفيدرالي",
            
            # أحداث وأفعال
            "dips": "ينخفض", "dip": "ينخفض",
            "surges": "ارتفاع حاد", "surge": "ارتفاع حاد",
            "soars": "يقفز", "soar": "قفزة",
            "drops": "انخفاض", "drop": "انخفاض",
            "plunges": "انهار", "plunge": "انهيار",
            "crashes": "انهيار", "crash": "انهيار",
            "pumps": "صعود مفاجئ", "pump": "صعود مفاجئ",
            "dumps": "هبوط حاد", "dump": "هبوط",
            "rallies": "تقدم", "rally": "تقدم",
            "breaks": "يخترق",
            "reaches": "يصل إلى",
            "falls": "يسقط",
            "rises": "يرتفع",
            "climbs": "يتسلق",
            "jumps": "يقفز",
            "gains": "يربح",
            "loses": "خاسر",
            "expects": "يتوقع",
            "confirms": "يؤكد",
            "reveals": "يكشف",
            "announces": "يعلن",
            "warns": "يحذر",
            "rejects": "يرفض",
            "approves": "يوافق",
            "banned": "ممنوع",
            "launched": "أُطلق",
            "listed": "إدراج",
            "delisted": "إزالة من القائمة",
            "surges": "ارتفاعات",
            "trading": "تداول",
            "investors": "المستثمرون",
            "analyst": "محلل",
            "price": "السعر",
            "market": "السوق",
            "below": "أقل من",
            "above": "أعلى من",
            "after": "بعد",
            "despite": "رغم",
            "without": "بدون",
            "against": "ضد",
            "between": "بين",
            "according to": "وفقاً لـ",
            "reported": "أُبلّغ عن",
            "says": "يقول",
            "will": "سوف",
            "could": "يمكن",
            "has": "لديه",
            "was": "كان",
            "is": "هو",
            "are": "هم",
            "been": "كان",
            "with": "مع",
            "from": "من",
            "that": "أن",
            "this": "هذا",
            "which": "الذي",
            "more": "المزيد من",
            "also": "أيضاً",
            "just": "فقط",
            "not": "ليس",
            "but": "لكن",
            "very": "جداً",
            "most": "معظم",
            "some": "بعض",
            "how": "كيف",
            "why": "لماذا",
            "what": "ماذا",
            "when": "متى",
            "where": "أين",
            "who": "من",
            "new": "جديد",
            "first": "الأول",
            "next": "التالي",
            "another": "آخر",
            "major": "كبير",
            "high": "مرتفع",
            "low": "منخفض",
            "now": "الآن",
            "today": "اليوم",
            "week": "الأسبوع",
            "month": "الشهر",
            "year": "السنة",
            "million": "مليون",
            "billion": "مليار",
            "trillion": "تريليون",
            "percent": "بالمئة",
            "levels": "مستويات",
            "resistance": "مقاومة",
            "support": "دعم",
            "volume": "حجم التداول",
            "whale": "حوت",
            "institutional": "مؤسسي",
            "retail": "تجزء",
            "fear": "خوف",
            "greed": "طمع",
            "manipulation": "تلاعب",
            "smart": "ذكي",
            "contract": "عقد",
            "layer": "طبقة",
            "defi": "ديفاي",
            "nft": "إن إف تي",
            "etf": "صندوق متداول",
            "halving": "تنصيف",
            "regulation": "تنظيم",
            "compliance": "امتثال",
            "innovation": "ابتكار",
            "technology": "تقنية",
            "development": "تطوير",
            "community": "مجتمع",
            "ecosystem": "نظام بيئي",
            "adoption": "اعتماد",
            "integration": "دمج",
            "partnership": "شراكة",
            "milestone": "إنجاز",
            "update": "تحديث",
            "upgrade": "ترقية",
            "release": "إصدار",
            "version": "إصدار",
            "hack": "اختراق",
            "exploit": "ثغرة",
            "security": "أمني",
            "breach": "اختراق",
            "vulnerability": "ثغرة أمنية",
            "scam": "احتيال",
            "fraud": "احتيال",
            "theft": "سرقة",
            "lawsuit": "دعوى قضائية",
            "investigation": "تحقيق",
            "fine": "غرامة",
            "penalty": "عقوبة",
            "warning": "تحذير",
            "suspicious": "مشبوه",
            "illegal": "غير قانوني",
            "legal": "قانوني",
            "bullish": "صعودي",
            "bearish": "هبوطي",
            "volatile": "متقلب",
            "stable": "مستقر",
            "profit": "ربح",
            "loss": "خسارة",
            "risk": "مخاطرة",
            "opportunity": "فرصة",
            "threat": "تهديد",
            "challenge": "تحدي",
            "solution": "حل",
            "problem": "مشكلة",
            "reason": "سبب",
            "result": "نتيجة",
            "impact": "تأثير",
            "effect": "تأثير",
            "cause": "سبب",
            "concern": "قلق",
            "crisis": "أزمة",
            "recovery": "تعافي",
            "decline": "انخفاض",
            "growth": "نمو",
            "improvement": "تحسين",
            "setback": "تراجع",
            "progress": "تقدم",
            "success": "نجاح",
            "failure": "فشل",
        }
        
        translated = []
        for word in words:
            word_lower = word.lower().strip('.,!?()[]{}"\'')
            clean_word = word.strip('.,!?()[]{}"\'')
            if word_lower in word_map:
                if word_map[word_lower]:
                    translated.append(word_map[word_lower])
            else:
                translated.append(clean_word)
        
        result = " ".join(translated)
        return result
    
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