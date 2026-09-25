# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://common-changelog.org/).
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Apply `QA_BROWSER`, screenshot, trace, and video settings when the matching pytest flags are omitted
- Default TOTP to SHA-1 and wait for the next time step instead of a fixed 31 seconds
- Honor `expires_in` in the API token cache
- Run API smoke tests once in CI instead of once per browser

### Removed

- Unused `tenacity` and `pytest-timeout` dependencies

## [0.1.0]

### Added

- Initial Playwright and pytest QA archetype
