import aiohttp
from models.summary import AISummary
from ai.gemini_provider import GeminiProvider
from ai.openrouter_provider import OpenRouterProvider
from config.settings import settings
from utils.logger import logger

SYSTEM_PROMPT = """
You are an expert international news editor and translator.
Analyze the provided news article and generate a COMPREHENSIVE, DETAILED, and IN-DEPTH dual-language summary.

Return ONLY a valid JSON object matching this EXACT schema:
{
  "title_en": "Professional concise English headline",
  "title_ar": "عنوان خبري احترافي ودقيق باللغة العربية",
  "summary_en": "Comprehensive detailed 150-250 word summary covering all facts, background context, and key developments in clear professional English.",
  "summary_ar": "ملخص صحفي تفصيلي وافي ومعمق (150-250 كلمة) يغطي كافة الحقائق والتفاصيل والسياق باللغة العربية السليمة.",
  "key_points_en": ["Detailed point 1 in English", "Detailed point 2 in English", "Detailed point 3 in English"],
  "key_points_ar": ["نقطة تفصيلية 1 بالعربية", "نقطة تفصيلية 2 بالعربية", "نقطة تفصيلية 3 بالعربية"],
  "why_it_matters_en": "In-depth explanation of the global, geopolitical, economic, or technological impact in English.",
  "why_it_matters_ar": "شرح تفصيلي لأهمية الخبر والتأثير الجيوسياسي أو الاقتصادي أو التقني باللغة العربية.",
  "category_en": "Technology / Business / Politics / Science / Crypto / Health / Climate",
  "category_ar": "تكنولوجيا / اقتصاد / سياسة / علوم / عملات رقمية / صحة / مناخ",
  "country": "Primary region/country affected",
  "keywords": ["Hashtag1", "Hashtag2", "Hashtag3"]
}

Rules:
- Make summaries rich, thorough, and highly detailed (never short or brief).
- Provide accurate translations without omitting context.
- Do NOT hallucinate names or figures.
"""

class AIRouter:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_AI_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

        # أسماء نماذج جوميناي الرسمية المستقرة والمؤكدة 100% في Google AI Studio API
        self.google_models = [
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro"
        ]

        self.openrouter_models = [
            "openrouter/free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-2-9b-it:free"
        ]

    async def summarize_article(self, text: str) -> AISummary:
        # 1️⃣ تجربة نماذج جوجل المستقرة الرسمية
        if self.gemini_key:
            for model_name in self.google_models:
                try:
                    provider = GeminiProvider(self.gemini_key, self.session, model_name=model_name)
                    res = await provider.summarize(text, SYSTEM_PROMPT)
                    logger.info(f"Successfully summarized article using Google Gemini [{model_name}]")
                    return res
                except Exception as e:
                    logger.warning(f"Google model [{model_name}] failed: {e}. Trying next model...")

        # 2️⃣ التجربة عبر OpenRouter عند اللزوم
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

        # 3️⃣ ملخص طوارئ للهيكل في حال فشل جميع الاتصالات
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
