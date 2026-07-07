import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self._model = model

    def reply(self, messages: list[dict]) -> str:
        response = requests.post(
            GROQ_URL,
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
        data = response.json()
        content = data["choices"][0]["message"].get("content")
        return content or "[No reply generated]"
