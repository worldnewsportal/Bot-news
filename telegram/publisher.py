import asyncio
import aiohttp
from config.settings import settings
from models.article import Article
from models.summary import AISummary
from telegram.formatter import TelegramFormatter
from utils.logger import logger

class TelegramPublisher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def publish_news(self, article: Article, summary: AISummary) -> bool:
        if not self.token or not self.chat_id:
            logger.error("Telegram token or chat ID missing.")
            return False

        # تنسيق النص وإضافة روابط ShrinkMe و Adsterra
        text = TelegramFormatter.format_message(article, summary)
        
        # Try sendPhoto first
        photo_url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        payload_photo = {
            "chat_id": self.chat_id,
            "photo": article.image_url or settings.DEFAULT_IMAGE_URL,
            "caption": text,
            "parse_mode": "HTML"
        }

        try:
            async with self.session.post(photo_url, json=payload_photo, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return True
                elif resp.status == 429: # Rate Limited
                    data = await resp.json()
                    retry_after = data.get("parameters", {}).get("retry_after", 5)
                    logger.warning(f"Telegram Rate limited! Sleeping for {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self.publish_news(article, summary)
                else:
                    logger.warning(f"sendPhoto failed HTTP {resp.status}. Falling back to sendMessage.")
        except Exception as e:
            logger.warning(f"Error in sendPhoto: {e}. Trying sendMessage.")

        # Fallback to sendMessage
        msg_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload_msg = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            async with self.session.post(msg_url, json=payload_msg, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to publish article via sendMessage: {e}")
            return False
