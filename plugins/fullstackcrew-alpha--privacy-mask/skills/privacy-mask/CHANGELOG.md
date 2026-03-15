# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2025-03-14

### Fixed
- Fix MRZ_LINE2 false positives — require chevron separators (`<`) in pattern
- Fix SWIFT_BIC false positives — add ISO 3166 country code constraint, disabled by default

### Added
- Claude Code plugin structure (`.claude-plugin/`, hooks, scripts)
- CLAUDE.md with project conventions and test commands
- GitHub Actions CI workflow (Ubuntu + macOS, Python 3.10–3.12)
- 208+ tests covering all 47 detection rules
- CONTRIBUTING.md with step-by-step guide for adding rules
- CHANGELOG.md

### Changed
- Update project URLs to fullstackcrew-alpha organization

## [0.1.1] - 2025-03-13

### Fixed
- Fix README images for PyPI: use absolute GitHub URLs
- Fix packaging audit issues and align SKILL.md with agentskills.io spec
- Avoid literal Stripe test keys to pass GitHub push protection

### Added
- OpenClaw to Agent Integration list

## [0.1.0] - 2025-03-12

### Added
- Initial release
- 47 regex detection rules covering 15+ countries
- Dual OCR engine support (Tesseract + RapidOCR)
- Multi-strategy image preprocessing with confidence-based merge
- CLI tool with mask, dry-run, and install commands
- Blur and fill masking methods
- 21 global sensitive info detection rules (IDs, dev keys, crypto, phones)
- Passport detection with MRZ, English dates, CN passport numbers
- pip-installable package with global Claude Code hook support
- Before/after demo images
- Bilingual README (English + Chinese)
- MIT license
