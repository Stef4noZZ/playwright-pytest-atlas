from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from framework.utils.logger import get_logger


class BaseAPIClient:
    """Thin wrapper around Playwright's `APIRequestContext`.

    Provides URL composition, structured logging, and verb shortcuts. Subclass
    per resource family (e.g. `UsersClient`, `OrdersClient`) and expose
    domain-specific methods that return typed Pydantic models where useful.
    """

    def __init__(self, request: APIRequestContext, base_url: str) -> None:
        self.request = request
        self.base_url = base_url.rstrip("/")
        self.log = get_logger(self.__class__.__name__)

    def _url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{normalized}"

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        self.log.info("api_request", method="GET", url=url)
        return self.request.get(url, **kwargs)

    def post(self, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        self.log.info("api_request", method="POST", url=url)
        return self.request.post(url, **kwargs)

    def put(self, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        self.log.info("api_request", method="PUT", url=url)
        return self.request.put(url, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        self.log.info("api_request", method="PATCH", url=url)
        return self.request.patch(url, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        self.log.info("api_request", method="DELETE", url=url)
        return self.request.delete(url, **kwargs)

    @staticmethod
    def expect_ok(response: APIResponse) -> APIResponse:
        if not response.ok:
            raise AssertionError(
                f"API call failed: {response.status} {response.status_text} -> {response.url}\n"
                f"body: {response.text()[:500]}"
            )
        return response
