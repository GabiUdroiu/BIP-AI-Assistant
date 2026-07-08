from app.services.chat_providers.base import BaseLlmProvider

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(BaseLlmProvider):
    """OpenRouter LLM provider with multi-model support."""

    def __init__(self, api_key: str, model: str) -> None:
        super().__init__(api_key, model, OPENROUTER_URL)
