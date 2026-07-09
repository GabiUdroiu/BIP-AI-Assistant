from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.infrastructure.database.session import get_db, get_engine
from app.services.admin_service import AdminService
from app.services.chat_providers.base import ChatProvider
from app.services.chat_providers.groq_provider import GroqProvider
from app.services.chat_providers.openrouter_provider import OpenRouterProvider
from app.services.conversation_service import ConversationService
from app.services.embedding_service import EmbeddingService
from app.services.prompt_service import PromptService
from app.services.rag_service import RagService
from app.services.speech_service import SpeechService


@lru_cache
def get_speech_service() -> SpeechService:
    settings = get_settings()
    return SpeechService(
        model_size=settings.whisper_model_size,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )


@lru_cache
def get_embedding_service() -> EmbeddingService | None:
    settings = get_settings()
    if not settings.openrouter_api_key:
        return None
    return EmbeddingService(
        api_key=settings.openrouter_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )


@lru_cache
def get_rag_service() -> RagService:
    settings = get_settings()
    engine = get_engine() if settings.database_url else None
    return RagService(engine=engine, embedding_service=get_embedding_service())


@lru_cache
def get_prompt_service() -> PromptService:
    settings = get_settings()
    engine = get_engine() if settings.database_url else None
    return PromptService(engine=engine)


@lru_cache
def get_openrouter_provider() -> OpenRouterProvider:
    settings = get_settings()
    return OpenRouterProvider(api_key=settings.openrouter_api_key, model=settings.openrouter_model)


@lru_cache
def get_groq_provider() -> GroqProvider:
    settings = get_settings()
    return GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)


def get_chat_provider(name: str | None = None) -> ChatProvider:
    settings = get_settings()
    provider_name = name or settings.default_chat_provider
    if provider_name == "groq":
        return get_groq_provider()
    return get_openrouter_provider()


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


@lru_cache
def get_admin_service() -> AdminService:
    return AdminService(get_engine(), embedding_service=get_embedding_service())
