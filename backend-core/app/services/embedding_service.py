import requests

OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"


class EmbeddingService:
    """Text -> vector via OpenRouter's embeddings endpoint (same API key as chat)."""

    def __init__(self, api_key: str, model: str, dimensions: int) -> None:
        self.api_key = api_key
        self._model = model
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            OPENROUTER_EMBEDDINGS_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={"model": self._model, "input": text, "dimensions": self._dimensions},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
