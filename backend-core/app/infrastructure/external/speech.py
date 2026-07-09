"""
Speech-to-Text service wrapper.
Infrastructure layer for Whisper speech recognition.
"""

from abc import ABC, abstractmethod

from app.core.logging import logger
from app.domain.exceptions import VoiceProcessingError, AudioProcessingError


class SpeechToTextService(ABC):
    """Abstract interface for speech-to-text services."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_bytes: Audio data in binary format

        Returns:
            Transcribed text

        Raises:
            AudioProcessingError: If transcription fails
        """
        pass


class WhisperSpeechService(SpeechToTextService):
    """
    Whisper-based speech-to-text service.
    Wraps the existing SpeechService.
    """

    def __init__(self, speech_service):
        """
        Initialize Whisper service wrapper.

        Args:
            speech_service: Instance of app.services.speech_service.SpeechService
        """
        self._speech_service = speech_service
        self.logger = logger

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio using Whisper.

        Args:
            audio_bytes: Audio data in binary format (webm, ogg, etc)

        Returns:
            Transcribed text

        Raises:
            AudioProcessingError: If transcription fails
        """
        if not audio_bytes:
            raise AudioProcessingError("No audio data provided")

        try:
            self.logger.info(f"Transcribing audio: {len(audio_bytes)} bytes")
            transcript = self._speech_service.transcribe(audio_bytes)

            if not transcript:
                self.logger.warning("Whisper returned empty transcription")
                return "[No speech detected]"

            self.logger.info(f"✓ Transcription: {transcript}")
            return transcript

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}", exc_info=True)
            raise AudioProcessingError(f"Failed to transcribe audio: {str(e)}") from e
