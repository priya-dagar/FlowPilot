import json

class FakeLLMClient:
    """Stand-in for Gemini. Same interface — .complete(prompt) -> JSON string.
    Swap this for a real GeminiClient later without touching leave_agent.py."""

    def complete(self, prompt: str) -> str:
        # crude keyword-based fake extraction, just to prove the pipeline
        text = prompt.lower()

        if "3 days" in text or "three days" in text:
            return json.dumps({"start_date": "2026-09-25", "days_requested": 3, "clear": True})
        if "2 days" in text or "two days" in text:
            return json.dumps({"start_date": "2026-09-25", "days_requested": 2, "clear": True})
        if "1 day" in text or "one day" in text:
            return json.dumps({"start_date": "2026-09-25", "days_requested": 1, "clear": True})

        # ambiguous fallback
        return json.dumps({"start_date": None, "days_requested": None, "clear": False})