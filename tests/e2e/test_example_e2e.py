from __future__ import annotations

import allure
import pytest
from framework.api.example_client import JsonPlaceholderClient
from framework.pages.example_page import PlaywrightHomePage


@pytest.mark.e2e
@allure.feature("End-to-end")
@allure.story("UI + API composition")
def test_ui_and_api_can_be_composed_in_one_test(
    home_page: PlaywrightHomePage, jsonplaceholder: JsonPlaceholderClient
) -> None:
    """Skeleton showing how UI and API layers compose in one test.

    Real end-to-end flows typically: seed state via API, exercise UI, then
    verify side-effects via API.
    """
    users = jsonplaceholder.list_users()
    assert users

    home_page.open()
    assert home_page.get_started_link.is_visible()
