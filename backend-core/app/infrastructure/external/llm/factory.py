"""
LLM Provider Factory.
Creates appropriate LLM provider based on configuration.
"""

from typing import Optional

from app.core.config import get_settings
from app.domain.exceptions import ConfigurationError
from app.core.logging import logger

# Import existing providers
from app.services.chat_providers.openrouter_provider import OpenRouterProvider
from app.services.chat_providers.groq_provider import GroqProvider


def get_llm_provider():
    """
    Factory function to get configured LLM provider.

    Returns the appropriate LLM provider based on APP_DEFAULT_CHAT_PROVIDER setting.

    Raises:
        ConfigurationError: If provider is not properly configured
    """
    settings = get_settings()
    provider_name = settings.default_chat_provider

    if provider_name == "groq":
        if not settings.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY not configured")
        logger.info(f"Using Groq LLM provider: {settings.groq_model}")
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model
        )

    elif provider_name == "openrouter":
        if not settings.openrouter_api_key:
            raise ConfigurationError("OPENROUTER_API_KEY not configured")
        logger.info(f"Using OpenRouter LLM provider: {settings.openrouter_model}")
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model
        )

    else:
        raise ConfigurationError(
            f"Unknown LLM provider: {provider_name}. "
            f"Must be 'groq' or 'openrouter'"
        )


def get_llm_provider_by_name(name: str):
    """
    Get specific LLM provider by name.

    Args:
        name: Provider name ('groq' or 'openrouter')

    Returns:
        Configured LLM provider instance

    Raises:
        ConfigurationError: If provider is not properly configured
    """
    settings = get_settings()

    if name == "groq":
        if not settings.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY not configured")
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model
        )

    elif name == "openrouter":
        if not settings.openrouter_api_key:
            raise ConfigurationError("OPENROUTER_API_KEY not configured")
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model
        )

    else:
        raise ConfigurationError(f"Unknown LLM provider: {name}")
