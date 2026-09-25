from __future__ import annotations

from framework.auth.otp import seconds_until_next_window
from framework.auth.token_cache import Token, TokenCache


def test_seconds_until_next_window_at_step_boundary() -> None:
    assert seconds_until_next_window(30, now=30.0) == 31


def test_seconds_until_next_window_near_end_of_step() -> None:
    assert seconds_until_next_window(30, now=59.0) == 2


def test_token_with_short_expires_in_is_not_reused() -> None:
    cache = TokenCache(ttl_seconds=900)
    cache.get_or_fetch(lambda: Token("access", expires_in=10))
    assert cache.is_valid() is False


def test_token_within_expires_in_is_reused() -> None:
    cache = TokenCache(ttl_seconds=900)
    first = cache.get_or_fetch(lambda: Token("access", expires_in=300))
    second = cache.get_or_fetch(lambda: Token("other", expires_in=300))
    assert second.access_token == first.access_token
    assert cache.is_valid() is True


def test_token_without_expires_in_uses_ttl() -> None:
    cache = TokenCache(ttl_seconds=120)
    cache.get_or_fetch(lambda: Token("access"))
    assert cache.is_valid() is True
