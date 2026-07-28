import aiohttp
from bs4 import BeautifulSoup
from config.settings import settings
from utils.logger import logger

class ImageExtractor:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def validate_or_extract_image(self, article_url: str, current_image_url: str) -> str:
        if current_image_url and current_image_url.startswith("http"):
            try:
                async with self.session.head(current_image_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                        return current_image_url
            except Exception:
                pass

        # HTML Scrape for OpenGraph
        try:
            async with self.session.get(article_url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    html_content = await resp.text()
                    soup = BeautifulSoup(html_content, "html.parser")
                    og_image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
                    if og_image and og_image.get("content"):
                        return og_image["content"]
        except Exception as e:
            logger.debug(f"Failed to scrape image from {article_url}: {e}")

        return settings.DEFAULT_IMAGE_URL
