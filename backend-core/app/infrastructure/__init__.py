"""Infrastructure layer - External services and data access."""

from .database import get_db, get_engine, Base
from .external import (
    SpeechToTextService,
    WhisperSpeechService,
    EmbeddingService,
    OpenRouterEmbeddingService,
    get_llm_provider,
    get_llm_provider_by_name,
)

__all__ = [
    # Database
    "get_db",
    "get_engine",
    "Base",
    # External Services
    "SpeechToTextService",
    "WhisperSpeechService",
    "EmbeddingService",
    "OpenRouterEmbeddingService",
    "get_llm_provider",
    "get_llm_provider_by_name",
]
