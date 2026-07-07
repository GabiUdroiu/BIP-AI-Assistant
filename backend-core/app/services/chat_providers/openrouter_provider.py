import requests

from app.services.chat_providers.base import ChatProviderError

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self._model = model

    def reply(self, messages: list[dict]) -> str:
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={
                    "model": self._model,
                    "messages": messages,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429:
                raise ChatProviderError("OpenRouter rate limit reached. Try again later.") from exc
            raise ChatProviderError(f"OpenRouter request failed: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ChatProviderError(f"OpenRouter is unreachable: {exc}") from exc

        data = response.json()
        content = data["choices"][0]["message"].get("content")
        return content or "[No reply generated]"
