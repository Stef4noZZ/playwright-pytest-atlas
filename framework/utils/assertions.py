"""Soft-assertion helpers for accumulating multiple checks within a single test."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


class SoftAssert:
    def __init__(self) -> None:
        self._errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self._errors.append(message)

    def equals(self, actual: Any, expected: Any, message: str | None = None) -> None:
        if actual != expected:
            self._errors.append(message or f"expected {expected!r}, got {actual!r}")

    def not_equals(self, actual: Any, expected: Any, message: str | None = None) -> None:
        if actual == expected:
            self._errors.append(message or f"expected value other than {expected!r}")

    def is_truthy(self, value: Any, message: str | None = None) -> None:
        if not value:
            self._errors.append(message or f"expected truthy value, got {value!r}")

    def assert_all(self) -> None:
        if self._errors:
            joined = "\n  - ".join(self._errors)
            raise AssertionError(f"Soft assertion failures:\n  - {joined}")


@contextmanager
def soft_assertions() -> Generator[SoftAssert, None, None]:
    sa = SoftAssert()
    yield sa
    sa.assert_all()
