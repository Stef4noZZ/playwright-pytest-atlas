from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.utils.logger import get_logger


class BasePage:
    """Foundation for Page Object Model classes.

    Subclasses set `url_path`, expose locators as properties, and provide
    intention-revealing action methods. Keep assertions out of page objects;
    they belong in tests or in step-style facades.
    """

    url_path: str = ""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.log = get_logger(self.__class__.__name__)

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.url_path}"

    def open(self) -> None:
        self.log.info("navigating", url=self.url)
        self.page.goto(self.url)
        self.wait_for_loaded()

    def wait_for_loaded(self) -> None:
        """Override in subclasses to assert that a key landmark is visible."""
        self.page.wait_for_load_state("domcontentloaded")

    def locate(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def reload(self) -> None:
        self.page.reload()
        self.wait_for_loaded()
