"""API-only fixtures.

Cross-cutting fixtures (`api_request_context`, `jsonplaceholder`) live in
`tests/conftest.py` so e2e tests can reuse them. Put fixtures here only when
they should never be visible to UI or e2e tests.
"""
