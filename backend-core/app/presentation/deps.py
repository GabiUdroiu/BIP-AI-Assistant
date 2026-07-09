"""
Dependency injection for presentation layer.
Provides application services and other dependencies to routes.
"""

from functools import lru_cache
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import (
    get_speech_service,
    get_conversation_service,
    get_rag_service,
    get_prompt_service,
    get_chat_provider,
)
from app.infrastructure.database.session import get_db
from app.infrastructure.external import WhisperSpeechService
from app.application import (
    ProcessVoiceUseCase,
    ChatWithContextUseCase,
    StreamVoiceUseCase,
    VoiceApplicationService,
    ChatApplicationService,
)
from app.core.logging import logger


# ============ Use Cases ============

@lru_cache
def get_process_voice_use_case() -> ProcessVoiceUseCase:
    """Get process voice use case."""
    speech_service = get_speech_service()
    whisper_service = WhisperSpeechService(speech_service)
    return ProcessVoiceUseCase(whisper_service)


def get_chat_use_case(db: Session = Depends(get_db)) -> ChatWithContextUseCase:
    """Get chat with context use case."""
    return ChatWithContextUseCase(
        chat_provider=get_chat_provider(),
        conversation_service=get_conversation_service(db),
        rag_service=get_rag_service(),
        prompt_service=get_prompt_service(),
    )


def get_stream_voice_use_case(chat_use_case: ChatWithContextUseCase = Depends(get_chat_use_case)) -> StreamVoiceUseCase:
    """Get stream voice use case."""
    return StreamVoiceUseCase(
        process_voice_use_case=get_process_voice_use_case(),
        chat_use_case=chat_use_case,
    )


# ============ Application Services ============

def get_voice_service(stream_voice_use_case: StreamVoiceUseCase = Depends(get_stream_voice_use_case)) -> VoiceApplicationService:
    """Get voice application service."""
    return VoiceApplicationService(
        process_voice_use_case=get_process_voice_use_case(),
        stream_voice_use_case=stream_voice_use_case,
    )


def get_chat_service(chat_use_case: ChatWithContextUseCase = Depends(get_chat_use_case)) -> ChatApplicationService:
    """Get chat application service."""
    return ChatApplicationService(
        chat_use_case=chat_use_case,
    )


# ============ Utilities ============

def log_request_start(endpoint: str, request_data: dict = None) -> None:
    """Log the start of a request."""
    logger.info(f"📨 {endpoint} request received")
    if request_data:
        logger.debug(f"   Data: {request_data}")


def log_request_success(endpoint: str, response_data: dict = None) -> None:
    """Log successful request completion."""
    logger.info(f"✅ {endpoint} completed successfully")
    if response_data:
        logger.debug(f"   Response: {response_data}")


def log_request_error(endpoint: str, error: str) -> None:
    """Log request error."""
    logger.error(f"❌ {endpoint} failed: {error}")
