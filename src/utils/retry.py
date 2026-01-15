"""Retry utility with exponential backoff"""
import time
from functools import wraps
from typing import Callable, Type, Tuple
from retrying import retry as retrying_decorator


# Define default retry exceptions
DEFAULT_RETRY_EXCEPTIONS = (
    Exception,
)


def retry(
    max_attempts: int = 3,
    wait_exponential_multiplier: int = 1000,
    wait_exponential_max: int = 4000,
    retry_on_exception: Callable[[Exception], bool] = None,
    stop_max_attempt_number: int = 3,
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        wait_exponential_multiplier: Base wait time in milliseconds (default: 1000)
        wait_exponential_max: Maximum wait time in milliseconds (default: 4000)
        retry_on_exception: Function that returns True if exception should trigger retry
        stop_max_attempt_number: Maximum number of attempts (alias for max_attempts)

    Returns:
        Decorated function with retry logic

    Example:
        @retry(max_attempts=3)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        return retrying_decorator(
            wait_exponential_multiplier=wait_exponential_multiplier,
            wait_exponential_max=wait_exponential_max,
            stop_max_attempt_number=stop_max_attempt_number,
            retry_on_exception=retry_on_exception or _should_retry_exception
        )(func)

    return decorator


def _should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry

    Args:
        exception: The exception to evaluate

    Returns:
        True if exception should trigger retry, False otherwise
    """
    # By default, retry on all exceptions except KeyboardInterrupt
    return not isinstance(exception, KeyboardInterrupt)


def retry_on_specific_exceptions(
    *exception_types: Type[Exception],
    max_attempts: int = 3,
) -> Callable:
    """
    Decorator for retrying on specific exceptions only

    Args:
        *exception_types: Exception types to retry on
        max_attempts: Maximum number of retry attempts

    Returns:
        Decorated function with retry logic

    Example:
        @retry_on_specific_exceptions(ConnectionError, TimeoutError, max_attempts=3)
        def connect_to_db():
            pass
    """
    def should_retry(exception: Exception) -> bool:
        return isinstance(exception, exception_types)

    return retry(
        max_attempts=max_attempts,
        retry_on_exception=should_retry
    )
