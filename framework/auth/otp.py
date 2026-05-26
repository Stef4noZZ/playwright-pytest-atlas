"""TOTP code generation.

`pyotp` is an optional dependency — install with `pip install -e ".[auth]"`.
Tests that need OTP should skip cleanly when `pyotp` is not installed and
when no OTP secret is configured.
"""

from __future__ import annotations

import hashlib
from typing import Literal

try:
    import pyotp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dep
    pyotp = None


OTPAlgorithm = Literal["SHA1", "SHA256", "SHA512"]

_ALGORITHM_MAP = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512,
}


def is_otp_available() -> bool:
    return pyotp is not None


def generate_totp(secret: str, algorithm: OTPAlgorithm = "SHA512") -> str:
    """Return the current TOTP code for the given base32 secret."""
    if pyotp is None:
        raise RuntimeError("pyotp is not installed. Install with: pip install -e '.[auth]'")

    digest = _ALGORITHM_MAP.get(algorithm.upper())
    if digest is None:
        raise ValueError(
            f"Unsupported OTP algorithm: {algorithm}. Supported: {list(_ALGORITHM_MAP.keys())}"
        )

    code: str = pyotp.TOTP(secret, digest=digest).now()
    return code
