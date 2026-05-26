.PHONY: help install browsers test smoke regression ui api e2e allure clean lint format type check

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n"} /^[a-zA-Z_-]+:.*?##/ {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies and pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

browsers: ## Install Playwright browsers and OS deps
	playwright install --with-deps

test: ## Run the full test suite
	pytest

smoke: ## Run smoke suite
	pytest -m smoke

regression: ## Run regression suite
	pytest -m regression

ui: ## Run UI tests only
	pytest -m ui

api: ## Run API tests only
	pytest -m api

e2e: ## Run end-to-end tests only
	pytest -m e2e

allure: ## Serve the Allure report (requires the allure CLI on PATH)
	allure serve reports/allure-results

clean: ## Remove report artifacts and tool caches
	rm -rf reports/* .pytest_cache .ruff_cache .mypy_cache

lint: ## Lint with ruff
	ruff check framework config tests

format: ## Format with ruff
	ruff format framework config tests

type: ## Type-check framework code with mypy
	mypy framework config

check: lint type ## Run lint and type checks
