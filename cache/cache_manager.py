import json
from pathlib import Path
from typing import Set
from utils.logger import logger

class CacheManager:
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.published_ids: Set[str] = set()
        self.load()

    def load(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.published_ids = set(data.get("published_ids", []))
                logger.info(f"Loaded {len(self.published_ids)} published IDs from cache.")
            except Exception as e:
                logger.error(f"Error loading cache file: {e}")
                self.published_ids = set()

    def is_published(self, article_id: str) -> bool:
        return article_id in self.published_ids

    def mark_published(self, article_id: str):
        self.published_ids.add(article_id)

    def save(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"published_ids": list(self.published_ids)}, f, indent=2)
            logger.info(f"Saved {len(self.published_ids)} published IDs to cache file.")
        except Exception as e:
            logger.error(f"Error saving cache file: {e}")
