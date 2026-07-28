import math
import re
from typing import List
from models.article import Article
from utils.logger import logger

class Deduplicator:
    @staticmethod
    def _tokenize(text: str) -> set:
        words = re.findall(r'\w+', text.lower())
        return set(words)

    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def deduplicate(self, articles: List[Article], similarity_threshold: float = 0.55) -> List[Article]:
        unique_articles: List[Article] = []
        seen_urls = set()
        seen_titles_tokens = []

        for article in articles:
            if article.url in seen_urls or article.canonical_url in seen_urls:
                continue

            tokens = self._tokenize(article.title)
            is_duplicate = False

            for existing_tokens in seen_titles_tokens:
                sim = self.jaccard_similarity(tokens, existing_tokens)
                if sim >= similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_urls.add(article.url)
                seen_urls.add(article.canonical_url)
                seen_titles_tokens.append(tokens)
                unique_articles.append(article)

        logger.info(f"Deduplication complete: {len(articles)} -> {len(unique_articles)} articles.")
        return unique_articles
