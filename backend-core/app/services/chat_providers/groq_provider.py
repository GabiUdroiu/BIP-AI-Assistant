from app.services.chat_providers.base import BaseLlmProvider

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(BaseLlmProvider):
    """Groq LLM provider using their OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str) -> None:
        super().__init__(api_key, model, GROQ_URL)
