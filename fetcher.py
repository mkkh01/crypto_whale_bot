"""
═══════════════════════════════════════════════════════════
   وحدة جلب الأخبار - محسنة لتجنب 429
═══════════════════════════════════════════════════════════
"""

import hashlib
import asyncio
import requests
from typing import List, Dict
from config import RSS_SOURCES, REQUEST_TIMEOUT
import logging

logger = logging.getLogger(__name__)

# خدمتين بديلتين لتبديل بينهما عند تجاوز limit
RSS_SERVICES = [
    "https://api.rss2json.com/v1/api.json",
    "https://api.allorigins.win/raw?url=",
]


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
    
    def _fetch_via_rss2json(self, url: str) -> List[Dict]:
        """الطريقة الأولى: rss2json"""
        try:
            resp = self.session.get(
                "https://api.rss2json.com/v1/api.json",
                params={"rss_url": url},
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    return data.get("items", [])
        except:
            pass
        return []
    
    def _fetch_via_allorigins(self, url: str) -> List[Dict]:
        """الطريقة الثانية: allorigins (بديل)"""
        try:
            import xml.etree.ElementTree as ET
            resp = self.session.get(
                "https://api.allorigins.win/raw",
                params={"url": url},
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                root = ET.fromstring(resp.text)
                items = root.findall('.//item')
                result = []
                for item in items[:10]:
                    title = item.findtext('title', '')
                    link = item.findtext('link', '')
                    desc = item.findtext('description', '')
                    pub_date = item.findtext('pubDate', '')
                    if title and link:
                        result.append({
                            "title": title.strip(),
                            "link": link.strip(),
                            "description": self._clean(desc) if desc else "",
                            "pubDate": pub_date,
                        })
                return result
        except:
            pass
        return []
    
    async def fetch_source(self, name: str, info: Dict) -> List[Dict]:
        news_list = []
        url = info["url"]
        
        try:
            logger.info(f"🔗 جاري جلب: {name}...")
            
            # المحاولة الأولى
            items = self._fetch_via_rss2json(url)
            
            # إذا فشلت، المحاولة الثانية
            if not items:
                items = self._fetch_via_allorigins(url)
            
            if not items:
                logger.warning(f"⚠️ {name}: لا توجد بيانات")
                return news_list
            
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
            
            if news_list:
                logger.info(f"✅ {name}: {len(news_list)} خبر")
            
            # انتظار ثانيتين بين كل مصدر لتجنب 429
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ خطأ {name}: {e}")
        
        return news_list
    
    async def fetch_all(self) -> List[Dict]:
        all_news = []
        
        for name, info in RSS_SOURCES.items():
            news = await self.fetch_source(name, info)
            all_news.extend(news)
        
        all_news.sort(key=lambda x: (-x["source_priority"], x["source"]))
        logger.info(f"📊 المجموع النهائي: {len(all_news)} خبر")
        
        return all_news


fetcher = NewsFetcher()