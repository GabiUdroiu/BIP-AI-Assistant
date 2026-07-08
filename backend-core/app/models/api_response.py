from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Unified API response model - matches frontend and backend.

    Examples:
    Success: {"data": {...}, "error": null, "error_code": null}
    Error: {"data": null, "error": "User error message", "error_code": "FIELD_VALIDATION_ERROR"}
    """

    data: Optional[T] = Field(default=None, description="Response payload")
    error: Optional[str] = Field(default=None, description="Human-readable error message")
    error_code: Optional[str] = Field(default=None, description="Machine-readable error code")

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        """Create a successful response."""
        return cls(data=data)

    @classmethod
    def fail(cls, error: str, error_code: Optional[str] = None) -> "ApiResponse[T]":
        """Create an error response."""
        return cls(error=error, error_code=error_code)

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.error is None and self.data is not None

    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.error is not None
