import aiohttp
from models.summary import AISummary
from ai.gemini_provider import GeminiProvider
from ai.openrouter_provider import OpenRouterProvider
from config.settings import settings
from utils.logger import logger

SYSTEM_PROMPT = """
You are an expert international news editor and translator.
Analyze the provided news article and generate a COMPREHENSIVE, DETAILED, and IN-DEPTH dual-language summary.
Please summarize in Arabic and English. 

Required Fields:
- title_en & title_ar: Concise headlines in English and Arabic.
- summary_en & summary_ar: Detailed 150-250 word summaries covering all background and facts.
- key_points_en & key_points_ar: 3 to 5 key takeaway bullet points in both languages.
- why_it_matters_en & why_it_matters_ar: In-depth impact analysis in both languages.
- category_en & category_ar: News category in both languages.
- country: Main region/country affected.
- keywords: 3 to 5 relevant tags/hashtags.

Never invent facts or hallucinate numbers/names.
"""

class AIRouter:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_AI_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

        # أحدث نماذج جوميناي عبر مكتبة Google GenAI SDK
        self.google_models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-1.5-flash"
        ]

        self.openrouter_models = [
            "openrouter/free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-2-9b-it:free"
        ]

    async def summarize_article(self, text: str) -> AISummary:
        # 1️⃣ التجربة باستخدام المكتبة الرسمية الجديدة لـ Google GenAI
        if self.gemini_key:
            for model_name in self.google_models:
                try:
                    provider = GeminiProvider(api_key=self.gemini_key, model_name=model_name)
                    res = await provider.summarize(text, SYSTEM_PROMPT)
                    logger.info(f"Successfully summarized article using Google GenAI SDK [{model_name}]")
                    return res
                except Exception as e:
                    logger.warning(f"Google GenAI SDK [{model_name}] failed: {e}. Trying next model...")

        # 2️⃣ الانتقال عبر OpenRouter عند اللزوم
        if self.openrouter_key:
            logger.info("Falling back to OpenRouter free models...")
            provider = OpenRouterProvider(self.openrouter_key, self.session)
            
            for model_id in self.openrouter_models:
                try:
                    res = await provider.summarize(text, SYSTEM_PROMPT, model_id=model_id)
                    logger.info(f"Successfully summarized article using OpenRouter [{model_id}]")
                    return res
                except Exception as e:
                    logger.warning(f"OpenRouter model [{model_id}] failed: {e}")

        # 3️⃣ ملخص طوارئ للهيكل في حال فشل جميع النماذج
        logger.error("All AI providers failed. Returning emergency structural summary.")
        return AISummary(
            title_en=text[:80],
            title_ar=text[:80],
            summary_en=text[:300] + "...",
            summary_ar=text[:300] + "...",
            key_points_en=["Detailed AI summary temporarily unavailable."],
            key_points_ar=["التلخيص التفصيلي غير متاح حالياً."],
            why_it_matters_en="Significant development in international news.",
            why_it_matters_ar="تطور هام في الأخبار العالمية.",
            category_en="General",
            category_ar="عام",
            country="Global",
            keywords=["News", "Update"]
        )
