# Validator Agent

**Pre-deployment quality gate for OpenClaw skills.** Runs a 10-section validation covering security, testing, code quality, documentation, and more — then generates a structured `VALIDATION_REPORT.md`.

Built by the **up2itnow** team, creators of [Agent Wallet](https://clawhub.com/up2itnow/agentwallet-sdk).

## How to Use

Install this skill in your OpenClaw agent, then say:

```
Validate my project at /path/to/my/skill
```

Other trigger phrases: `security check`, `pre-deploy check`, `audit my code`, `is my skill safe`

## What It Checks

### 10 Validation Sections

| # | Section | What It Does |
|---|---------|-------------|
| 1 | **Security** 🔒 | Runs `npm audit`, `forge build`, `slither`, secret scanning (`ggshield`/`trufflehog`/grep), input validation, access control, reentrancy checks |
| 2 | **Testing** ✅ | Executes test suites (`forge test`, `npm test`, `pytest`), checks coverage, looks for edge-case tests |
| 3 | **Code Quality** 📐 | Runs linters (`eslint`, `solhint`, `ruff`), checks for dead code, complexity |
| 4 | **Documentation** 📚 | Verifies README, API docs, changelog, deploy guides |
| 5 | **CI/CD** 🔄 | Checks for workflows, clean builds, rollback plans |
| 6 | **Privacy & PII** 🛡️ | Scans for hardcoded PII, logging of sensitive data |
| 7 | **Maintainability** 🔧 | Lockfiles, dependency freshness, config externalization |
| 8 | **Usability** 🎨 | Error handling, landing pages, UX basics |
| 9 | **Marketability** 📣 | One-liner clarity, demos, social proof |
| 10 | **Final Gate** 🚪 | Summary, blocking issues, deploy readiness |

### 13 ClawHub Security Domains

Gateway exposure, DM policy, credentials, browser sandboxing, network binding, tool sandboxing, file permissions, plugin trust, logging/redaction, prompt injection, dangerous commands, secret scanning, dependency safety.

## Sample Output

```markdown
# Validation Report — my-skill

**Date:** 2026-02-15
**Validator:** Validator Agent (Internal AI-Assisted Review)

## Summary

| Section | Status | Issues |
|---------|--------|--------|
| 1. Security | 🟠 High | 2 unpinned deps, no lockfile |
| 2. Testing | ✅ Passed | 25/25 tests pass |
| 3. Code Quality | 🟡 Medium | 3 eslint warnings |
| ... | ... | ... |

**Overall:** 🟠 CONDITIONAL
```

## Severity Ratings

- 🔴 **Critical** — Must fix before deploy
- 🟠 **High** — Should fix before deploy
- 🟡 **Medium** — Fix soon
- ✅ **Passed** — No issues
- ⬜ **N/A** — Not applicable
- 🔵 **Skipped** — Tool unavailable

## Honesty Policy

All reports are labeled **"Internal AI-Assisted Review"**. This is not a third-party audit. The agent runs real tools and commands, and honestly marks checks as 🔵 Skipped when tooling is unavailable.

## License

MIT
