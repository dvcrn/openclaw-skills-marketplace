# Contributing to privacy-mask

Thanks for your interest in contributing! This guide will help you get started.

## Quick Setup

```bash
git clone https://github.com/fullstackcrew-alpha/privacy-mask.git
cd privacy-mask
pip install -e .
```

## Running Tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -v
```

All tests must pass before submitting a PR. We currently have 208+ tests covering all 47 detection rules.

## How to Add a New Detection Rule

Adding a new regex rule is the easiest way to contribute. Here's the step-by-step process:

### 1. Edit `mask_engine/data/config.json`

Add your rule to the `rules` array:

```json
{
  "name": "MY_NEW_RULE",
  "pattern": "MY-\\d{6}-[A-Z]{2}",
  "flags": ["IGNORECASE"],
  "enabled": true
}
```

**Important:** Since patterns are JSON strings, backslashes must be double-escaped (`\\d` not `\d`).

### 2. Add Tests in `tests/test_detector.py`

Every rule needs both **positive** (should match) and **negative** (should NOT match) test cases:

```python
def test_my_new_rule_positive(detector):
    """MY_NEW_RULE should match valid patterns."""
    assert_detects(detector, "MY-123456-AB", "MY_NEW_RULE")
    assert_detects(detector, "MY-999999-ZZ", "MY_NEW_RULE")

def test_my_new_rule_negative(detector):
    """MY_NEW_RULE should not match common words or partial patterns."""
    assert_not_detects(detector, "MY-12-AB", "MY_NEW_RULE")
    assert_not_detects(detector, "MYSTERY", "MY_NEW_RULE")
```

### 3. Test for False Positives

This is critical. OCR can read common English words as uppercase text, so make sure your pattern doesn't match words like:
- ORGANIZATION, REQUIRED, CONTINUE, INFORMATION
- Common abbreviations in your target language

### 4. Run Tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_detector.py -v -k "my_new_rule"
```

## Other Ways to Contribute

### Improve OCR Accuracy
- Better image preprocessing strategies
- Support for additional OCR engines
- Multi-language OCR improvements

### Report False Positives
If you find that privacy-mask incorrectly detects normal text as sensitive data, please open an issue with:
- The text that was incorrectly detected
- Which rule triggered the false positive
- A screenshot if possible

### Improve Documentation
- Fix typos, clarify instructions
- Add examples for your country's ID formats
- Translate documentation

## Submitting a Pull Request

1. Fork the repo and create a feature branch from `main`
2. Make your changes and add tests
3. Run the full test suite and ensure all tests pass
4. Submit a PR with a clear description of the change

### PR Guidelines

- Keep PRs focused — one feature or fix per PR
- Include test cases for new detection rules (both positive and negative)
- Never commit real secrets, API keys, or personal data — use constructed test strings
- Update the README if adding user-facing features

## Issues

- Use the [issue tracker](https://github.com/fullstackcrew-alpha/privacy-mask/issues) for bug reports and feature requests
- Tag issues with `good first issue` if they're suitable for newcomers
- Check existing issues before opening a new one

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
