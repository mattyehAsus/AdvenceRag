import asyncio
import logging
from typing import TypeVar, Callable, Any, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    **kwargs: Any
) -> T:
    """
    Retry an async function with exponential backoff on Gemini 429 and 503 errors.
    """
    delay = initial_delay
    for i in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "ResourceExhausted" in error_str or "Too Many Requests" in error_str
            is_overloaded = "503" in error_str or "Overloaded" in error_str or "Service Unavailable" in error_str
            
            if (is_rate_limit or is_overloaded) and i < max_retries:
                error_type = "Rate Limit (429)" if is_rate_limit else "Model Overloaded (503)"
                logger.warning(f"Gemini {error_type} detected. Retrying in {delay}s... (Attempt {i+1}/{max_retries})")
                await asyncio.sleep(delay)
                delay *= backoff_factor
                continue
            
            # Max retries reached or not a retryable error
            if i == max_retries:
                logger.error(f"Max retries ({max_retries}) reached. Final error: {e}")
            raise
