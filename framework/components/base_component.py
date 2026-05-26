from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.utils.logger import get_logger


class BaseComponent:
    """Foundation for reusable UI fragments that appear on multiple pages.

    Compose components inside page objects rather than duplicating selectors.
    A component is scoped to a root Locator and exposes only what tests need.
    """

    def __init__(self, page: Page, root: Locator) -> None:
        self.page = page
        self.root = root
        self.log = get_logger(self.__class__.__name__)

    def is_visible(self) -> bool:
        return self.root.is_visible()

    def locate(self, selector: str) -> Locator:
        return self.root.locator(selector)
