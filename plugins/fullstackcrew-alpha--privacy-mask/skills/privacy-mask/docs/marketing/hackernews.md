# Hacker News - Show HN

## Title

Show HN: Privacy-mask – Local OCR + regex to redact sensitive info from screenshots before AI upload

## Body

I built a CLI tool that intercepts screenshots before they're sent to AI coding assistants (Claude Code, Cursor, Copilot, etc.) and automatically redacts sensitive information — credit card numbers, API keys, SSNs, phone numbers, and more.

The key constraint: everything runs locally. No cloud APIs, no image uploads to a third-party service. That would defeat the entire point.

**How it works:**

1. Dual-engine OCR (Tesseract + RapidOCR) extracts text with bounding boxes
2. 47 compiled regex rules scan the OCR output — covering IDs, financial data, developer secrets, and PII across 15+ countries
3. Matched regions get blurred or filled in the image

It ships as a Python package (`pip install privacy-mask`) and can hook into Claude Code as a pre-upload step, so masking happens transparently.

Some things I learned building this:

- OCR on screenshots is surprisingly noisy. Multi-strategy preprocessing (grayscale, binarization, contrast enhancement) with confidence-based merging made a huge difference.
- False positive suppression is harder than detection. Common English words in uppercase (ORGANIZATION, REQUIRED) kept triggering ID patterns. Ended up with 208+ test cases, most of them negative.
- Regex patterns in JSON config need double-escaped backslashes, which is its own special kind of pain.

The detection rules are fully configurable — you can add your own patterns or disable built-in ones.

GitHub: https://github.com/fullstackcrew-alpha/privacy-mask
PyPI: https://pypi.org/project/privacy-mask/
License: MIT

If this is useful to you, a star on GitHub would mean a lot. PRs are very welcome too — especially new detection rules for regions/formats I haven't covered, or OCR preprocessing improvements. The regex patterns are all in a single JSON config file, so adding a new rule is pretty low-friction.
