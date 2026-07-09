"""
Chat application service.
Unified interface for chat operations using use cases.
"""

from app.core.logging import logger
from app.domain.exceptions import ChatError
from app.application.use_cases import ChatWithContextUseCase


class ChatApplicationService:
    """
    Application service for chat operations.
    Coordinates chat-related use cases.
    """

    def __init__(self, chat_use_case: ChatWithContextUseCase):
        """
        Initialize chat application service.

        Args:
            chat_use_case: Use case for chat with context
        """
        self._chat = chat_use_case
        self.logger = logger

    def send_message(
        self,
        message: str,
        session_id: str = "default",
    ) -> dict:
        """
        Send a chat message and get response.

        Args:
            message: User message/question
            session_id: Conversation session identifier

        Returns:
            Dict with 'response' key or 'error'
        """
        try:
            self.logger.info(f"Chat application service: Processing message: {message[:100]}...")
            response = self._chat.execute(
                user_message=message,
                session_id=session_id,
            )
            return {
                "success": True,
                "response": response,
            }
        except ChatError as e:
            self.logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_conversation_history(self, session_id: str = "default") -> dict:
        """
        Get conversation history for a session.

        Args:
            session_id: Conversation session identifier

        Returns:
            Dict with 'history' key containing list of messages
        """
        try:
            # This would retrieve from conversation_service
            # For now, return structured response
            return {
                "success": True,
                "session_id": session_id,
                "history": [],  # Would be populated from service
            }
        except Exception as e:
            self.logger.error(f"Failed to get history: {e}")
            return {
                "success": False,
                "error": str(e),
            }
