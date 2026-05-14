"""
═══════════════════════════════════════════════════════════
   وحدة جلب الأخبار - عبر خدمة rss2json
═══════════════════════════════════════════════════════════
"""

import hashlib
import requests
from typing import List, Dict
from config import RSS_SOURCES, REQUEST_TIMEOUT
import logging

logger = logging.getLogger(__name__)

RSS2JSON = "https://api.rss2json.com/v1/api.json"


class NewsFetcher:
    
    def __init__(self):
        self.session = requests.Session()
    
    def _gen_id(self, title: str, link: str) -> str:
        return hashlib.md5(f"{title}:{link}".encode()).hexdigest()[:12]
    
    def _clean(self, text: str) -> str:
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'&[^;]+;', ' ', clean)
        return clean[:300].strip()
    
    def fetch_source(self, name: str, info: Dict) -> List[Dict]:
        news_list = []
        
        try:
            logger.info(f"🔗 جاري جلب: {name}...")
            
            resp = self.session.get(
                RSS2JSON,
                params={"rss_url": info["url"]},
                timeout=REQUEST_TIMEOUT
            )
            
            if resp.status_code != 200:
                logger.warning(f"⚠️ {name}: رمز {resp.status_code}")
                return news_list
            
            data = resp.json()
            
            if data.get("status") != "ok":
                logger.warning(f"⚠️ {name}: rss2json خطأ")
                return news_list
            
            items = data.get("items", [])
            logger.info(f"📥 {name}: {len(items)} عنصر")
            
            for item in items:
                title = item.get("title", "").strip()
                link = item.get("link", "").strip()
                desc = item.get("description", "")
                pub_date = item.get("pubDate", "")
                
                if title and link:
                    news_list.append({
                        "id": self._gen_id(title, link),
                        "title": title,
                        "link": link,
                        "description": self._clean(desc) if desc else "",
                        "pub_date": pub_date,
                        "source": name,
                        "source_priority": info.get("priority", 5),
                        "source_category": info.get("category", "general"),
                    })
            
            # تسجيل أول عنوان
            if news_list:
                logger.info(f"   📰 {news_list[0]['title'][:80]}")
            
            logger.info(f"✅ {name}: {len(news_list)} خبر")
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ انتهت مهلة {name}")
        except Exception as e:
            logger.warning(f"⚠️ خطأ {name}: {e}")
        
        return news_list
    
    def fetch_all(self) -> List[Dict]:
        all_news = []
        
        for name, info in RSS_SOURCES.items():
            news = self.fetch_source(name, info)
            all_news.extend(news)
        
        all_news.sort(key=lambda x: (-x["source_priority"], x["source"]))
        logger.info(f"📊 المجموع النهائي: {len(all_news)} خبر")
        
        return all_news


fetcher = NewsFetcher()