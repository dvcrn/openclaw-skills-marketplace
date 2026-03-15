---
name: clawhub-publish
description: "Create, package, and publish OpenClaw skills to ClawHub. Use when you need to: (1) build a new skill from scratch, (2) package a skill into a .skill file, (3) publish or update a skill on clawhub.com, (4) set up a GitHub repo for a skill, (5) audit a skill before publishing. Covers the full lifecycle from idea to published skill, including frontmatter, scripts, references, validation, versioning, and the clawhub CLI. Complements the skill-creator skill with ClawHub-specific publishing workflow and practical patterns."
---

# ClawHub Skill Publishing

End-to-end workflow for creating and publishing OpenClaw skills to ClawHub.

## Quick reference

```bash
# Create
scripts/init_skill.py my-skill --path . --resources scripts,references

# Validate
python3 scripts/quick_validate.py my-skill/

# Package
python3 scripts/package_skill.py my-skill/

# Publish
clawhub login
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --changelog "Initial release"

# Update
clawhub publish ./my-skill --slug my-skill --version 1.1.0 --changelog "Added feature X"

# Sync all local skills
clawhub sync --dry-run
clawhub sync --all --bump patch --changelog "Bug fixes"
```

## Workflow

### 1. Plan the skill

Before writing code, clarify:

- **What triggers it?** — what would a user say that should activate this skill?
- **What scripts are needed?** — what operations are fragile, repetitive, or need determinism?
- **What references are needed?** — what API docs, schemas, or domain knowledge should be available?
- **What dependencies are required?** — what bins/packages must be present?

### 2. Create the skill

Use the init script from skill-creator (if available), or create manually:

```
my-skill/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Optional: executable code
├── references/        # Optional: API docs, schemas
└── assets/            # Optional: templates, images
```

### 3. Write SKILL.md

#### Frontmatter (critical for triggering)

```yaml
---
name: my-skill
description: >
  One-paragraph description of what the skill does AND when to use it.
  Include specific trigger phrases. This is the ONLY thing the agent sees
  before deciding to load the skill, so be comprehensive.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔧",
        "os": ["linux", "darwin"],
        "requires": { "bins": ["curl", "jq"], "anyBins": ["node", "bun"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "my-tool",
              "bins": ["my-tool"],
              "label": "Install my-tool (brew)",
            },
          ],
      },
  }
---
```

**Requires options:**
- `bins`: ALL must be present
- `anyBins`: at least ONE must be present

**Install kinds:** `brew`, `node`, `pip`, `cargo`, `go`

#### Body guidelines

- Keep under 500 lines (context window is shared)
- Use imperative form ("Run the script", not "You should run")
- Show concrete examples, not verbose explanations
- Put detailed API docs in `references/`, not in the body
- Reference scripts by relative path: `scripts/my_script.sh`

### 4. Write scripts

**When to use scripts:**
- Same code would be rewritten every time
- Deterministic reliability is needed
- Complex parsing or encoding (bitfields, binary formats)
- Multi-step API workflows with error handling

**Script conventions:**
- Add shebang: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`
- Make executable: `chmod +x scripts/*.sh`
- Use `set -euo pipefail` in bash scripts
- Print progress/status to stderr, data to stdout
- Support `--help` and `--json` flags where appropriate
- Use env vars for configuration, with sensible defaults

**Common patterns:**
- Auth scripts: cache credentials in `~/.openclaw/credentials/`
- API scripts: follow redirects (`curl -sfL`), handle JSON errors
- Download scripts: dry-run by default, support `--limit`

### 5. Pre-publish checklist

Before publishing, verify:

- [ ] No secrets in code or git history (passwords, tokens, API keys)
- [ ] No hardcoded user-specific paths or credentials
- [ ] Scripts are executable (`chmod +x`)
- [ ] curl calls follow redirects (`-L` flag) where needed
- [ ] All jq filters handle null/missing fields gracefully
- [ ] Bash pipes that need variable persistence use process substitution (`< <(...)`) not `|`
- [ ] `description` in frontmatter includes trigger phrases
- [ ] `.gitignore` excludes `.skill` packages
- [ ] Scripts tested against real data

### 6. Validate and package

```bash
# Validate only
python3 ~/openclaw_repo/skills/skill-creator/scripts/quick_validate.py ./my-skill

# Package (validates first, then creates .skill zip)
python3 ~/openclaw_repo/skills/skill-creator/scripts/package_skill.py ./my-skill
```

Packaging checks: frontmatter format, required fields, naming conventions, directory structure, no symlinks.

### 7. Publish to ClawHub

```bash
# First time
clawhub login                    # Opens browser for OAuth
clawhub whoami                   # Verify auth

# Publish new skill
clawhub publish ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 1.0.0 \
  --changelog "Initial release"

# Update existing skill
clawhub publish ./my-skill \
  --slug my-skill \
  --version 1.1.0 \
  --changelog "Added feature X, fixed bug Y"

# Bulk sync all local skills
clawhub sync --dry-run           # Preview
clawhub sync --all --bump patch  # Publish all changes
```

**Versioning:** Use semver. Bump major for breaking changes, minor for features, patch for fixes.

### 8. Set up GitHub repo (optional but recommended)

```bash
cd my-skill
git init
echo "*.skill" > .gitignore
git add -A && git commit -m "Initial implementation"
gh repo create org/my-skill --private --source=. --push \
  --description "OpenClaw skill: short description"

# Make public when ready
gh repo edit org/my-skill --visibility public --accept-visibility-change-consequences
```

Users can then install via git clone as an alternative to ClawHub:
```bash
cd /path/to/workspace/skills && git clone https://github.com/org/my-skill.git
```

## ClawHub CLI reference

See `references/clawhub_cli.md` for the full command reference.

## Lessons learned

See `references/patterns.md` for common pitfalls and solutions discovered during real skill development.
