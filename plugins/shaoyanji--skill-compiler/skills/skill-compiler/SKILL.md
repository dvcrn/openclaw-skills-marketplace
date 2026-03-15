---
name: skill-compiler
description: "Compile SKILL.md files into runtime artifacts (SKILL.struct.json and SKILL.toon), verify freshness/health, and prepare portable publish-ready skill folders for ClawHub-style registries."
---

# skill-compiler

Compile-first workflow for skill runtime performance.

## Commands

```bash
# Check local dependencies
skills/public/skill-compiler/scripts/check-env

# Compile one skill doc
skills/public/skill-compiler/scripts/compile-skill --skill skills/todoist/SKILL.md

# Compile all SKILL.md under a root (default: ./skills)
skills/public/skill-compiler/scripts/compile-all --root skills
```

## Outputs

For each input `SKILL.md`, compiler generates sibling artifacts:
- `SKILL.struct.json` (canonical runtime structure)
- `SKILL.toon` (token-lean projection)

## Entrypoint trigger setup (`exe` / `execute`)

Preferred runtime trigger words:
- `exe <skill>`
- `execute <skill>`

Resolution order:
1. `SKILL.struct.json` / `SKILL.toon` (artifact-first)
2. `quick_cmd` from frontmatter
3. `SKILL.md` fallback

Use bundled helper:
```bash
skills/public/skill-compiler/scripts/exe skill-compiler
```

## Publish-ready shape

This folder is ClawHub-ready once versioned:
- `SKILL.md`
- `skill.yaml`
- `scripts/*`

Optional publish command:
```bash
clawhub publish ./skills/public/skill-compiler \
  --slug skill-compiler \
  --name "Skill Compiler" \
  --version 0.2.0 \
  --changelog "Add exe/execute trigger docs and artifact-first entrypoint"
```
