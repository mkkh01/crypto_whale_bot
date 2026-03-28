"""
═══════════════════════════════════════════════════════════
   وحدة التخزين - منع إرسال الخبر أكثر من مرة
═══════════════════════════════════════════════════════════
"""

import json
import os
from datetime import datetime, timedelta
from config import SENT_NEWS_FILE


class NewsStorage:
    """فئة لإدارة تخزين معرفات الأخبار المرسلة"""
    
    def __init__(self):
        self.file_path = SENT_NEWS_FILE
        self.sent_ids = self._load()
    
    def _load(self) -> set:
        """تحميل المعرفات المحفوظة من الملف"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # تحويل إلى set مع التحقق من الصلاحية
                    valid_ids = set()
                    for item in data:
                        # إزالة المعرفات القديمة (أقدم من 24 ساعة)
                        timestamp = item.get("timestamp", 0)
                        if timestamp:
                            try:
                                sent_time = datetime.fromtimestamp(timestamp)
                                if datetime.now() - sent_time < timedelta(hours=24):
                                    valid_ids.add(item["id"])
                            except:
                                pass
                    return valid_ids
        except Exception as e:
            print(f"⚠️ خطأ في تحميل التخزين: {e}")
        return set()
    
    def _save(self):
        """حفظ المعرفات في الملف"""
        try:
            data = [
                {"id": news_id, "timestamp": datetime.now().timestamp()}
                for news_id in self.sent_ids
            ]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ التخزين: {e}")
    
    def is_sent(self, news_id: str) -> bool:
        """التحقق مما إذا كان الخبر قد أُرسل مسبقاً"""
        return news_id in self.sent_ids
    
    def mark_as_sent(self, news_id: str):
        """وضع علامة على الخبر كمرسل"""
        self.sent_ids.add(news_id)
        self._save()
    
    def get_count(self) -> int:
        """الحصول على عدد الأخبار المحفوظة"""
        return len(self.sent_ids)
    
    def clear_all(self) -> int:
        """مسح جميع المعرفات (للأمر /reset)"""
        count = len(self.sent_ids)
        self.sent_ids.clear()
        self._save()
        return count


# إنشاء نسخة واحدة من التخزين (Singleton)
storage = NewsStorage()
