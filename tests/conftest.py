from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright.sync_api import Page, Playwright

from playwright.sync_api import APIRequestContext

from config.settings import Settings, get_settings
from framework.api.auth_client import AuthClient
from framework.api.example_client import JsonPlaceholderClient
from framework.auth.token_cache import Token
from framework.pages.example_page import PlaywrightHomePage
from framework.pages.login_page import LoginPage
from framework.utils.logger import configure_logging


def pytest_configure(config: pytest.Config) -> None:
    configure_logging()


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    return str(settings.base_url).rstrip("/")


@pytest.fixture(scope="session")
def api_base_url(settings: Settings) -> str:
    return str(settings.api_base_url).rstrip("/")


@pytest.fixture(scope="session")
def credentials(settings: Settings) -> tuple[str, str]:
    """Return (username, password) or skip when not configured."""
    if not settings.username or not settings.password:
        pytest.skip("auth credentials not configured (set QA_USERNAME and QA_PASSWORD)")
    return settings.username, settings.password.get_secret_value()


@pytest.fixture(scope="session")
def otp_secret(settings: Settings) -> str | None:
    return settings.otp_secret.get_secret_value() if settings.otp_secret else None


# ---------------------------------------------------------------------------
# Playwright wiring (pytest-playwright fixture overrides)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    return {
        **browser_type_launch_args,
        "headless": settings.headless,
        "slow_mo": settings.slow_mo_ms,
    }


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any],
    settings: Settings,
    storage_state_path: Path | None,
) -> dict[str, Any]:
    args: dict[str, Any] = {
        **browser_context_args,
        "base_url": str(settings.base_url).rstrip("/"),
        "ignore_https_errors": True,
        "record_video_dir": (
            str(settings.artifacts_dir / "videos") if settings.record_video else None
        ),
    }
    if storage_state_path is not None:
        args["storage_state"] = str(storage_state_path)
    return args


@pytest.fixture
def page(page: Page, settings: Settings) -> Page:
    page.set_default_timeout(settings.default_timeout_ms)
    page.set_default_navigation_timeout(settings.navigation_timeout_ms)
    return page


# ---------------------------------------------------------------------------
# Sample page objects and API clients
#
# Shared by UI, API, and e2e tests so cross-cutting flows can compose them.
# Project-specific fixtures should live next to the tests that use them
# (tests/ui/conftest.py, tests/api/conftest.py).
# ---------------------------------------------------------------------------


@pytest.fixture
def home_page(page: Page, base_url: str) -> PlaywrightHomePage:
    return PlaywrightHomePage(page, base_url)


@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright, api_base_url: str
) -> Generator[APIRequestContext, None, None]:
    request = playwright.request.new_context(base_url=api_base_url)
    yield request
    request.dispose()


@pytest.fixture
def jsonplaceholder(
    api_request_context: APIRequestContext, api_base_url: str
) -> JsonPlaceholderClient:
    return JsonPlaceholderClient(api_request_context, api_base_url)


# ---------------------------------------------------------------------------
# Authentication fixtures
#
# All auth fixtures are opt-in. When credentials or endpoints are not
# configured they return `None` so anonymous test suites run unchanged.
# Tests that *require* auth depend on `credentials` (which skips cleanly).
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def storage_state_path(
    playwright: Playwright,
    settings: Settings,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path | None:
    """Log in once via the UI and persist the auth state for reuse across tests.

    Returns None when auth is not configured, in which case `browser_context_args`
    starts every context anonymously.
    """
    if not settings.username or not settings.password:
        return None

    state_file = tmp_path_factory.mktemp("auth") / "state.json"

    browser_name = settings.browser
    launcher = getattr(playwright, browser_name)
    browser = launcher.launch(headless=True)
    try:
        context = browser.new_context(base_url=str(settings.base_url).rstrip("/"))
        page = context.new_page()
        login = LoginPage(page, str(settings.base_url).rstrip("/"))
        login.open()
        login.login(
            username=settings.username,
            password=settings.password.get_secret_value(),
            otp_secret=settings.otp_secret.get_secret_value() if settings.otp_secret else None,
        )
        context.storage_state(path=state_file)
    finally:
        browser.close()

    return state_file


@pytest.fixture(scope="session")
def auth_client(
    playwright: Playwright, settings: Settings
) -> Generator[AuthClient | None, None, None]:
    """Provide an API auth client, or None when no `QA_AUTH_TOKEN_URL` is configured."""
    if not settings.auth_token_url:
        yield None
        return

    request = playwright.request.new_context()
    client = AuthClient(
        request=request,
        token_url=settings.auth_token_url,
        client_id=settings.auth_client_id,
        grant_type=settings.auth_grant_type,
    )
    try:
        yield client
    finally:
        request.dispose()


@pytest.fixture(scope="session")
def api_token(
    auth_client: AuthClient | None,
    credentials: tuple[str, str],
    otp_secret: str | None,
    settings: Settings,
) -> Generator[Token, None, None]:
    """Cached API access token. Skips when no auth endpoint is configured."""
    if auth_client is None:
        pytest.skip("API auth not configured (set QA_AUTH_TOKEN_URL)")

    username, password = credentials
    token = auth_client.authenticate(username, password, otp_secret)
    yield token
    auth_client.logout(token, logout_url=settings.auth_logout_url)


@pytest.fixture
def auth_headers(api_token: Token) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_token.access_token}"}


@pytest.fixture
def ui_login(
    page: Page,
    base_url: str,
    credentials: tuple[str, str],
    otp_secret: str | None,
) -> Generator[LoginPage, None, None]:
    """Per-test UI login. Use this when you need a fresh login flow rather
    than the session-wide `storage_state`.
    """
    username, password = credentials
    login = LoginPage(page, base_url)
    login.open()
    login.login(username=username, password=password, otp_secret=otp_secret)
    yield login
    login.logout()


# ---------------------------------------------------------------------------
# Failure capture
# ---------------------------------------------------------------------------


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, Any, None]:
    """Attach a screenshot to the Allure report when a UI test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page: Page | None = item.funcargs.get("page")  # type: ignore[assignment]
    if page is None:
        return

    try:
        allure.attach(
            page.screenshot(full_page=True),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            page.url,
            name="failure-url",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(
    item: pytest.Item, nextitem: pytest.Item | None
) -> Generator[None, Any, None]:
    """Safety backstop: clear cookies on the browser context after each test."""
    yield
    page: Page | None = item.funcargs.get("page")  # type: ignore[assignment]
    if page is None:
        return
    try:
        page.context.clear_cookies()
    except Exception:
        pass
