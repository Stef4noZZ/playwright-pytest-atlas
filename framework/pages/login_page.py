"""UI login placeholder.

Defaults match a Keycloak-style two-step login (username -> password ->
optional OTP). Override class attributes or methods for your real app.
"""

from __future__ import annotations

import time

from playwright.sync_api import Locator, TimeoutError as PWTimeout, expect

from framework.auth.otp import generate_totp
from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    url_path = "/"

    username_label = "Username or email"
    password_label = "Password"
    otp_label = "One-time code"
    submit_button_name = "Sign In"

    otp_max_attempts = 3
    otp_window_sleep_seconds = 31
    otp_retry_sleep_seconds = 2
    otp_visibility_timeout_ms = 3_000

    @property
    def username_input(self) -> Locator:
        return self.page.get_by_label(self.username_label)

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_label(self.password_label, exact=True)

    @property
    def otp_input(self) -> Locator:
        return self.page.get_by_label(self.otp_label)

    @property
    def submit_button(self) -> Locator:
        return self.page.get_by_role("button", name=self.submit_button_name)

    def wait_for_loaded(self) -> None:
        expect(self.username_input).to_be_visible()

    def login(
        self,
        username: str,
        password: str,
        otp_secret: str | None = None,
        expect_success_url_contains: str | None = None,
    ) -> None:
        """Run the full UI login flow with optional OTP handling."""
        self.log.info("ui_login_start", username=username)

        self.username_input.fill(username)
        self.submit_button.click()

        self.password_input.fill(password)
        self.submit_button.click()

        if otp_secret:
            self._handle_otp(otp_secret)

        if expect_success_url_contains:
            self.page.wait_for_url(f"**{expect_success_url_contains}**")

        self.log.info("ui_login_complete")

    def logout(self, avatar_selector: str = '[data-test="avatar"]', menu_text: str = "Logout") -> None:
        """Best-effort UI logout. Override per app."""
        try:
            self.page.locator(avatar_selector).click()
            self.page.get_by_text(menu_text).click()
        except Exception as exc:
            self.log.warning("ui_logout_failed", error=str(exc))

    def _handle_otp(self, otp_secret: str) -> None:
        if not self._is_otp_required():
            return

        for attempt in range(self.otp_max_attempts):
            if attempt > 0:
                time.sleep(self.otp_window_sleep_seconds)

            code = generate_totp(otp_secret)
            self.otp_input.clear()
            self.otp_input.fill(code)
            self.submit_button.click()

            if not self._is_otp_required():
                return

            time.sleep(self.otp_retry_sleep_seconds)

        raise AssertionError(f"OTP authentication failed after {self.otp_max_attempts} attempts")

    def _is_otp_required(self) -> bool:
        try:
            return self.otp_input.is_visible(timeout=self.otp_visibility_timeout_ms)
        except PWTimeout:
            return False
