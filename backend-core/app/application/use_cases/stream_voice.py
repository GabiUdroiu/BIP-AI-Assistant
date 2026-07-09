"""
Stream voice use case.
Handles continuous voice streaming with transcription and chat responses.
"""

from app.application.use_cases.base import UseCase
from app.application.use_cases.process_voice import ProcessVoiceUseCase
from app.application.use_cases.chat_with_context import ChatWithContextUseCase
from app.core.logging import logger
from app.domain.exceptions import VoiceProcessingError, ChatError


class StreamVoiceUseCase(UseCase):
    """
    Use case for streaming voice input.
    Processes audio chunks, transcribes them, and generates chat responses.
    """

    def __init__(
        self,
        process_voice_use_case: ProcessVoiceUseCase,
        chat_use_case: ChatWithContextUseCase,
    ):
        """
        Initialize stream voice use case.

        Args:
            process_voice_use_case: Voice processing use case instance
            chat_use_case: Chat use case instance
        """
        self._process_voice = process_voice_use_case
        self._chat = chat_use_case
        self.logger = logger

    def execute(
        self,
        audio_bytes: bytes,
        session_id: str = "default",
    ) -> dict:
        """
        Execute voice streaming.

        Args:
            audio_bytes: Audio data to process
            session_id: Session identifier for conversation

        Returns:
            Dict with 'transcript' and 'response' keys

        Raises:
            VoiceProcessingError: If voice processing fails
            ChatError: If chat processing fails
        """
        result = {
            "transcript": None,
            "response": None,
            "error": None,
        }

        try:
            # Step 1: Process voice - transcribe audio
            self.logger.info("Step 1: Processing voice...")
            try:
                transcript = self._process_voice.execute(audio_bytes)
                result["transcript"] = transcript
                self.logger.info(f"✓ Transcription: {transcript}")
            except VoiceProcessingError as e:
                result["error"] = f"Voice processing failed: {str(e)}"
                self.logger.error(result["error"])
                return result

            # Step 2: Get chat response
            self.logger.info("Step 2: Getting chat response...")
            try:
                response = self._chat.execute(
                    user_message=transcript,
                    session_id=session_id,
                )
                result["response"] = response
                self.logger.info(f"✓ Chat response: {response[:100]}...")
            except ChatError as e:
                result["error"] = f"Chat failed: {str(e)}"
                self.logger.error(result["error"])
                # Still return transcript even if chat fails
                return result

            self.logger.info("✓ Voice streaming complete")
            return result

        except Exception as e:
            self.logger.error(f"Unexpected error during voice streaming: {e}", exc_info=True)
            result["error"] = f"Unexpected error: {str(e)}"
            return result
