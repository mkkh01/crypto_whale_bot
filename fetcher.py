"""
═══════════════════════════════════════════════════════════
   وحدة جلب الأخبار - Fetcher (بدون تصفية صارمة)
═══════════════════════════════════════════════════════════
"""

import re
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from config import (
    RSS_SOURCES,
    REQUEST_TIMEOUT,
)
import logging

logger = logging.getLogger(__name__)


class NewsFetcher:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def _generate_id(self, title: str, link: str) -> str:
        unique_string = f"{title}:{link}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def _parse_rss(self, xml_content: str, source_name: str, source_info: Dict) -> List[Dict]:
        news_list = []
        
        try:
            root = ET.fromstring(xml_content)
            
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:20]:
                try:
                    title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                    title = title_elem.text if title_elem is not None else ""
                    
                    link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                    if link_elem is not None:
                        link = link_elem.text if link_elem.text else link_elem.get('href', '')
                    else:
                        link = ""
                    
                    date_elem = (
                        item.find('pubDate') or 
                        item.find('{http://www.w3.org/2005/Atom}published') or
                        item.find('{http://www.w3.org/2005/Atom}updated')
                    )
                    pub_date = date_elem.text if date_elem is not None else ""
                    
                    desc_elem = item.find('description') or item.find('{http://www.w3.org/2005/Atom}summary')
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
                except Exception:
                    continue
                    
        except ET.ParseError as e:
            logger.warning(f"⚠️ خطأ تحليل XML من {source_name}: {e}")
        except Exception as e:
            logger.warning(f"⚠️ خطأ في {source_name}: {e}")
        
        return news_list
    
    def _clean_html(self, text: str) -> str:
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'&[^;]+;', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean[:300]
    
    def fetch_from_source(self, source_name: str, source_info: Dict) -> List[Dict]:
        news_list = []
        url = source_info["url"]
        
        try:
            logger.info(f"🔗 جاري جلب: {source_name}...")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            logger.info(f"📥 {source_name}: حالة {response.status_code}")
            
            if response.status_code == 200:
                raw_news = self._parse_rss(response.text, source_name, source_info)
                
                # تسجيل أول 3 عناوين للمراقبة
                for i, news in enumerate(raw_news[:3]):
                    logger.info(f"   📰 [{source_name}] {news['title'][:80]}")
                
                logger.info(f"✅ {source_name}: {len(raw_news)} خبر")
                news_list = raw_news
            else:
                logger.warning(f"⚠️ {source_name}: رمز حالة {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ انتهت مهلة {source_name}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 خطأ اتصال {source_name}")
        except Exception as e:
            logger.warning(f"⚠️ خطأ {source_name}: {e}")
        
        return news_list
    
    def fetch_all(self) -> List[Dict]:
        all_news = []
        
        for source_name, source_info in RSS_SOURCES.items():
            news = self.fetch_from_source(source_name, source_info)
            all_news.extend(news)
        
        all_news.sort(key=lambda x: (-x["source_priority"], x["source"]))
        logger.info(f"📊 المجموع النهائي: {len(all_news)} خبر")
        
        return all_news


fetcher = NewsFetcher()