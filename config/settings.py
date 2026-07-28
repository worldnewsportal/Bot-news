import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseModel):
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    GNEWS_API_KEY: str = os.getenv("GNEWS_API_KEY", "")

    MAX_TOP_NEWS: int = 100
    CACHE_FILE: Path = BASE_DIR / "data" / "published_cache.json"
    
    DEFAULT_IMAGE_URL: str = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"
    
    CONCURRENT_REQUESTS: int = 25
    TELEGRAM_POST_DELAY: float = 1.5  # Seconds between messages to respect Telegram limits
    MAX_RETRIES: int = 3

settings = Settings()
