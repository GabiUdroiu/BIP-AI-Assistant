from typing import Protocol


class ChatProviderError(Exception):
    """Raised when a chat provider call fails, with a message safe to show the user."""


class ChatProvider(Protocol):
    api_key: str

    def reply(self, messages: list[dict]) -> str: ...
