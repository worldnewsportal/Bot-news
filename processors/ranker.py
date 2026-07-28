from datetime import datetime
from typing import List
from models.article import Article
from utils.logger import logger

class NewsRanker:
    BREAKING_KEYWORDS = {"breaking", "urgent", "announces", "launches", "war", "crisis", "breakthrough", "disaster", "major"}

    def rank_and_select(self, articles: List[Article], top_n: int = 100) -> List[Article]:
        now = datetime.utcnow()

        for article in articles:
            # 1. Base Score from Credibility
            score = article.source_credibility * 10.0

            # 2. Recency Decay (Hours old)
            hours_old = max((now - article.pub_date).total_seconds() / 3600.0, 0.1)
            recency_score = max(24.0 - hours_old, 0.0)
            score += recency_score

            # 3. Breaking Keyword Boost
            title_lower = article.title.lower()
            if any(word in title_lower for word in self.BREAKING_KEYWORDS):
                score += 15.0

            # 4. Content Richness
            if len(article.content) > 200:
                score += 5.0

            article.score = score

        # Sort descending by score
        ranked = sorted(articles, key=lambda x: x.score, reverse=True)
        selected = ranked[:top_n]
        logger.info(f"Ranked {len(articles)} articles. Selected Top {len(selected)}.")
        return selected
