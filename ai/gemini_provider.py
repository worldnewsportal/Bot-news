import json
import re
from google import genai
from google.genai import types
from models.summary import AISummary
from utils.logger import logger

class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        # استخدام المكتبة الرسمية الحديثة الموحدة من جوجل
        self.client = genai.Client(api_key=self.api_key)

    async def summarize(self, text: str, prompt: str) -> AISummary:
        full_prompt = f"{prompt}\n\nArticle Text:\n{text}"
        
        # ربط Pydantic Schema مباشرة بمكتبة جوجل لضمان جودة الهيكل المزدوج
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AISummary,
            temperature=0.2
        )

        # استدعاء غير متزامن باستخدام client.aio الحديث
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=config
        )

        # إذا ارجعت المكتبة الكائن جاهزاً ومترجماً
        if hasattr(response, 'parsed') and response.parsed:
            return response.parsed
        
        # في حال إرجاع نص خام مفكك
        raw_text = response.text
        clean_json = re.sub(r'```(?:json)?\s*|\s*```', '', raw_text).strip()
        parsed = json.loads(clean_json)
        return AISummary(**parsed)
