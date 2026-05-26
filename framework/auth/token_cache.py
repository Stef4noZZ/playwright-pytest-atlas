"""In-process token cache with a configurable TTL.

Avoids re-authenticating once per test. Replace with a Redis-backed cache if
you need to share tokens across xdist workers.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    access_token: str
    refresh_token: str | None = None
    issued_at: float = 0.0


class TokenCache:
    def __init__(self, ttl_seconds: int = 15 * 60) -> None:
        self._ttl = ttl_seconds
        self._token: Token | None = None

    def is_valid(self) -> bool:
        if self._token is None:
            return False
        return (time.time() - self._token.issued_at) < self._ttl

    def get_or_fetch(self, fetcher: Callable[[], Token]) -> Token:
        if self.is_valid():
            assert self._token is not None
            return self._token
        token = fetcher()
        self._token = Token(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            issued_at=time.time(),
        )
        return self._token

    def clear(self) -> None:
        self._token = None
