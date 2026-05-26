"""API authentication placeholder for OAuth2 / OIDC password grant.

Defaults match a Keycloak token endpoint
(`/auth/realms/{realm}/protocol/openid-connect/token`) but the URL is
fully configurable. Subclass for SAML, custom token exchanges, or PAT
flows.
"""

from __future__ import annotations

import time
from typing import Any

from playwright.sync_api import APIRequestContext

from framework.auth.otp import generate_totp, is_otp_available
from framework.auth.token_cache import Token, TokenCache
from framework.utils.logger import get_logger


class AuthClient:
    OTP_MAX_ATTEMPTS = 3
    OTP_WINDOW_SLEEP_SECONDS = 31

    def __init__(
        self,
        request: APIRequestContext,
        token_url: str,
        client_id: str = "ocp",
        grant_type: str = "password",
        cache: TokenCache | None = None,
    ) -> None:
        self.request = request
        self.token_url = token_url
        self.client_id = client_id
        self.grant_type = grant_type
        self.cache = cache or TokenCache()
        self.log = get_logger(self.__class__.__name__)

    def authenticate(
        self, username: str, password: str, otp_secret: str | None = None
    ) -> Token:
        """Return a Token, using the cache when valid and OTP retries when required."""
        return self.cache.get_or_fetch(
            lambda: self._fetch_token(username, password, otp_secret)
        )

    def logout(self, token: Token, logout_url: str | None = None) -> None:
        """Best-effort logout. Pass the matching OIDC logout endpoint via `logout_url`."""
        if not logout_url or not token.refresh_token:
            self.cache.clear()
            return

        try:
            self.request.post(
                logout_url,
                form={"client_id": self.client_id, "refresh_token": token.refresh_token},
            )
        except Exception as exc:
            self.log.warning("api_logout_failed", error=str(exc))
        finally:
            self.cache.clear()

    def _fetch_token(self, username: str, password: str, otp_secret: str | None) -> Token:
        last_error: Exception | None = None

        for attempt in range(self.OTP_MAX_ATTEMPTS):
            if attempt > 0 and otp_secret:
                time.sleep(self.OTP_WINDOW_SLEEP_SECONDS)

            payload = self._build_payload(username, password, otp_secret)
            response = self.request.post(self.token_url, form=payload)

            if response.ok:
                body: dict[str, Any] = response.json()
                self.log.info("api_login_success", username=username)
                return Token(
                    access_token=body["access_token"],
                    refresh_token=body.get("refresh_token"),
                )

            last_error = AssertionError(
                f"token endpoint returned {response.status} {response.status_text}: "
                f"{response.text()[:300]}"
            )

            if not otp_secret:
                break

        raise last_error or AssertionError("authentication failed")

    def _build_payload(
        self, username: str, password: str, otp_secret: str | None
    ) -> dict[str, str]:
        payload = {
            "username": username,
            "password": password,
            "client_id": self.client_id,
            "grant_type": self.grant_type,
        }
        if otp_secret:
            if not is_otp_available():
                raise RuntimeError(
                    "OTP secret provided but pyotp is not installed. "
                    "Install with: pip install -e '.[auth]'"
                )
            payload["otp"] = generate_totp(otp_secret)
        return payload
