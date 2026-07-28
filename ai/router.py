import aiohttp
from models.summary import AISummary
from ai.gemini_provider import GeminiProvider
from ai.openrouter_provider import OpenRouterProvider
from config.settings import settings
from utils.logger import logger

SYSTEM_PROMPT = """
Analyze the news article and return ONLY a valid JSON object containing dual-language fields (English and Arabic).
Match this exact JSON schema:
{
  "title_en": "Professional concise English headline",
  "title_ar": "عنوان خبري احترافي ودقيق باللغة العربية",
  "summary_en": "Accurate 100-150 word summary in English",
  "summary_ar": "ملخص خبري صحفي دقيق ومترجم باللغة العربية (100-150 كلمة)",
  "key_points_en": ["Point 1 in English", "Point 2 in English", "Point 3 in English"],
  "key_points_ar": ["نقطة 1 بالعربية", "نقطة 2 بالعربية", "نقطة 3 بالعربية"],
  "why_it_matters_en": "Context and impact in English",
  "why_it_matters_ar": "أهمية الخبر وسياقه باللغة العربية",
  "category_en": "Category in English",
  "category_ar": "التصنيف بالعربية",
  "country": "Primary region/country",
  "keywords": ["Hashtag1", "Hashtag2", "Hashtag3"]
}
Never invent facts or hallucinate numbers/names.
"""

class AIRouter:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_AI_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

        # أرخص وأسرع 3 نماذج مجانية مباشرة من Google AI Studio
        self.google_models = [
            "gemini-2.5-flash-lite",  # الخيار 1: الأسرع والأخف مجاناً 30RPM
            "gemini-2.5-flash",       # الخيار 2: المتوازن عالي الدقة 15RPM
            "gemini-1.5-flash-8b"     # الخيار 3: النموذج المصغر عالي السرعة
        ]

        # أرخص 3 نماذج مجانية من OpenRouter كبديل طوارئ
        self.openrouter_models = [
            "openrouter/free",                       # الموجه الذكي التلقائي لأفضل نموذج مجاني متاح
            "meta-llama/llama-3.3-70b-instruct:free", # نموذج Llama 3.3 المجاني
            "google/gemma-2-9b-it:free"               # نموذج Gemma 2 المجاني
        ]

    async def summarize_article(self, text: str) -> AISummary:
        # 1️⃣ المحاولة أولاً مع أرخص 3 نماذج من جوجل بالترتيب
        if self.gemini_key:
            for model_name in self.google_models:
                try:
                    provider = GeminiProvider(self.gemini_key, self.session, model_name=model_name)
                    res = await provider.summarize(text, SYSTEM_PROMPT)
                    logger.info(f"Successfully summarized article using Google Gemini [{model_name}]")
                    return res
                except Exception as e:
                    logger.warning(f"Google model [{model_name}] failed/quota: {e}. Trying next model...")

        # 2️⃣ الانتقال لأرخص 3 نماذج في OpenRouter إذا انتهت حصة جوجل
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

        # 3️⃣ ملخص طوارئ للهيكل في حال توقف جميع النماذج لتجنب توقف البوت
        logger.error("All AI providers failed. Returning emergency structural summary.")
        return AISummary(
            title_en=text[:80],
            title_ar=text[:80],
            summary_en=text[:250] + "...",
            summary_ar=text[:250] + "...",
            key_points_en=["Detailed AI summary temporarily unavailable."],
            key_points_ar=["التلخيص التفصيلي غير متاح حالياً."],
            why_it_matters_en="Significant development in international news.",
            why_it_matters_ar="تطور هام في الأخبار العالمية.",
            category_en="Other",
            category_ar="أخرى",
            country="Global",
            keywords=["News", "Update"]
        )
