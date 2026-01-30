"""Custom exceptions for the application."""


class AIServiceException(Exception):
    """Base exception for AI service errors."""

    def __init__(
        self, message: str, status_code: int = 500, error_code: str = "ai_service_error"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class InsufficientBalanceException(AIServiceException):
    """Raised when OpenAI API returns insufficient balance error."""

    def __init__(
        self,
        message: str = "AI service has insufficient balance. Please contact support.",
    ):
        super().__init__(
            message=message, status_code=402, error_code="insufficient_balance"
        )


class RateLimitException(AIServiceException):
    """Raised when OpenAI API rate limit is exceeded."""

    def __init__(
        self, message: str = "AI service rate limit exceeded. Please try again later."
    ):
        super().__init__(
            message=message, status_code=429, error_code="rate_limit_exceeded"
        )


class InvalidAPIKeyException(AIServiceException):
    """Raised when OpenAI API key is invalid."""

    def __init__(
        self, message: str = "AI service configuration error. Please contact support."
    ):
        super().__init__(message=message, status_code=500, error_code="invalid_api_key")


class AIServiceUnavailableException(AIServiceException):
    """Raised when OpenAI API is unavailable."""

    def __init__(
        self,
        message: str = "AI service is temporarily unavailable. Please try again later.",
    ):
        super().__init__(
            message=message, status_code=503, error_code="service_unavailable"
        )


class AITimeoutException(AIServiceException):
    """Raised when OpenAI API request times out."""

    def __init__(
        self, message: str = "AI service request timed out. Please try again."
    ):
        super().__init__(message=message, status_code=504, error_code="request_timeout")
