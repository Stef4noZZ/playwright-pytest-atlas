from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Type-safe runtime configuration sourced from environment variables.

    Override via real env vars or an `.env` file at the project root. All
    settings carry the `QA_` prefix to avoid collisions with framework defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="QA_",
        extra="ignore",
        case_sensitive=False,
    )

    environment: Literal["local", "dev", "staging", "prod"] = "local"

    base_url: HttpUrl = Field(default=HttpUrl("https://playwright.dev"))
    api_base_url: HttpUrl = Field(default=HttpUrl("https://jsonplaceholder.typicode.com"))

    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    slow_mo_ms: int = Field(default=0, ge=0)

    default_timeout_ms: int = Field(default=30_000, ge=0)
    navigation_timeout_ms: int = Field(default=30_000, ge=0)

    record_video: bool = False
    record_trace: Literal["off", "on", "retain-on-failure"] = "retain-on-failure"
    capture_screenshot: Literal["off", "on", "only-on-failure"] = "only-on-failure"

    api_key: SecretStr | None = None

    # Authentication. Leave blank to run tests anonymously.
    username: str | None = None
    password: SecretStr | None = None
    otp_secret: SecretStr | None = None

    # OAuth2 / OIDC. `auth_token_url` is the full token endpoint, e.g.
    # https://{host}/auth/realms/{realm}/protocol/openid-connect/token
    auth_token_url: str | None = None
    auth_logout_url: str | None = None
    auth_client_id: str = "ocp"
    auth_grant_type: str = "password"

    artifacts_dir: Path = Field(default=Path("reports"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
