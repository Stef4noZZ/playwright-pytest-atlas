from __future__ import annotations

import allure
import pytest
from framework.api.example_client import JsonPlaceholderClient


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("Sample API")
@allure.story("Users collection")
def test_list_users_returns_non_empty_collection(jsonplaceholder: JsonPlaceholderClient) -> None:
    users = jsonplaceholder.list_users()
    assert isinstance(users, list)
    assert len(users) > 0


@pytest.mark.api
@allure.feature("Sample API")
@allure.story("Single user")
def test_get_single_user_returns_expected_shape(jsonplaceholder: JsonPlaceholderClient) -> None:
    user = jsonplaceholder.get_user(1)
    assert user["id"] == 1
    for field in ("name", "email", "username"):
        assert field in user, f"missing field: {field}"


@pytest.mark.api
@allure.feature("Sample API")
@allure.story("Filtered posts")
def test_posts_filtered_by_user(jsonplaceholder: JsonPlaceholderClient) -> None:
    posts = jsonplaceholder.list_posts(user_id=1)
    assert posts, "expected at least one post for user 1"
    assert all(post["userId"] == 1 for post in posts)
