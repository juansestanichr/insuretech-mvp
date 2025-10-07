from ..config import settings
import httpx

class ChatbotAgent:
    def reply(self, message: str) -> str:
        # Very simple rule-based fallback
        text = message.lower()
        if "quote" in text or "cotiza" in text:
            return "I can help with quotes. Please provide age, vehicle value, prior claims and credit score."
        if "claim" in text or "siniestro" in text:
            return "To report a claim, send a short description and an amount estimate."
        if "agent" in text:
            return "Our agents are standing by. Meanwhile, ask me anything about your policy."
        # Optional: call LLM if key present (pseudo, not executed here)
        if settings.openai_api_key:
            return "LLM response (placeholder)."
        return "Hello! How can I help you today?"
