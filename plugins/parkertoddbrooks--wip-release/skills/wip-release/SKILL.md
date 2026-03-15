---
name: wip-release
description: "One-command release pipeline. Bumps version, updates changelog + SKILL.md, publishes to npm + GitHub."
---

# wip-release

Local release pipeline. One command bumps version, updates all docs, publishes everywhere.

## When to Use This Skill

**Use wip-release for:**
- Releasing a new version of any @wipcomputer package
- After merging a PR to main and you need to publish
- Bumping version + changelog + SKILL.md in one step

**Use --dry-run for:**
- Previewing what a release would do before committing

**Use --no-publish for:**
- Bumping version and tagging without publishing to registries

### Do NOT Use For

- Pre-release / alpha versions (not yet supported)
- Repos without a package.json

## API Reference

### CLI

```bash
wip-release patch --notes="fix X"           # full pipeline
wip-release minor --dry-run                 # preview only
wip-release major --no-publish              # bump + tag only
wip-release patch --skip-product-check      # skip product docs gate
```

### Product Docs Gate

wip-release checks that product docs (dev update, roadmap, readme-first) were updated before publishing. Only runs on repos with an `ai/` directory.

- **patch**: warns if product docs are stale (non-blocking)
- **minor/major**: blocks release until product docs are updated
- **--skip-product-check**: bypasses the gate

Checks:
1. `ai/dev-updates/` has a file from the last 3 days
2. `ai/product/plans-prds/roadmap.md` was modified since last release
3. `ai/product/readme-first-product.md` was modified since last release

### Module

```javascript
import { release, detectCurrentVersion, bumpSemver, syncSkillVersion } from '@wipcomputer/wip-release';

await release({ repoPath: '.', level: 'patch', notes: 'fix', dryRun: false, noPublish: false });
```

## Troubleshooting

### "Could not fetch npm token from 1Password"
Check that `~/.openclaw/secrets/op-sa-token` exists and `op` CLI is installed.

### "Push failed"
Branch protection may prevent direct pushes. Make sure you're on main after merging a PR.

### SKILL.md not updated
Only updates if the file has a YAML frontmatter `version:` field between `---` markers.

## MCP

Tools: `release`, `release_status`

Add to `.mcp.json`:
```json
{
  "wip-release": {
    "command": "node",
    "args": ["/path/to/tools/wip-release/mcp-server.mjs"]
  }
}
```
