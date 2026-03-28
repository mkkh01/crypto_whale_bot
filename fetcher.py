"""
═══════════════════════════════════════════════════════════
   وحدة جلب الأخبار - Fetcher
═══════════════════════════════════════════════════════════
تجلب الأخبار من مصادر RSS وتقوم بالتصفية الأولية
"""

import re
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from config import (
    RSS_SOURCES, 
    FILTER_KEYWORDS, 
    REQUEST_TIMEOUT
)


class NewsFetcher:
    """فئة لجلب الأخبار من مصادر RSS"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _generate_id(self, title: str, link: str) -> str:
        """توليد معرف فريد للخبر"""
        unique_string = f"{title}:{link}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def _parse_rss(self, xml_content: str, source_name: str, source_info: Dict) -> List[Dict]:
        """تحليل محتوى RSS واستخراج الأخبار"""
        news_list = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # البحث عن عناصر الأخبار (قد تكون item أو entry)
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:15]:  # آخر 15 خبر من كل مصدر
                try:
                    # استخراج العنوان
                    title_elem = (
                        item.find('title') or 
                        item.find('{http://www.w3.org/2005/Atom}title')
                    )
                    title = title_elem.text if title_elem is not None else ""
                    
                    # استخراج الرابط
                    link_elem = (
                        item.find('link') or 
                        item.find('{http://www.w3.org/2005/Atom}link')
                    )
                    if link_elem is not None:
                        link = link_elem.text if link_elem.text else link_elem.get('href', '')
                    else:
                        link = ""
                    
                    # استخراج التاريخ
                    date_elem = (
                        item.find('pubDate') or 
                        item.find('{http://www.w3.org/2005/Atom}published') or
                        item.find('{http://www.w3.org/2005/Atom}updated')
                    )
                    pub_date = date_elem.text if date_elem is not None else ""
                    
                    # استخراج الوصف
                    desc_elem = (
                        item.find('description') or 
                        item.find('{http://www.w3.org/2005/Atom}summary')
                    )
                    description = desc_elem.text if desc_elem is not None else ""
                    
                    if title and link:
                        news_list.append({
                            "id": self._generate_id(title, link),
                            "title": title.strip(),
                            "link": link.strip(),
                            "description": self._clean_html(description) if description else "",
                            "pub_date": pub_date,
                            "source": source_name,
                            "source_priority": source_info.get("priority", 5),
                            "source_category": source_info.get("category", "general"),
                        })
                except Exception as e:
                    continue
                    
        except ET.ParseError as e:
            print(f"⚠️ خطأ في تحليل RSS من {source_name}: {e}")
        except Exception as e:
            print(f"⚠️ خطأ غير متوقع في {source_name}: {e}")
        
        return news_list
    
    def _clean_html(self, text: str) -> str:
        """إزالة أكواد HTML من النص"""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'&[^;]+;', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean[:200]  # اقتطاع الوصف
    
    def _passes_filter(self, title: str, description: str) -> bool:
        """التحقق مما إذا كان الخبر يمرر التصفية الأولية"""
        combined_text = (title + " " + description).lower()
        
        for keyword in FILTER_KEYWORDS:
            if keyword in combined_text:
                return True
        
        return False
    
    def fetch_from_source(self, source_name: str, source_info: Dict) -> List[Dict]:
        """جلب الأخبار من مصدر واحد"""
        news_list = []
        
        try:
            response = self.session.get(
                source_info["url"],
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                raw_news = self._parse_rss(response.text, source_name, source_info)
                
                # تطبيق التصفية الأولية
                for news in raw_news:
                    if self._passes_filter(news["title"], news["description"]):
                        news_list.append(news)
                        
        except requests.exceptions.Timeout:
            print(f"⏱️ انتهت مهلة الاتصال بـ {source_name}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ خطأ في الاتصال بـ {source_name}: {e}")
        except Exception as e:
            print(f"⚠️ خطأ في جلب {source_name}: {e}")
        
        return news_list
    
    def fetch_all(self) -> List[Dict]:
        """جلب الأخبار من جميع المصادر"""
        all_news = []
        
        for source_name, source_info in RSS_SOURCES.items():
            news = self.fetch_from_source(source_name, source_info)
            all_news.extend(news)
        
        # ترتيب حسب الأولوية ثم حسب المصدر
        all_news.sort(key=lambda x: (-x["source_priority"], x["source"]))
        
        return all_news


# إنشاء نسخة واحدة من الجالب
fetcher = NewsFetcher()
