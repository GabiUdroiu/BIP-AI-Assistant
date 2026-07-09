"""
Centralized error handling for presentation layer.
Converts domain exceptions to HTTP responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.domain.exceptions import (
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
from app.presentation.api.v1.schemas import ErrorResponse, ValidationErrorResponse
from app.core.logging import logger


def register_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI app."""

    # ============ Domain Exceptions ============

    @app.exception_handler(VoiceProcessingError)
    async def voice_processing_error_handler(request: Request, exc: VoiceProcessingError):
        logger.error(f"Voice processing error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(exc),
                "error_code": "VOICE_PROCESSING_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(AudioProcessingError)
    async def audio_processing_error_handler(request: Request, exc: AudioProcessingError):
        logger.error(f"Audio processing error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(exc),
                "error_code": "AUDIO_PROCESSING_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(ChatError)
    async def chat_error_handler(request: Request, exc: ChatError):
        logger.error(f"Chat error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": str(exc),
                "error_code": "CHAT_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(ContextRetrievalError)
    async def context_retrieval_error_handler(request: Request, exc: ContextRetrievalError):
        logger.error(f"Context retrieval error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": str(exc),
                "error_code": "CONTEXT_RETRIEVAL_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(request: Request, exc: ConfigurationError):
        logger.error(f"Configuration error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": str(exc),
                "error_code": "CONFIGURATION_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(ExternalServiceError)
    async def external_service_error_handler(request: Request, exc: ExternalServiceError):
        logger.error(f"External service error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": str(exc),
                "error_code": "EXTERNAL_SERVICE_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": str(exc),
                "error_code": "DATABASE_ERROR",
                "details": None,
            },
        )

    @app.exception_handler(ConversationNotFoundError)
    async def conversation_not_found_error_handler(request: Request, exc: ConversationNotFoundError):
        logger.error(f"Conversation not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": str(exc),
                "error_code": "CONVERSATION_NOT_FOUND",
                "details": None,
            },
        )

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        logger.error(f"Application error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": str(exc),
                "error_code": "APPLICATION_ERROR",
                "details": None,
            },
        )

    # ============ Pydantic Validation Errors ============

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": [
                    {
                        "loc": list(error["loc"]),
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ],
            },
        )

    # ============ General Exception Handler ============

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": None,
            },
        )
