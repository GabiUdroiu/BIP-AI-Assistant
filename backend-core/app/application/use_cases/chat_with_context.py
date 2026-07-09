"""
Chat with context use case.
Handles chat interactions with conversation history and RAG retrieval.
"""

from app.application.use_cases.base import UseCase
from app.core.logging import logger
from app.domain.exceptions import ChatError, ContextRetrievalError, ExternalServiceError


class ChatWithContextUseCase(UseCase):
    """
    Use case for chat interactions with context.
    Retrieves relevant context from RAG, builds conversation history,
    and gets response from LLM.
    """

    def __init__(
        self,
        chat_provider,
        conversation_service,
        rag_service,
        prompt_service,
    ):
        """
        Initialize chat use case.

        Args:
            chat_provider: LLM provider instance
            conversation_service: Service for managing conversation history
            rag_service: RAG service for context retrieval
            prompt_service: Service for system prompts
        """
        self._chat_provider = chat_provider
        self._conversation_service = conversation_service
        self._rag_service = rag_service
        self._prompt_service = prompt_service
        self.logger = logger

    def execute(
        self,
        user_message: str,
        session_id: str = "default",
    ) -> str:
        """
        Execute chat with context.

        Args:
            user_message: User's message/question
            session_id: Conversation session identifier

        Returns:
            Chat response from LLM

        Raises:
            ChatError: If chat processing fails
        """
        if not user_message or not user_message.strip():
            raise ChatError("Empty message provided")

        try:
            self.logger.info(f"Processing chat: {user_message[:100]}...")

            # Get system prompt (with strict brevity enforced)
            system_prompt = self._prompt_service.get_system_prompt()
            system_prompt += "\n\n⚠️ STRICT: Keep ALL responses to 2-3 sentences MAXIMUM. No long explanations."
            self.logger.debug("Retrieved system prompt")

            # Get conversation history
            history = self._conversation_service.get_history(session_id)
            self.logger.debug(f"Retrieved {len(history)} history messages")

            # Build messages for LLM
            messages = [
                {"role": "system", "content": system_prompt},
                *history,
                {"role": "user", "content": user_message},
            ]

            # Get response from LLM
            self.logger.info("Requesting response from LLM...")
            reply = self._chat_provider.reply(messages)

            if not reply:
                raise ChatError("Empty response from LLM")

            self.logger.info(f"✓ Chat response: {reply[:100]}...")

            # Save to conversation history
            self._conversation_service.save_message(session_id, "user", user_message)
            self._conversation_service.save_message(session_id, "assistant", reply)
            self.logger.debug("Saved messages to conversation history")

            return reply

        except ExternalServiceError as e:
            self.logger.error(f"External service error: {e}")
            raise ChatError(f"Service unavailable: {str(e)}") from e
        except ChatError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during chat: {e}", exc_info=True)
            raise ChatError(f"Chat processing failed: {str(e)}") from e
