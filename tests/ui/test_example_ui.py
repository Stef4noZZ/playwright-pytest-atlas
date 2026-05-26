from __future__ import annotations

import re

import allure
import pytest
from framework.pages.example_page import PlaywrightHomePage
from playwright.sync_api import expect


@pytest.mark.ui
@pytest.mark.smoke
@allure.feature("Sample UI")
@allure.story("Home page loads")
def test_home_page_displays_get_started(home_page: PlaywrightHomePage) -> None:
    home_page.open()
    expect(home_page.get_started_link).to_be_visible()


@pytest.mark.ui
@allure.feature("Sample UI")
@allure.story("Navigation")
def test_clicking_get_started_navigates_to_docs(home_page: PlaywrightHomePage) -> None:
    home_page.open()
    home_page.click_get_started()
    expect(home_page.page).to_have_url(re.compile(r"/docs"))
