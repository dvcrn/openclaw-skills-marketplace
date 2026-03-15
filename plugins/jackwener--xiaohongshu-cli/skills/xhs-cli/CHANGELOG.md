# Changelog

All notable changes to this project will be documented in this file.

## v0.1.2 - 2026-03-06

### Added

- Added terminal QR rendering with half-block characters (`▀`, `▄`, `█`) for QR login.
- Added post-login session usability probing (feed/search) to detect limited/guest sessions.
- Added stricter and broader test coverage for auth, CLI login flows, and publish heuristics.
- Added `qrcode` dependency for terminal QR rendering.

### Changed

- Strengthened cookie requirements for saved/manual auth:
  - Required cookies are now `a1` + `web_session`.
- Improved QR login robustness:
  - Force switch to QR login tab when possible.
  - Better QR payload extraction heuristics to avoid homepage/logo false matches.
  - Better QR fallback element selection for screenshots.
- Improved login success detection:
  - Treat guest sessions as invalid.
  - Accept non-guest page state as a login success signal (not only session cookie change).
- Improved operation reliability:
  - Tightened success criteria for publish/comment/delete flows.
  - Added strict data-wait timeout path to reduce silent empty results.
- Updated `whoami --json` to include normalized top-level fields when resolvable.
- Updated docs (`README.md` and `README_EN.md`) to match current login/auth behavior.

### Fixed

- Fixed transient cookie verification flow to avoid unintended QR login fallback.
- Fixed favorites note ID extraction regex to support alphanumeric note IDs.
- Fixed cross-platform cookie save behavior by handling `chmod` failures safely.
- Fixed multiple false-positive success cases in interaction and publish flows.

### Validation

- `ruff check .` passes.
- `pytest -q` passes (`66 passed, 21 deselected`).
