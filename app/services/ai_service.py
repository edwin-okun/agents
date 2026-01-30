import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.exceptions import (
    AIServiceException,
    AIServiceUnavailableException,
    AITimeoutException,
    InsufficientBalanceException,
    InvalidAPIKeyException,
    RateLimitException,
)
from app.core.settings import settings

logger = logging.getLogger(__name__)

deepseek_client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_api_base_url,
)


class AIService:
    def __init__(self):
        self.client = deepseek_client

    async def chat(self, message: str) -> dict:
        """
        Send a chat message to the AI service.

        Args:
            message: The user's message

        Returns:
            dict: Response containing the AI's message

        Raises:
            InsufficientBalanceException: When API account has insufficient balance
            RateLimitException: When rate limit is exceeded
            InvalidAPIKeyException: When API key is invalid
            AIServiceUnavailableException: When service is unavailable
            AITimeoutException: When request times out
            AIServiceException: For other AI service errors
        """
        try:
            logger.info("Sending chat request to AI service")
            response = await self.client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[{"role": "user", "content": message}],
            )
            logger.info("Successfully received response from AI service")
            return {"message": response.choices[0].message.content}

        except APIStatusError as e:
            # Handle specific HTTP status errors from OpenAI
            logger.error(
                f"OpenAI API status error: {e.status_code} - {e.message}", exc_info=True
            )

            if e.status_code == 402:
                # Insufficient balance
                raise InsufficientBalanceException()
            elif e.status_code == 401:
                # Invalid API key
                raise InvalidAPIKeyException()
            elif e.status_code == 429:
                # Rate limit exceeded
                raise RateLimitException()
            elif e.status_code >= 500:
                # Server errors
                raise AIServiceUnavailableException(
                    f"AI service is experiencing issues (Status: {e.status_code})"
                )
            else:
                # Other status errors
                raise AIServiceException(
                    message=f"AI service error: {e.message}",
                    status_code=e.status_code,
                    error_code="api_error",
                )

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}", exc_info=True)
            raise RateLimitException()

        except APITimeoutError as e:
            logger.error(f"OpenAI timeout error: {e}", exc_info=True)
            raise AITimeoutException()

        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}", exc_info=True)
            raise AIServiceUnavailableException(
                "Unable to connect to AI service. Please check your internet connection."
            )

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in AI service: {e}", exc_info=True)
            raise AIServiceException(
                message="An unexpected error occurred while processing your request.",
                status_code=500,
                error_code="internal_error",
            )
