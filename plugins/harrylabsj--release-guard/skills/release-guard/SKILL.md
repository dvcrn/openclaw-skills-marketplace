---
name: release-guard
description: "Guard skill releases with pre-publish validation, quality checks, and safety gates. Use before publishing any skill to ensure it meets minimum standards, passes tests, and has no obvious risks. Acts as a safety net for the skill ecosystem."
---

# Release Guard

## Overview

Release Guard is a quality assurance skill that validates skills before they are published or shared. It runs a comprehensive checklist of validations to catch common issues and ensure skills meet minimum standards.

The `release-guard` skill ensures that skill releases meet quality and safety standards. It runs pre-release validation checks including security scans, dependency audits, documentation completeness, and compatibility verification.

## When to Use

- Before publishing any skill to ClawHub
- When preparing a new version release
- During CI/CD release pipelines
- When the user asks to "检查" or "验证" a release
- Before creating GitHub releases

## Prerequisites

- Node.js 18+ for script execution
- Optional: `security-auditor` for detailed security scans

## Usage

### CLI Commands

```bash
# Run all release checks
./scripts/release-check.sh <skill-directory>

# Run with auto-fix mode
./scripts/release-check.sh <skill-directory> --fix

# Quick validation (current directory)
./scripts/release-check.sh .
```

### Check Levels

| Level | Description | Failure Action |
|-------|-------------|-----------------|
| `critical` | Required for release | Blocks release |
| `standard` | Best practice | Warning |
| `optional` | Enhancement | Suggestion |

## Validation Rules

### Version Format
- Must follow semver (e.g., `1.0.0`, `1.2.3-beta.1`)
- Version must increment from previous release

### Documentation Requirements
- README.md must exist
- SKILL.md must exist
- No Chinese characters in documentation
- All headings properly capitalized

### Security Checks
- No hardcoded secrets
- No vulnerable dependencies
- Safe file permissions (644 for files, 755 for executables)

## Output

The tool produces a JSON report:

```json
{
  "skill": "example-skill",
  "version": "1.2.0",
  "timestamp": "2024-03-12T09:00:00Z",
  "checks": {
    "security": { "status": "pass", "issues": 0 },
    "docs": { "status": "pass", "issues": 0 },
    "version": { "status": "pass", "issues": 0 },
    "deps": { "status": "pass", "issues": 0 }
  },
  "overall": "pass",
  "warnings": [],
  "errors": []
}
```

## Exit Codes

- `0` - All checks passed
- `1` - One or more checks failed
- `2` - Invalid arguments or skill not found

## Limitations

- Does not execute skill code (use testing framework for that)
- Cannot verify runtime behavior
- Does not check external API availability

## Related Skills

- [skill-safety-auditor](./skill-safety-auditor) - Detailed security auditing
- [security-auditor](./security-auditor) - Security vulnerability scanning
- [release-skills](./release-skills) - Publishing workflow