from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")

RETRYABLE = ("ratelimit", "rate limit", "429", "json_validate_failed", "does not match", "parsing failed")


def is_retryable(error: Exception) -> bool:
    message = str(error).lower()
    return any(token in message for token in RETRYABLE)


def with_retry(call: Callable[[], T], attempts: int = 5, base_delay: float = 4.0) -> T:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return call()
        except Exception as error:
            if not is_retryable(error):
                raise
            last = error
            if attempt == attempts - 1:
                break
            time.sleep(base_delay * (2**attempt) + random.uniform(0, 1.5))
    assert last is not None
    raise last
