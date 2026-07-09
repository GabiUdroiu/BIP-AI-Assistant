"""
Domain models - Core business entities.
Language: Python with Pydantic for validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============ Value Objects ============

class AudioSegment(BaseModel):
    """Represents an audio recording."""
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str = "webm"


class Transcript(BaseModel):
    """Represents a speech-to-text result."""
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    language: str = "en"
    interim: bool = False


class ChatResponse(BaseModel):
    """Represents a chat response."""
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


# ============ Entities ============

class Message(BaseModel):
    """Represents a message in a conversation."""
    id: Optional[str] = None
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None


class Conversation(BaseModel):
    """Represents a conversation session."""
    session_id: str
    messages: list[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None

    def add_message(self, role: str, content: str) -> Message:
        """Add a message to conversation."""
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg


class VoiceStreamSession(BaseModel):
    """Represents an active voice streaming session."""
    session_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    audio_segments: list[AudioSegment] = []
    full_transcript: str = ""
    metadata: Optional[dict] = None

    def add_audio_segment(self, segment: AudioSegment) -> None:
        """Add audio segment to session."""
        self.audio_segments.append(segment)

    def close(self) -> None:
        """Close the voice session."""
        self.is_active = False
