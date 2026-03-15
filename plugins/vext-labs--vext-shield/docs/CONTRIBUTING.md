# Contributing to VEXT Shield

## Adding New Threat Signatures

The most common contribution. Edit `shared/threat_signatures.json`:

1. Find the appropriate category and subcategory
2. Add a new pattern object:

```json
{
    "id": "XX-NNN",
    "name": "Descriptive Name",
    "pattern": "(?i)your\\s+regex\\s+here",
    "pattern_type": "regex",
    "description": "What this pattern detects and why it's dangerous."
}
```

3. Ensure the pattern ID is unique across the entire file
4. Run `python -m pytest tests/test_signatures.py` to validate
5. Add a test fixture if the pattern catches a novel attack

### ID Conventions

| Prefix | Category |
|--------|----------|
| PI | Prompt Injection |
| DE | Data Exfiltration |
| PE | Persistence |
| PR | Privilege Escalation |
| SC | Supply Chain |
| SW | Semantic Worm |
| RS | Reverse Shell |
| CM | Cryptominer |

### Pattern Tips

- Use `(?i)` for case-insensitive matching
- Use `\b` for word boundaries to reduce false positives
- Escape special regex characters: `\.`, `\(`, `\[`
- Test your pattern against the test fixtures to verify it matches

## Adding Red Team Test Batteries

1. Add a new method to `RedTeamRunner` in `skills/vext-redteam/redteam.py`:

```python
def test_new_battery(self) -> BatteryResult:
    """Test for [new attack vector]."""
    start = time.monotonic()
    findings: list[RedTeamFinding] = []
    tests_run = 0
    tests_failed = 0

    # Your test logic here
    # ...

    elapsed = int((time.monotonic() - start) * 1000)
    return BatteryResult(
        name="New Battery Name",
        tests_run=tests_run,
        tests_passed=tests_run - tests_failed,
        tests_failed=tests_failed,
        findings=findings,
        duration_ms=elapsed,
    )
```

2. Add the battery to `run_all_batteries()` in the same class
3. Add a corresponding section to `skills/vext-redteam/SKILL.md`

## Adding Test Fixtures

Create a new directory under `tests/fixtures/`:

```
tests/fixtures/new_attack_skill/
├── SKILL.md          # Must have valid OpenClaw frontmatter
└── malicious.py      # Optional: Python script with the attack
```

The SKILL.md must have YAML frontmatter:

```yaml
---
name: skill-name
description: Description
version: 1.0.0
metadata:
  openclaw:
    emoji: "X"
    requires:
      bins: ["python3"]
---
```

## Code Style

- Python 3.10+ type hints throughout
- Zero external dependencies — stdlib only
- Docstrings on all public functions
- `from __future__ import annotations` at the top of every module
- Dataclasses for structured data
- `Path` objects (not string paths)

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_scanner.py -v

# Test against fixtures
python skills/vext-scan/scan.py --skill-dir tests/fixtures/exfil_skill
python skills/vext-redteam/redteam.py --skill-dir tests/fixtures/semantic_worm_skill
```

## Reporting Security Issues

If you discover a vulnerability in VEXT Shield itself, please email security@vext.co rather than opening a public issue.

---

*Built by Vext Labs — Autonomous AI Red Team Technology*
