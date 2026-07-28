import asyncio
import hashlib
import time
from datetime import datetime
from typing import List
import aiohttp
import feedparser
from bs4 import BeautifulSoup

from collectors.base_collector import BaseCollector
from models.article import Article
from config.sources import NEWS_SOURCES
from utils.logger import logger
from utils.text_sanitizer import clean_url, sanitize_html

class RSSCollector(BaseCollector):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_feed(self, source: dict) -> List[Article]:
        articles = []
        try:
            async with self.session.get(source["url"], timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed HTTP {resp.status} for RSS source: {source['name']}")
                    return articles
                content = await resp.read()
                
            parsed = feedparser.parse(content)
            for entry in parsed.entries:
                title = sanitize_html(getattr(entry, "title", ""))
                link = clean_url(getattr(entry, "link", ""))
                if not title or not link:
                    continue

                summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary_clean = BeautifulSoup(summary_raw, "html.parser").get_text() if summary_raw else title

                pub_date = datetime.utcnow()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))

                # Hash ID generation
                article_id = hashlib.md5(f"{link}_{title}".encode("utf-8")).hexdigest()

                # Media image extraction
                img_url = None
                if "media_content" in entry and len(entry.media_content) > 0:
                    img_url = entry.media_content[0].get("url")
                elif "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
                    img_url = entry.media_thumbnail[0].get("url")

                articles.append(Article(
                    id=article_id,
                    title=title,
                    content=summary_clean,
                    description=summary_clean[:300],
                    url=link,
                    canonical_url=link,
                    image_url=img_url,
                    pub_date=pub_date,
                    author=getattr(entry, "author", source["name"]),
                    source=source["name"],
                    source_credibility=source["credibility"],
                    language="en"
                ))
        except Exception as e:
            logger.error(f"Error fetching RSS for {source['name']}: {e}")
        return articles

    async def collect(self) -> List[Article]:
        tasks = [self.fetch_feed(source) for source in NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_articles = []
        for res in results:
            if isinstance(res, list):
                all_articles.extend(res)
        logger.info(f"Collected total of {len(all_articles)} articles from RSS feeds.")
        return all_articles
