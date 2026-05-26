from __future__ import annotations

from playwright.sync_api import Locator, expect

from framework.pages.base_page import BasePage


class PlaywrightHomePage(BasePage):
    """Sample page object against https://playwright.dev. Replace with your own."""

    url_path = "/"

    @property
    def get_started_link(self) -> Locator:
        return self.page.get_by_role("link", name="Get started")

    @property
    def search_button(self) -> Locator:
        return self.page.get_by_role("button", name="Search")

    def click_get_started(self) -> None:
        self.get_started_link.click()

    def wait_for_loaded(self) -> None:
        expect(self.get_started_link).to_be_visible()
