"""
API Request/Response schemas.
Pydantic models for input validation and response formatting.
"""

from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar


T = TypeVar('T')


# ============ Generic Response ============

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    def is_success(self) -> bool:
        """Check if response is successful."""
        return self.error is None


# ============ Voice Endpoints ============

class VoiceProcessRequest(BaseModel):
    """Request for voice processing endpoint."""
    # Audio is sent as binary, not in JSON


class VoiceProcessResponse(BaseModel):
    """Response from voice processing."""
    message: str = Field(..., description="Transcribed text from audio")


class StreamVoiceRequest(BaseModel):
    """WebSocket streaming request."""
    # Audio is sent as binary over WebSocket


class StreamVoiceResponse(BaseModel):
    """WebSocket streaming response."""
    type: str = Field(..., description="Message type: transcript, chat_response, or error")
    text: Optional[str] = None
    interim: Optional[bool] = None
    original_transcript: Optional[str] = None
    message: Optional[str] = None  # For error messages


# ============ Chat Endpoints ============

class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(default="default", description="Session identifier")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    reply: str = Field(..., description="Assistant reply")
    session_id: str = Field(..., description="Session identifier")


class ConversationMessage(BaseModel):
    """Message in conversation history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history."""
    session_id: str
    messages: list[ConversationMessage]


# ============ Admin Endpoints ============

class TableInfo(BaseModel):
    """Information about a database table."""
    name: str
    row_count: int
    columns: Optional[int] = None


class TablesResponse(BaseModel):
    """Response with database tables info."""
    tables: list[TableInfo]


# ============ Error Responses ============

class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str
    error_code: str
    details: Optional[dict] = None


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    loc: list
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    error: str = "Validation failed"
    error_code: str = "VALIDATION_ERROR"
    details: list[ValidationErrorDetail]
