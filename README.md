# playwright-pytest-atlas

A reusable Python QA archetype for UI and API testing. Built on **Playwright** and **Pytest** with Allure reporting. Clone it, point it at your target system, write tests.

---

## Table of contents

- [What you get](#what-you-get)
- [Prerequisites](#prerequisites)
- [Setup from scratch](#setup-from-scratch)
- [Running tests](#running-tests)
- [Project layout](#project-layout)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Adding tests](#adding-tests)
- [Markers](#markers)
- [Reporting](#reporting)
- [Code quality](#code-quality)
- [Continuous integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)
- [Adopting this archetype](#adopting-this-archetype)
- [License](#license)

---

## What you get

- **Page Object Model** with a `BasePage` foundation, `LoginPage` placeholder, and component composition
- **API client layer** using Playwright's `APIRequestContext` (shared runtime with the browser)
- **OAuth2 / OIDC auth** via a cached `AuthClient` with TOTP retry across windows
- **Type-safe configuration** via `pydantic-settings` and `.env` files (`SecretStr` for credentials)
- **Allure + pytest-html** reports with screenshot, video, and trace attachments on failure
- **Parallel execution** (`pytest-xdist`) and **automatic retry** of flaky tests (`pytest-rerunfailures`)
- **Test data factories** via Faker, with Pydantic models for shape validation
- **Structured logging** via `structlog`
- **GitHub Actions** matrix across Chromium / Firefox / WebKit plus a lint + type check job
- **Ruff** (lint + format), **mypy strict**, **pre-commit** hooks
- Markers: `smoke`, `regression`, `ui`, `api`, `e2e`, `slow`

---

## Prerequisites

- **Python 3.11+** (`python3.11 --version` should print `3.11.x` or higher)
- **Git**
- **Allure CLI** (optional, only if you want to view the Allure HTML report locally — `brew install allure` on macOS)

---

## Setup from scratch

```bash
# 1. Clone (or use this repo as a template)
git clone <your-fork-url>.git
cd playwright-pytest-atlas

# 2. Create and activate a Python 3.11 virtual environment
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Upgrade pip and install the project in editable mode
pip install --upgrade pip
pip install -e ".[dev]"            # runtime + ruff/mypy/pre-commit
# or, if you need OTP / JWT helpers:
pip install -e ".[dev,auth]"       # also pulls pyotp and pyjwt

# 4. Install the Playwright browsers
playwright install chromium        # lightest option (~100 MB)
# or, for all three browsers + OS deps:
playwright install --with-deps

# 5. Configure the environment
cp .env.example .env
# Edit .env — defaults already point to public demo targets so the smoke
# suite runs out of the box. Replace QA_BASE_URL / QA_API_BASE_URL for
# your real system under test.

# 6. Run the smoke suite to validate everything works
pytest -m smoke -v
# Expected: 2 passed (1 UI + 1 API) against playwright.dev and jsonplaceholder.typicode.com
```

> No `requirements.txt`. Dependencies live in [pyproject.toml](pyproject.toml) under `[project].dependencies` (runtime) and `[project.optional-dependencies]` (`dev`, `auth`). `pip install -e .` reads them directly.

After the initial setup, every future session is just:

```bash
source .venv/bin/activate
pytest -m smoke
```

---

## Running tests

| Goal                                  | Command                                                               |
|---------------------------------------|-----------------------------------------------------------------------|
| Smoke suite                           | `pytest -m smoke` or `make smoke`                                     |
| Full suite                            | `pytest` or `make test`                                               |
| UI tests only                         | `pytest -m ui` or `make ui`                                           |
| API tests only                        | `pytest -m api` or `make api`                                         |
| End-to-end only                       | `pytest -m e2e` or `make e2e`                                         |
| Compound selection                    | `pytest -m "smoke and ui"` &nbsp; `pytest -m "regression and not slow"` |
| Single file                           | `pytest tests/ui/test_example_ui.py -v`                               |
| Single test                           | `pytest tests/ui/test_example_ui.py::test_home_page_displays_get_started -v` |
| Substring match on test names         | `pytest -k home`                                                       |
| Parallel (auto-detect cores)          | `pytest -n auto`                                                       |
| Switch browser one-off                | `pytest --browser=firefox -m ui`                                       |
| Multiple browsers in one run          | `pytest --browser=chromium --browser=firefox`                          |

### Watching the browser (headed mode)

By default tests run headless. To see the actual browser window:

```bash
# Show the browser, slow down each action by ~1s so you can follow along
pytest tests/ui/test_example_ui.py --headed --slowmo 1000 -v

# Step through interactively with the Playwright Inspector (also disables timeouts)
PWDEBUG=1 pytest tests/ui/test_example_ui.py::test_home_page_displays_get_started --headed
```

To run headed permanently for your local sessions, set `QA_HEADLESS=false` in your [.env](.env).

> On macOS the browser window often opens *behind* your terminal. Cmd+Tab or check the dock if you do not see it pop forward.

---

## Project layout

```
.
├── framework/                Reusable building blocks (the archetype core)
│   ├── pages/                Page Object Model
│   │   ├── base_page.py      BasePage foundation
│   │   ├── example_page.py   Sample page object (delete when adapting)
│   │   └── login_page.py     Keycloak-style login placeholder
│   ├── components/           UI fragments scoped to a Locator
│   │   └── base_component.py
│   ├── api/                  HTTP clients on top of APIRequestContext
│   │   ├── base_client.py    BaseAPIClient with verb shortcuts + ok-helper
│   │   ├── example_client.py Sample client (delete when adapting)
│   │   └── auth_client.py    OAuth2 / OIDC token client with OTP retry
│   ├── auth/                 Auth helpers
│   │   ├── otp.py            TOTP generation (requires the [auth] extras)
│   │   └── token_cache.py    In-process Token cache with TTL
│   ├── data/                 Test data
│   │   ├── models.py         Pydantic schemas
│   │   └── factories.py      Faker-driven builders
│   └── utils/                Cross-cutting helpers
│       ├── logger.py         structlog setup + get_logger()
│       └── assertions.py     SoftAssert context manager
├── config/
│   └── settings.py           pydantic-settings (env-driven, QA_ prefix)
├── tests/
│   ├── conftest.py           Root: settings, page/api/auth fixtures, Allure hooks
│   ├── ui/                   UI tests (subfolder conftest is a placeholder)
│   ├── api/                  API tests (subfolder conftest is a placeholder)
│   └── e2e/                  Flows combining UI + API
├── reports/                  Allure results, pytest-html, videos, traces (gitignored)
├── .github/workflows/
│   └── tests.yml             Chromium/Firefox/WebKit matrix + lint job
├── .env.example              Configuration template (copy to .env)
├── .gitignore
├── .pre-commit-config.yaml   Ruff + standard hooks
├── LICENSE                   MIT
├── Makefile                  Common commands
├── pyproject.toml            Deps, pytest, ruff, mypy config
└── README.md
```

> **Fixture rule.** Cross-cutting fixtures (page objects, API clients used by e2e) live in the root [tests/conftest.py](tests/conftest.py) so every test type can see them. Subfolder conftests at [tests/ui/](tests/ui/conftest.py) and [tests/api/](tests/api/conftest.py) are placeholders for genuinely UI-only or API-only fixtures.

---

## Configuration

All runtime settings are env-driven with the `QA_` prefix. See [.env.example](.env.example) and [config/settings.py](config/settings.py) for the full schema. Set real env vars in CI; never commit secrets.

Common knobs:

| Variable                     | Default                              | Purpose                              |
|------------------------------|--------------------------------------|--------------------------------------|
| `QA_ENVIRONMENT`             | `local`                              | `local` / `dev` / `staging` / `prod` |
| `QA_BASE_URL`                | `https://playwright.dev`             | Base URL for UI tests                |
| `QA_API_BASE_URL`            | `https://jsonplaceholder.typicode.com` | Base URL for API tests             |
| `QA_BROWSER`                 | `chromium`                           | `chromium`, `firefox`, or `webkit`   |
| `QA_HEADLESS`                | `true`                               | `false` to show the browser          |
| `QA_SLOW_MO_MS`              | `0`                                  | Add latency between Playwright actions |
| `QA_DEFAULT_TIMEOUT_MS`      | `30000`                              | Per-action timeout                   |
| `QA_NAVIGATION_TIMEOUT_MS`   | `30000`                              | Page navigation timeout              |
| `QA_RECORD_VIDEO`            | `false`                              | Record videos for every test         |
| `QA_RECORD_TRACE`            | `retain-on-failure`                  | `off` / `on` / `retain-on-failure`   |
| `QA_CAPTURE_SCREENSHOT`      | `only-on-failure`                    | `off` / `on` / `only-on-failure`     |

Auth-related variables (all optional) are documented in [.env.example](.env.example) and the [Authentication](#authentication) section below.

---

## Authentication

Auth is **opt-in**. Leave `QA_USERNAME` / `QA_PASSWORD` blank and tests run anonymously. Set them and the auth fixtures activate automatically.

Install the auth extras if you need TOTP or JWT decoding:

```bash
pip install -e ".[dev,auth]"
```

### UI auth — one-time login via storage state

The `storage_state_path` session fixture logs in once through [LoginPage](framework/pages/login_page.py), persists cookies + localStorage to disk, and every subsequent browser context loads that state. No re-login per test.

Defaults match a Keycloak-style two-step form. Override class attributes (`username_label`, `password_label`, `submit_button_name`) or methods on a project-specific subclass.

### UI auth — per-test fresh login

Depend on the `ui_login` fixture when you need to exercise the login flow itself or want a clean slate:

```python
def test_dashboard_after_fresh_login(ui_login, page):
    page.goto("/dashboard")
    ...
```

### API auth — cached OAuth2 / OIDC token

Set `QA_AUTH_TOKEN_URL` and depend on `api_token` (a `Token` dataclass) or `auth_headers` (a `{"Authorization": "Bearer ..."}` dict):

```python
def test_admin_endpoint(jsonplaceholder, auth_headers):
    response = jsonplaceholder.get("/admin/users", headers=auth_headers)
    assert response.ok
```

The token is cached for 15 minutes inside [TokenCache](framework/auth/token_cache.py). [AuthClient](framework/api/auth_client.py) handles OTP retries across TOTP windows when `QA_OTP_SECRET` is set.

### Custom auth flows

For SAML, PAT exchange, header-based auth, or anything non-standard: subclass `AuthClient`, override `_build_payload` / `_fetch_token`, then replace the `auth_client` fixture in your project conftest.

---

## Adding tests

### A new page object

```python
# framework/pages/dashboard_page.py
from playwright.sync_api import Locator, expect

from framework.pages.base_page import BasePage


class DashboardPage(BasePage):
    url_path = "/dashboard"

    @property
    def greeting(self) -> Locator:
        return self.page.get_by_role("heading", name="Welcome")

    def wait_for_loaded(self) -> None:
        expect(self.greeting).to_be_visible()
```

Expose it via a fixture. For cross-cutting use (UI + e2e), add it in the root [tests/conftest.py](tests/conftest.py); for UI-only, add it in [tests/ui/conftest.py](tests/ui/conftest.py):

```python
@pytest.fixture
def dashboard_page(page, base_url) -> DashboardPage:
    return DashboardPage(page, base_url)
```

### A new API client

```python
# framework/api/users_client.py
from framework.api.base_client import BaseAPIClient
from framework.data.models import User


class UsersClient(BaseAPIClient):
    def create(self, user: User) -> dict:
        return self.expect_ok(
            self.post("/users", data=user.model_dump())
        ).json()
```

### A new test

```python
# tests/ui/test_dashboard.py
import pytest

@pytest.mark.ui
@pytest.mark.smoke
def test_dashboard_greets_user(dashboard_page):
    dashboard_page.open()
    assert dashboard_page.greeting.is_visible()
```

---

## Markers

Tag tests with markers declared in [pyproject.toml](pyproject.toml):

```python
@pytest.mark.ui
@pytest.mark.smoke
def test_something(...):
    ...
```

Run subsets:

```bash
pytest -m smoke
pytest -m "smoke and ui"
pytest -m "regression and not slow"
pytest -m "e2e or smoke"
```

Adding a new marker requires registering it in `[tool.pytest.ini_options].markers` in `pyproject.toml` (we run with `--strict-markers`).

---

## Reporting

Three reports are generated for every run, written to `reports/`:

| Report          | Path                          | View                                       |
|-----------------|-------------------------------|--------------------------------------------|
| Allure (raw)    | `reports/allure-results/`     | `make allure` (requires the `allure` CLI)  |
| Pytest HTML     | `reports/html/report.html`    | Open the file in a browser                 |
| Playwright artifacts (screenshot / video / trace) | `reports/playwright/` | View traces with `playwright show-trace <file>` |

On failure, screenshots are automatically attached to the Allure report and a Playwright trace is retained at `reports/playwright/<test-name>/trace.zip`. Open it with:

```bash
playwright show-trace reports/playwright/<test-name>/trace.zip
```

---

## Code quality

Ruff (lint + format), mypy strict, and pre-commit hooks are pre-wired.

```bash
make lint          # ruff check
make format        # ruff format
make type          # mypy strict on framework + config
make check         # lint + type

pre-commit install # install git hooks (also runs on every commit)
pre-commit run --all-files   # run all hooks on demand
```

---

## Continuous integration

[.github/workflows/tests.yml](.github/workflows/tests.yml) runs on every push and pull request:

- **`test` job**: matrix across Chromium / Firefox / WebKit on Python 3.11. Runs the smoke suite by default, in parallel via `pytest-xdist`, with one automatic retry on flake.
- **`lint` job**: ruff check + ruff format check + mypy strict.

Reports are uploaded as build artifacts (`reports-chromium-py3.11`, etc.) with 14-day retention.

To trigger an ad-hoc run with a custom marker expression: open the **Actions** tab → **tests** → **Run workflow**, and provide a marker expression (default `smoke`).

---

## Troubleshooting

### `pytest` fails to import `framework` or `config`

You're not in the venv. Re-activate: `source .venv/bin/activate`. Or you skipped the editable install — re-run `pip install -e ".[dev]"`.

### `python3.11: command not found`

Install Python 3.11+. On macOS: `brew install python@3.11`. The default `python3` on macOS is often 3.9 which is below the minimum.

### `--headed` opens nothing visible

Two common causes:
1. The smoke test is too fast (~2s) — the window opens and closes before you notice. Add `--slowmo 1000` so each action is delayed.
2. On macOS, the browser opens *behind* your terminal. Cmd+Tab or check the dock.

If you genuinely see no window at all, `playwright install chromium` may have installed only the headless shell. Re-run:

```bash
playwright install chromium --force
playwright install --list   # should show both chromium-XXXX and chromium_headless_shell-XXXX
```

### `allure: command not found`

The Allure CLI is a separate runtime. On macOS:

```bash
brew install allure
```

The raw results in `reports/allure-results/` are still produced without it, and `reports/html/report.html` works standalone.

### Tests skip with "auth credentials not configured"

That's the auth fixtures behaving correctly — they refuse to run when `QA_USERNAME` / `QA_PASSWORD` are blank. Either configure auth in your `.env`, or do not depend on `credentials` / `api_token` / `ui_login` in tests that should run anonymously.

### Pre-commit fails on commit

Run the hooks on demand to see exactly what tripped:

```bash
pre-commit run --all-files
```

Most commonly ruff auto-fixes the issue; just `git add -u && git commit` again.

---

## Adopting this archetype

1. Click **Use this template** on GitHub, or clone and `rm -rf .git && git init`.
2. Update `name`, `description`, and `authors` in [pyproject.toml](pyproject.toml).
3. Point [.env.example](.env.example) at your real target URLs.
4. Delete the samples (`framework/pages/example_page.py`, `framework/api/example_client.py`, `tests/ui/test_example_ui.py`, `tests/api/test_example_api.py`, `tests/e2e/test_example_e2e.py`) and the fixtures referencing them in [tests/conftest.py](tests/conftest.py).
5. Customise [framework/pages/login_page.py](framework/pages/login_page.py) for your real login flow (override class attributes or `login()`).
6. Keep `framework/` generic. Project-specific page objects and clients live alongside it (they reuse `BasePage` / `BaseAPIClient`).

---

## License

MIT. See [LICENSE](LICENSE).

---

> Dependency modernization and review assisted by Claude (Anthropic Opus 4.8).
