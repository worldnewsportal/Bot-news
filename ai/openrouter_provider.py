import json
import aiohttp
from models.summary import AISummary
from utils.logger import logger

class OpenRouterProvider:
    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self.api_key = api_key
        self.session = session
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    @staticmethod
    async def get_free_models() -> list:
        """جلب قائمة النماذج المجانية المتاحة حالياً على OpenRouter تلقائياً"""
        default_free = [
            "openrouter/free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-2-9b-it:free"
        ]
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("https://openrouter.ai/api/v1/models", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        free = [m["id"] for m in data.get("data", []) if m.get("pricing", {}).get("prompt") == "0"]
                        if free:
                            return free
        except Exception as e:
            logger.warning(f"Failed to dynamically fetch OpenRouter free models: {e}")
        return default_free

    async def summarize(self, text: str, prompt: str, model_id: str) -> AISummary:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": "You are an expert news editor. Output strict valid JSON matching the requested schema."},
                {"role": "user", "content": f"{prompt}\n\nArticle Text:\n{text}"}
            ],
            "response_format": {"type": "json_object"}
        }

        async with self.session.post(self.endpoint, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=25)) as resp:
            if resp.status != 200:
                res_text = await resp.text()
                raise Exception(f"OpenRouter [{model_id}] error status {resp.status}: {res_text}")
            
            data = await resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)
            return AISummary(**parsed)
