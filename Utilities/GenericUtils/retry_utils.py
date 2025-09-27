import time
from functools import wraps

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


def retry(max_attempts: int = 3, delay: int = 2, backoff: int = 2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.
    max_attempts: number of retries
    delay: initial delay in seconds
    backoff: multiplier (2 = doubles each retry)
    Example Uses:
        from Utilities.GenericUtils.retry_utils import retry

        @retry(max_attempts=3, delay=1)
        def flaky_function():
            # do something that may fail
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    logger.error("[Retry] Attempt %d failed: %s. Retrying in %ds...", attempt, e, _delay)
                    time.sleep(_delay)
                    _delay *= backoff
            return None  # This should never be reached, but satisfies pylint

        return wrapper

    return decorator
