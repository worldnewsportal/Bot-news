import json
import re
import aiohttp
from models.summary import AISummary
from utils.logger import logger

class GeminiProvider:
    def __init__(self, api_key: str, session: aiohttp.ClientSession, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.session = session
        self.model_name = model_name
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    async def summarize(self, text: str, prompt: str) -> AISummary:
        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nArticle Text:\n{text}"}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        async with self.session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                res_text = await resp.text()
                raise Exception(f"Gemini [{self.model_name}] error status {resp.status}: {res_text}")
            
            data = await resp.json()
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # تنظيف علامات Markdown (```json) لتجنب أخطاء القراءة
            clean_json = re.sub(r'```(?:json)?\s*|\s*```', '', raw_json).strip()
            parsed = json.loads(clean_json)
            return AISummary(**parsed)
