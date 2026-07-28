import aiohttp
from models.summary import AISummary
from ai.gemini_provider import GeminiProvider
from ai.openrouter_provider import OpenRouterProvider
from config.settings import settings
from utils.logger import logger

SYSTEM_PROMPT = """
Analyze the article and return ONLY a valid JSON object with these exact keys:
- title: Concise professional headline
- summary: Detailed accurate summary (150-300 words)
- key_points: Array of 3-5 key bullet points
- why_it_matters: Impact & significance
- category: One of [Technology, Artificial Intelligence, Politics, Business, Economy, Finance, Science, Space, Health, Cybersecurity, Gaming, Crypto, Climate, Education, Sports, Entertainment, Other]
- country: Main region/country affected
- keywords: Array of 3-5 tags
Never invent facts or hallucinate numbers/names.
"""

class AIRouter:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_AI_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

    async def summarize_article(self, text: str) -> AISummary:
        # Tier 1: Gemini Primary
        if self.gemini_key:
            try:
                provider = GeminiProvider(self.gemini_key, self.session)
                res = await provider.summarize(text, SYSTEM_PROMPT)
                logger.info("Successfully summarized article using Gemini")
                return res
            except Exception as e:
                logger.warning(f"Gemini Primary failed: {e}. Falling back to OpenRouter...")

        # Tier 2 & 3: OpenRouter Dynamic Free Models
        if self.openrouter_key:
            free_models = await OpenRouterProvider.get_free_models()
            provider = OpenRouterProvider(self.openrouter_key, self.session)
            
            for model_id in free_models:
                try:
                    res = await provider.summarize(text, SYSTEM_PROMPT, model_id=model_id)
                    logger.info(f"Successfully summarized article using OpenRouter [{model_id}]")
                    return res
                except Exception as e:
                    logger.warning(f"OpenRouter model {model_id} failed: {e}")

        # Emergency Fallback Mock Model to prevent workflow collapse
        logger.error("All AI providers failed. Returning emergency structural summary.")
        return AISummary(
            title=text[:80],
            summary=text[:300] + "...",
            key_points=["Detailed AI summary temporarily unavailable."],
            why_it_matters="Significant development in international news.",
            category="Other",
            country="Global",
            keywords=["News", "Update"]
        )
