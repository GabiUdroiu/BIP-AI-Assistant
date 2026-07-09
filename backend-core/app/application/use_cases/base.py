"""
Base use case interface.
Defines contract for all business logic use cases.
"""

from abc import ABC, abstractmethod


class UseCase(ABC):
    """
    Base class for all use cases.
    Represents a single business operation.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the use case."""
        pass
