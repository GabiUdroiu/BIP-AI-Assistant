"""
Base LLM provider interface.
Defines contract for all LLM implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_chat_response(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Get response from LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Response creativity (0-2)
            max_tokens: Maximum response length

        Returns:
            Response text from LLM

        Raises:
            ExternalServiceError: If LLM request fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if LLM service is accessible."""
        pass
