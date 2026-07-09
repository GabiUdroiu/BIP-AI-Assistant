"""Domain layer - Core business logic and entities."""

from .models import (
    AudioSegment,
    Transcript,
    ChatResponse,
    Message,
    Conversation,
    VoiceStreamSession,
)
from .exceptions import (
    ApplicationException,
    VoiceProcessingError,
    AudioProcessingError,
    ChatError,
    ContextRetrievalError,
    ConfigurationError,
    ExternalServiceError,
    DatabaseError,
    ConversationNotFoundError,
)

__all__ = [
    # Models
    "AudioSegment",
    "Transcript",
    "ChatResponse",
    "Message",
    "Conversation",
    "VoiceStreamSession",
    # Exceptions
    "ApplicationException",
    "VoiceProcessingError",
    "AudioProcessingError",
    "ChatError",
    "ContextRetrievalError",
    "ConfigurationError",
    "ExternalServiceError",
    "DatabaseError",
    "ConversationNotFoundError",
]
