"""
═══════════════════════════════════════════════════════════
   وحدة توليد الإشارات - Signal Generator
═══════════════════════════════════════════════════════════
تنتج إشارة تداول بناءً على نتائج التحليل
"""

from typing import Dict, Tuple


class SignalGenerator:
    """فئة لتوليد إشارات التداول"""
    
    # قواعد الإشارات
    SIGNAL_RULES = {
        "شراء": {
            "conditions": [
                ("sentiment", "positive"),
                ("importance_min", 7),
            ],
            "boosters": [
                ("category", "📈 سوقي"),
                ("category", "💻 تقني"),
                ("has_crypto", True),
            ],
            "base_confidence": 60,
            "max_confidence": 95,
            "emoji": "🟢",
        },
        "بيع": {
            "conditions": [
                ("sentiment", "negative"),
                ("importance_min", 7),
            ],
            "boosters": [
                ("category", "🔒 أمني"),
                ("category", "⚖️ تنظيمي"),
                ("has_crypto", True),
            ],
            "base_confidence": 60,
            "max_confidence": 95,
            "emoji": "🔴",
        },
    }
    
    def _check_conditions(self, analysis: Dict, conditions: list) -> bool:
        """التحقق من الشروط الأساسية"""
        for condition in conditions:
            key, value = condition
            if key == "sentiment":
                if analysis["sentiment"] != value:
                    return False
            elif key == "importance_min":
                if analysis["importance"] < value:
                    return False
        return True
    
    def _calculate_boost(self, analysis: Dict, boosters: list) -> int:
        """حساب نسبة زيادة الثقة"""
        boost = 0
        for booster in boosters:
            key, value = booster
            if key == "category" and analysis["category"] == value:
                boost += 8
            elif key == "has_crypto" and value and len(analysis["cryptos"]) > 0:
                boost += 5
        return boost
    
    def _get_reason(self, signal: str, analysis: Dict) -> str:
        """توليد سبب مبسط للإشارة"""
        reasons = []
        
        # سبب المشاعر
        sentiment_reasons = {
            "positive": "مشاعر إيجابية",
            "negative": "مشاعر سلبية",
            "neutral": "مشاعر محايدة"
        }
        reasons.append(sentiment_reasons.get(analysis["sentiment"], ""))
        
        # سبب التصنيف
        category_reasons = {
            "⚖️ تنظيمي": "تطور تنظيمي",
            "📊 اقتصادي": "تطور اقتصادي",
            "🔒 أمني": "حدث أمني",
            "🌍 جيوسياسي": "تطور جيوسياسي",
            "💻 تقني": "تطور تقني",
            "📈 سوقي": "حركة سوقية",
        }
        reasons.append(category_reasons.get(analysis["category"], ""))
        
        # سبب الأهمية
        if analysis["importance"] >= 9:
            reasons.append("أهمية قصوى")
        elif analysis["importance"] >= 7:
            reasons.append("أهمية عالية")
        
        # تصفية الأسباب الفارغة
        reasons = [r for r in reasons if r]
        
        return "، ".join(reasons[:3])
    
    def generate(self, analysis: Dict) -> Dict:
        """توليد إشارة التداول"""
        
        # محاولة إيجاد إشارة شراء أو بيع
        for signal_name, rules in self.SIGNAL_RULES.items():
            if self._check_conditions(analysis, rules["conditions"]):
                boost = self._calculate_boost(analysis, rules["boosters"])
                confidence = min(rules["base_confidence"] + boost, rules["max_confidence"])
                
                return {
                    "signal": signal_name,
                    "emoji": rules["emoji"],
                    "confidence": confidence,
                    "reason": self._get_reason(signal_name, analysis),
                    "action": "🚀 فوري" if confidence >= 85 else "⏱️ متابعة",
                }
        
        # إذا لم تتحقق شروط الشراء أو البيع
        if analysis["importance"] >= 7:
            if analysis["sentiment"] == "neutral":
                return {
                    "signal": "ترقب",
                    "emoji": "🟡",
                    "confidence": 50,
                    "reason": "مشاعر محايدة مع أهمية عالية",
                    "action": "👀 مراقبة",
                }
            else:
                return {
                    "signal": "مراقبة",
                    "emoji": "👁️",
                    "confidence": 45,
                    "reason": self._get_reason("مراقبة", analysis),
                    "action": "📊 تحليل إضافي",
                }
        
        # أخبار أقل أهمية
        return {
            "signal": "ترقب",
            "emoji": "⚪",
            "confidence": 30,
            "reason": "أهمية متوسطة",
            "action": "📝 تسجيل",
        }


# إنشاء نسخة واحدة من مولد الإشارات
signal_generator = SignalGenerator()
