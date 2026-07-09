"""
Voice application service.
Unified interface for voice operations using use cases.
"""

from app.core.logging import logger
from app.domain.exceptions import VoiceProcessingError
from app.application.use_cases import ProcessVoiceUseCase, StreamVoiceUseCase


class VoiceApplicationService:
    """
    Application service for voice operations.
    Coordinates voice-related use cases.
    """

    def __init__(
        self,
        process_voice_use_case: ProcessVoiceUseCase,
        stream_voice_use_case: StreamVoiceUseCase,
    ):
        """
        Initialize voice application service.

        Args:
            process_voice_use_case: Use case for voice processing
            stream_voice_use_case: Use case for voice streaming
        """
        self._process_voice = process_voice_use_case
        self._stream_voice = stream_voice_use_case
        self.logger = logger

    def process_voice_message(self, audio_bytes: bytes) -> dict:
        """
        Process a voice message (one-shot).

        Args:
            audio_bytes: Audio data

        Returns:
            Dict with 'transcript' key or 'error'
        """
        try:
            self.logger.info("Voice application service: Processing voice message")
            transcript = self._process_voice.execute(audio_bytes)
            return {
                "success": True,
                "transcript": transcript,
            }
        except VoiceProcessingError as e:
            self.logger.error(f"Voice processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def stream_voice_chunk(
        self,
        audio_bytes: bytes,
        session_id: str = "default",
    ) -> dict:
        """
        Process a voice stream chunk.

        Args:
            audio_bytes: Audio data chunk
            session_id: Session identifier

        Returns:
            Dict with 'transcript', 'response', and optional 'error'
        """
        try:
            self.logger.info("Voice application service: Processing stream chunk")
            result = self._stream_voice.execute(
                audio_bytes=audio_bytes,
                session_id=session_id,
            )
            return {
                "success": result["error"] is None,
                "transcript": result["transcript"],
                "response": result["response"],
                "error": result["error"],
            }
        except Exception as e:
            self.logger.error(f"Stream processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }
