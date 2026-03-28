"""
═══════════════════════════════════════════════════════════
   وحدة التحليل - Analyzer
═══════════════════════════════════════════════════════════
تحلل الخبر وتستخرج: العملات، التصنيف، المشاعر، الأهمية
"""

import re
from typing import Dict, List, Tuple
from config import (
    CATEGORY_KEYWORDS,
    POSITIVE_WORDS,
    NEGATIVE_WORDS,
    HIGH_IMPACT_WORDS,
    CRYPTO_MAP,
    CRYPTO_EMOJIS,
)


class NewsAnalyzer:
    """فئة لتحليل الأخبار"""
    
    def __init__(self):
        # ترجمة بسيطة لبعض المصطلحات الشائعة
        self.category_translations = {
            "⚖️ تنظيمي": "Regulatory",
            "📊 اقتصادي": "Economic",
            "🔒 أمني": "Security",
            "🌍 جيوسياسي": "Geopolitical",
            "💻 تقني": "Technical",
            "📈 سوقي": "Market",
        }
    
    def extract_cryptos(self, text: str) -> List[str]:
        """استخراج العملات المذكورة في النص"""
        text_lower = text.lower()
        found_cryptos = set()
        
        # ترتيب حسب طول الكلمة (للتطابق الأدق)
        sorted_map = sorted(CRYPTO_MAP.items(), key=lambda x: -len(x[0]))
        
        for keyword, symbol in sorted_map:
            if keyword in text_lower:
                found_cryptos.add(symbol)
        
        # إذا لم يتم العثور على عملات، أضف CRYPTO كتصنيف عام
        if not found_cryptos and ("crypto" in text_lower or "blockchain" in text_lower):
            found_cryptos.add("CRYPTO")
        
        return sorted(list(found_cryptos))
    
    def classify_category(self, text: str) -> str:
        """تصنيف الخبر بناءً على الكلمات المفتاحية"""
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
        """تحليل مشاعر الخبر"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for w in words if w in POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        
        if total == 0:
            return "neutral", 0.0
        
        # حساب النتيجة (-1 إلى +1)
        score = (positive_count - negative_count) / total
        
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return sentiment, round(score, 2)
    
    def calculate_importance(self, text: str, source_priority: int) -> int:
        """حساب أهمية الخبر (1-10)"""
        text_lower = text.lower()
        importance = 3  # القيمة الأساسية
        
        # إضافة نقاط حسب أولوية المصدر
        importance += min(source_priority // 3, 3)
        
        # إضافة نقاط للكلمات عالية التأثير
        high_impact_count = sum(1 for word in HIGH_IMPACT_WORDS if word in text_lower)
        importance += min(high_impact_count * 2, 4)
        
        # تحديد إذا كان الخبر يتحدث عن عملات رئيسية
        major_cryptos = ["btc", "eth", "sol", "bnb"]
        for crypto in major_cryptos:
            if crypto in text_lower:
                importance += 1
                break
        
        # تحديد إذا كان يتضمن أرقام كبيرة (مليارات، ملايين)
        if any(word in text_lower for word in ["billion", "million", "$", "trillion"]):
            importance += 1
        
        # الحد الأقصى 10
        return min(importance, 10)
    
    def translate_title_ar(self, title: str) -> str:
        """
        ترجمة مبسطة للعنوان (بدون API خارجي)
        تستخدم قاموس بسيط للمصطلحات الشائعة
        """
        translations = {
            # عملات
            "Bitcoin": "بيتكوين", "Ethereum": "إيثريوم", "Solana": "سولانا",
            "BNB": "بي إن بي", "XRP": "ريبل", "Cardano": "كاردانو",
            "Dogecoin": "دوجكوين", "Polygon": "بوليجون", "Avalanche": "أفالانش",
            "Polkadot": "بولكادوت", "Chainlink": "شينلينك", "Litecoin": "لايتكوين",
            
            # أحداث
            "Hack": "اختراق", "Exploit": "ثغرة", "Breach": "اختراق",
            "Lawsuit": "دعوى قضائية", "Ban": "حظر", "Approve": "موافقة",
            "Reject": "رفض", "ETF": "صندوق متداول", "Halving": "تنصيف",
            "Fork": "تفرع", "Upgrade": "تحديث", "Airdrop": "توزيع مجاني",
            "Staking": "ستيكنج", "Mining": "تعدين",
            
            # جهات
            "SEC": "هيئة الأوراق المالية", "Federal Reserve": "الاحتياطي الفيدرالي",
            "Fed": "الفيدرالي", "Binance": "بينانس", "Coinbase": "كوينبيس",
            
            # مصطلحات سوق
            "Surge": "ارتفاع حاد", "Crash": "انهيار", "Pump": "صعود",
            "Dump": "هبوط", "Bull": "صعودي", "Bear": "هبوطي",
            "Rally": "تقدم", "Plunge": "انخفاض حاد", "Soar": "قفزة",
            "Slump": "ركود", "Recovery": "تعافي",
            
            # أخرى
            "Price": "السعر", "Market": "السوق", "Trading": "التداول",
            "Investor": "المستثمر", "Regulation": "تنظيم", "Crypto": "كريبتو",
            "Blockchain": "بلوكشين", "DeFi": "ديفاي", "NFT": "إن إف تي",
        }
        
        translated = title
        for en, ar in sorted(translations.items(), key=lambda x: -len(x[0])):
            translated = translated.replace(en, ar)
        
        return translated
    
    def analyze(self, news: Dict) -> Dict:
        """تحليل خبر واحد بالكامل"""
        full_text = news["title"] + " " + news["description"]
        
        # استخراج العملات
        cryptos = self.extract_cryptos(full_text)
        
        # تصنيف الخبر
        category = self.classify_category(full_text)
        
        # تحليل المشاعر
        sentiment, sentiment_score = self.analyze_sentiment(full_text)
        
        # حساب الأهمية
        importance = self.calculate_importance(full_text, news["source_priority"])
        
        # ترجمة العنوان
        title_ar = self.translate_title_ar(news["title"])
        
        # أيقونات المشاعر
        sentiment_emojis = {
            "positive": "🟢",
            "negative": "🔴",
            "neutral": "⚪"
        }
        
        # أيقونات العملات
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
            "pub_date": news["pub_date"],
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


# إنشاء نسخة واحدة من المحلل
analyzer = NewsAnalyzer()
