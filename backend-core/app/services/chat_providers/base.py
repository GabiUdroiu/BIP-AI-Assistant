from typing import Protocol
from abc import ABC
import requests


class ChatProviderError(Exception):
    """Raised when a chat provider call fails, with a message safe to show the user."""


class ChatProvider(Protocol):
    api_key: str

    def reply(self, messages: list[dict]) -> str: ...


class BaseLlmProvider(ABC):
    """Base class for LLM chat providers with common logic for API calls."""

    def __init__(self, api_key: str, model: str, endpoint: str) -> None:
        self.api_key = api_key
        self._model = model
        self._endpoint = endpoint

    def reply(self, messages: list[dict]) -> str:
        """Get a reply from the LLM."""
        try:
            response = self._make_request(messages)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429:
                raise ChatProviderError(
                    f"{self.__class__.__name__} rate limit reached. Try again later."
                ) from exc
            raise ChatProviderError(f"{self.__class__.__name__} request failed: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ChatProviderError(f"{self.__class__.__name__} is unreachable: {exc}") from exc

        return self._extract_content(response)

    def _make_request(self, messages: list[dict]) -> requests.Response:
        """Make HTTP request to the LLM endpoint."""
        return requests.post(
            self._endpoint,
            headers=self._get_headers(),
            json=self._get_payload(messages),
            timeout=30,
        )

    def _get_headers(self) -> dict:
        """Get HTTP headers for the request."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _get_payload(self, messages: list[dict]) -> dict:
        """Get request payload. Can be overridden by subclasses."""
        return {
            "model": self._model,
            "messages": messages,
        }

    def _extract_content(self, response: requests.Response) -> str:
        """Extract content from response. Can be overridden by subclasses."""
        data = response.json()
        content = data["choices"][0]["message"].get("content")
        return content or "[No reply generated]"
