"""
Custom application exceptions.
Organized by domain responsibility.
"""


class ApplicationException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str | None = None, details: dict | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# Voice/Speech Exceptions
class VoiceProcessingError(ApplicationException):
    """Raised when voice processing fails."""
    pass


class AudioProcessingError(ApplicationException):
    """Raised when audio processing fails."""
    pass


# Chat Exceptions
class ChatError(ApplicationException):
    """Raised when chat operation fails."""
    pass


class ContextRetrievalError(ApplicationException):
    """Raised when context/RAG retrieval fails."""
    pass


# Configuration Exceptions
class ConfigurationError(ApplicationException):
    """Raised when configuration is invalid."""
    pass


class ExternalServiceError(ApplicationException):
    """Raised when external service (LLM, Whisper, etc) fails."""
    pass


# Database Exceptions
class DatabaseError(ApplicationException):
    """Raised when database operation fails."""
    pass


class ConversationNotFoundError(ApplicationException):
    """Raised when conversation doesn't exist."""
    pass
