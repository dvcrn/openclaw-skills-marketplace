# Severity Matrix

## Issue Classification

### Critical (Blocks Release)

| Issue | Description | Example |
|-------|-------------|---------|
| MISSING_SKILL_MD | No SKILL.md file | Directory exists but no skill definition |
| INVALID_FRONTMATTER | YAML frontmatter malformed | Missing closing `---` |
| MISSING_NAME | No name field in frontmatter | `name:` not found |
| MISSING_DESCRIPTION | No description field | `description:` not found |
| NESTED_SKILL | SKILL.md in subdirectory | `lib/SKILL.md` exists |
| SECRET_DETECTED | Potential secret in content | `api_key: abc123` |
| DANGEROUS_COMMAND | rm -rf / or similar | Unrestricted destructive command |

### Warning (Should Fix)

| Issue | Description | Example |
|-------|-------------|---------|
| NO_REFERENCES | Missing references/ directory | Documentation not organized |
| SCRIPTS_NOT_EXECUTABLE | Scripts lack +x permission | `scripts/test.sh` not executable |
| SHORT_DESCRIPTION | Description < 20 chars | "A skill" |
| SHORT_CONTENT | SKILL.md < 50 lines | Minimal documentation |
| NO_EXAMPLES | No trigger examples | Users won't know how to use |
| NO_TEST_SCRIPT | Missing scripts/test.sh | No automated testing |
| ABSOLUTE_PATH | Hardcoded absolute path | `/Users/name/...` in script |

### Info (Nice to Have)

| Issue | Description | Example |
|-------|-------------|---------|
| NO_README | Missing README.md | Only SKILL.md present |
| NO_LICENSE | Missing LICENSE file | Unclear usage rights |
| NO_CHANGELOG | Missing CHANGELOG.md | No version history |
| UNCOMMON_TAG | Non-standard tag used | Custom tag not in taxonomy |

## Severity Overrides

Users can override severity with comments in SKILL.md:

```markdown
<!-- release-guard: ignore SECRET_DETECTED -->
This is a demo key, not real: api_key: demo123
```

```markdown
<!-- release-guard: warn NO_TEST_SCRIPT -->
This skill doesn't need tests (documentation only)
```

## Auto-Fix Rules

Some issues can be auto-fixed:

| Issue | Auto-Fix | Command |
|-------|----------|---------|
| SCRIPTS_NOT_EXECUTABLE | Yes | `chmod +x scripts/*.sh` |
| NO_REFERENCES | Yes | `mkdir -p references` |
| NO_README | Partial | Scaffold from SKILL.md |

## Scoring Formula

```
Total = (Critical_Passed * 10) + (Standard_Passed * 5) + (Optional_Passed * 2)
Max = (Critical_Total * 10) + (Standard_Total * 5) + (Optional_Total * 2)
Score = (Total / Max) * 100
```

**Release Criteria:**
- Score >= 80%: Approved
- Score >= 60%: Approved with warnings
- Score < 60%: Blocked
- Any Critical failed: Blocked regardless of score
