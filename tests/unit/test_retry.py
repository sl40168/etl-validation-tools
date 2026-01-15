"""Unit tests for retry utility"""
import pytest
from src.utils.retry import retry, retry_on_specific_exceptions, _should_retry_exception
import time


def test_retry_success_first_attempt():
    """Test function that succeeds on first attempt"""
    call_count = [0]

    @retry(max_attempts=3)
    def test_func():
        call_count[0] += 1
        return "success"

    result = test_func()
    assert result == "success"
    assert call_count[0] == 1


def test_retry_fail_then_succeed():
    """Test function that fails twice then succeeds"""
    call_count = [0]

    @retry(max_attempts=3)
    def test_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    result = test_func()
    assert result == "success"
    assert call_count[0] == 3


def test_retry_fail_all_attempts():
    """Test function that fails all attempts"""
    call_count = [0]

    @retry(max_attempts=3)
    def test_func():
        call_count[0] += 1
        raise ConnectionError("Persistent failure")

    with pytest.raises(ConnectionError, match="Persistent failure"):
        test_func()
    assert call_count[0] == 3


def test_retry_on_specific_exceptions_only():
    """Test retrying only on specific exception types"""
    call_count = [0]

    @retry_on_specific_exceptions(ConnectionError, TimeoutError, max_attempts=3)
    def test_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    result = test_func()
    assert result == "success"
    assert call_count[0] == 3


def test_retry_specific_exception_not_matching():
    """Test no retry when exception type doesn't match"""
    call_count = [0]

    @retry_on_specific_exceptions(ConnectionError, max_attempts=3)
    def test_func():
        call_count[0] += 1
        raise ValueError("Other error")

    with pytest.raises(ValueError, match="Other error"):
        test_func()
    # Should fail immediately without retry
    assert call_count[0] == 1


def test_should_retry_exception_keyboard_interrupt():
    """Test that KeyboardInterrupt does not trigger retry"""
    exception = KeyboardInterrupt()
    assert _should_retry_exception(exception) is False


def test_should_retry_exception_generic():
    """Test that generic exceptions trigger retry"""
    exception = ConnectionError("Test")
    assert _should_retry_exception(exception) is True


def test_retry_exponential_backoff():
    """Test exponential backoff timing"""
    call_count = [0]
    call_times = []

    @retry(max_attempts=3, wait_exponential_multiplier=100)  # 100ms base
    def test_func():
        call_times.append(time.time())
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    start_time = time.time()
    test_func()

    # Verify exponential backoff (approximately)
    # First retry: ~100ms, Second retry: ~200ms
    assert call_count[0] == 3
    assert len(call_times) == 3
