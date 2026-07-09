"""
Process voice/audio use case.
Handles transcription of audio to text.
"""

from app.application.use_cases.base import UseCase
from app.core.logging import logger
from app.domain.exceptions import AudioProcessingError, VoiceProcessingError
from app.infrastructure.external import SpeechToTextService


class ProcessVoiceUseCase(UseCase):
    """
    Use case for processing voice input.
    Transcribes audio to text using speech-to-text service.
    """

    def __init__(self, speech_service: SpeechToTextService):
        """
        Initialize voice processing use case.

        Args:
            speech_service: Speech-to-text service instance
        """
        self._speech_service = speech_service
        self.logger = logger

    def execute(self, audio_bytes: bytes) -> str:
        """
        Execute voice processing.

        Args:
            audio_bytes: Raw audio data (webm, ogg, etc)

        Returns:
            Transcribed text

        Raises:
            VoiceProcessingError: If processing fails
        """
        if not audio_bytes:
            raise VoiceProcessingError("No audio data provided")

        try:
            self.logger.info(f"Processing voice: {len(audio_bytes)} bytes")

            # Transcribe audio
            transcript = self._speech_service.transcribe(audio_bytes)

            if not transcript or transcript == "[No speech detected]":
                self.logger.warning("No speech detected in audio")
                raise VoiceProcessingError("No speech detected in audio")

            self.logger.info(f"✓ Voice processing complete: {transcript[:100]}...")
            return transcript

        except AudioProcessingError as e:
            self.logger.error(f"Audio processing failed: {e}")
            raise VoiceProcessingError(f"Failed to process voice: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during voice processing: {e}", exc_info=True)
            raise VoiceProcessingError(f"Unexpected error: {str(e)}") from e
