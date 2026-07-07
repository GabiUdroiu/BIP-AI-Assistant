from typing import Protocol


class ChatProvider(Protocol):
    api_key: str

    def reply(self, messages: list[dict]) -> str: ...
