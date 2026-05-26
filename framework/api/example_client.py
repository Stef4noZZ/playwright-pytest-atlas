from __future__ import annotations

from typing import Any, cast

from framework.api.base_client import BaseAPIClient


class JsonPlaceholderClient(BaseAPIClient):
    """Sample client against https://jsonplaceholder.typicode.com.

    A read-only public API used purely to demonstrate the API layer. Replace
    with your own client(s) when adapting the archetype.
    """

    def list_users(self) -> list[dict[str, Any]]:
        return cast("list[dict[str, Any]]", self.expect_ok(self.get("/users")).json())

    def get_user(self, user_id: int) -> dict[str, Any]:
        return cast("dict[str, Any]", self.expect_ok(self.get(f"/users/{user_id}")).json())

    def list_posts(self, user_id: int | None = None) -> list[dict[str, Any]]:
        params = {"userId": user_id} if user_id is not None else None
        return cast(
            "list[dict[str, Any]]",
            self.expect_ok(self.get("/posts", params=params)).json(),
        )
