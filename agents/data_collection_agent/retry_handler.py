import time
from collections.abc import Callable


def with_retry(operation: Callable, attempts: int = 2, delay: float = 0.25):
    last_error = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(delay * (attempt + 1))
    if last_error:
        raise last_error
