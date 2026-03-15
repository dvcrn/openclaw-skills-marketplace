# Publishing to ClawHub

ClawHub serves skill bundles from its registry. When agents run `clawhub install ludwitt-university`, they get the **last published** version — not the repo.

## When to republish

- Changed `install.sh` (API URL, behavior)
- Changed `daemon.js`
- Changed `SKILL.md` (API docs, Base URL, install instructions)

## How to republish

```bash
cd ludwitt-skill   # from repo root
clawhub login      # if not already
clawhub publish . \
  --slug ludwitt-university \
  --version 1.0.1 \
  --changelog "Fix API base URL to opensource.ludwitt.com" \
  --tags latest
```

Bump the version (patch for URL/docs fixes, minor for new features). Use `--bump patch` to auto-increment.
