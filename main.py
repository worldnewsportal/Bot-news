import asyncio
import time
import aiohttp

from config.settings import settings
from collectors.rss_collector import RSSCollector
from collectors.api_collector import APICollector
from processors.deduplicator import Deduplicator
from processors.ranker import NewsRanker
from processors.image_extractor import ImageExtractor
from ai.router import AIRouter
from telegram.publisher import TelegramPublisher
from cache.cache_manager import CacheManager
from utils.logger import logger

async def main():
    start_time = time.time()
    logger.info("===========================================")
    logger.info("  Starting Automated AI Telegram News Bot  ")
    logger.info("===========================================")

    cache_manager = CacheManager(settings.CACHE_FILE)

    async with aiohttp.ClientSession() as session:
        # Step 1: Collect News
        logger.info("[1/6] Collecting news articles from sources...")
        rss_collector = RSSCollector(session)
        api_collector = APICollector(session)

        rss_articles, api_articles = await asyncio.gather(
            rss_collector.collect(),
            api_collector.collect()
        )
        raw_articles = rss_articles + api_articles
        logger.info(f"Total raw articles collected: {len(raw_articles)}")

        # Filter already published
        unpublished_articles = [a for a in raw_articles if not cache_manager.is_published(a.id)]
        logger.info(f"Articles after cache filtering: {len(unpublished_articles)}")

        # Step 2: Deduplicate
        logger.info("[2/6] Running semantic deduplication engine...")
        deduplicator = Deduplicator()
        unique_articles = deduplicator.deduplicate(unpublished_articles)

        # Step 3: Rank & Select Top 100
        logger.info("[3/6] Ranking news articles and selecting Top 100...")
        ranker = NewsRanker()
        top_articles = ranker.rank_and_select(unique_articles, top_n=settings.MAX_TOP_NEWS)

        # Step 4 & 5 & 6: Process AI, Extract Images, & Publish
        logger.info("[4/6] Processing AI Summaries and Telegram Publishing...")
        ai_router = AIRouter(session)
        image_extractor = ImageExtractor(session)
        publisher = TelegramPublisher(session)

        published_count = 0
        skipped_count = 0

        for idx, article in enumerate(top_articles, 1):
            logger.info(f"Processing ({idx}/{len(top_articles)}): {article.title[:60]}...")

            # Validate / Extract Image
            article.image_url = await image_extractor.validate_or_extract_image(article.url, article.image_url)

            # Summarize via AI Router
            try:
                summary = await ai_router.summarize_article(article.content)
            except Exception as e:
                logger.error(f"Failed AI summarization for article '{article.title}': {e}")
                skipped_count += 1
                continue

            # Publish to Telegram
            success = await publisher.publish_news(article, summary)
            if success:
                published_count += 1
                cache_manager.mark_published(article.id)
                logger.info(f"Successfully published article #{published_count}")
            else:
                skipped_count += 1
                logger.error(f"Failed to publish article #{idx}")

            # Rate Limit Delay between posts
            await asyncio.sleep(settings.TELEGRAM_POST_DELAY)

        # Save Persistent Cache
        cache_manager.save()

        elapsed = time.time() - start_time
        logger.info("===========================================")
        logger.info(f"Execution Completed in {elapsed:.2f} seconds.")
        logger.info(f"Published: {published_count} | Skipped: {skipped_count}")
        logger.info("===========================================")

if __name__ == "__main__":
    asyncio.run(main())
