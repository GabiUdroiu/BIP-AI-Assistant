"""
Embeddings service wrapper.
Infrastructure layer for text embedding generation.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.core.logging import logger
from app.domain.exceptions import ExternalServiceError


class EmbeddingService(ABC):
    """Abstract interface for embedding services."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            ExternalServiceError: If embedding fails
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ExternalServiceError: If embedding fails
        """
        pass


class OpenRouterEmbeddingService(EmbeddingService):
    """
    OpenRouter-based embedding service.
    Wraps the existing EmbeddingService.
    """

    def __init__(self, embedding_service):
        """
        Initialize OpenRouter embedding service wrapper.

        Args:
            embedding_service: Instance of app.services.embedding_service.EmbeddingService
        """
        self._embedding_service = embedding_service or EmbeddingService()
        self.logger = logger

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            ExternalServiceError: If embedding fails
        """
        if not text:
            raise ExternalServiceError("Empty text provided for embedding")

        try:
            self.logger.debug(f"Embedding text: {text[:100]}...")
            embedding = self._embedding_service.embed_text(text)

            if not embedding:
                raise ExternalServiceError("Empty embedding returned")

            self.logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            self.logger.error(f"Embedding failed: {e}", exc_info=True)
            raise ExternalServiceError(f"Failed to embed text: {str(e)}") from e

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ExternalServiceError: If embedding fails
        """
        if not texts:
            raise ExternalServiceError("Empty text list provided for embedding")

        try:
            self.logger.debug(f"Embedding batch of {len(texts)} texts")
            embeddings = [self.embed_text(text) for text in texts]
            self.logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except ExternalServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Batch embedding failed: {e}", exc_info=True)
            raise ExternalServiceError(f"Failed to embed batch: {str(e)}") from e
