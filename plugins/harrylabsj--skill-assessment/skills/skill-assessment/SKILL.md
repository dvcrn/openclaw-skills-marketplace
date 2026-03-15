---
name: skill-assessment
description: "Evaluate OpenClaw skills with lightweight static analysis across documentation completeness, code quality, configuration friendliness, and maintenance signals. Use when comparing skills, checking release readiness, or finding weaknesses before publishing."
---

# Skill Assessment

A lightweight static analysis tool for evaluating the quality of OpenClaw skills.

## What It Checks

- documentation completeness
- code quality and safety signals
- configuration friendliness
- maintenance and versioning signals

## Typical Use Cases

- compare similar skills before installing
- assess a skill before publishing it
- batch-review local skills to find weak spots
- generate a report for follow-up improvements

## Typical Commands

```bash
skill-assess ~/.openclaw/skills/skill-creator
skill-assess .
skill-assess --all
skill-assess ~/.openclaw/skills/skill-creator --format json
skill-assess ~/.openclaw/skills/skill-creator --problems-only
skill-assess --compare skill-creator skill-audit
```

## Scoring Dimensions

1. documentation completeness
2. code quality
3. configuration friendliness
4. maintenance activity
