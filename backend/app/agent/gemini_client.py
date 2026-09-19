import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def complete(self, prompt: str) -> str:
        for attempt in range(4):
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                )
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.strip("`").replace("json\n", "", 1)
                return text
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)  # 1s, 2s, 4s