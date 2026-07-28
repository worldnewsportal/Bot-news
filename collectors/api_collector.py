from typing import List
import aiohttp
from collectors.base_collector import BaseCollector
from models.article import Article
from config.settings import settings
from utils.logger import logger

class APICollector(BaseCollector):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def collect(self) -> List[Article]:
        articles = []
        if not settings.NEWSAPI_KEY:
            return articles
            
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=100&apiKey={settings.NEWSAPI_KEY}"
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for item in data.get("articles", []):
                        if not item.get("title") or not item.get("url"):
                            continue
                        articles.append(Article(
                            id=item["url"],
                            title=item["title"],
                            content=item.get("content") or item.get("description") or item["title"],
                            description=item.get("description") or item["title"],
                            url=item["url"],
                            canonical_url=item["url"],
                            image_url=item.get("urlToImage"),
                            pub_date=item.get("publishedAt"),
                            author=item.get("author") or "NewsAPI",
                            source=item.get("source", {}).get("name", "NewsAPI"),
                            source_credibility=2.5,
                            language="en"
                        ))
        except Exception as e:
            logger.error(f"Error fetching NewsAPI: {e}")
        return articles
