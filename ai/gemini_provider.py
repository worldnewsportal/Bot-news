import json
import aiohttp
from models.summary import AISummary
from utils.logger import logger

class GeminiProvider:
    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self.api_key = api_key
        self.session = session
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

    async def summarize(self, text: str, prompt: str) -> AISummary:
        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nArticle Text:\n{text}"}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        async with self.session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                res_text = await resp.text()
                raise Exception(f"Gemini API error status {resp.status}: {res_text}")
            
            data = await resp.json()
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_json)
            return AISummary(**parsed)
