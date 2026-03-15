# Install via CLI

## Option A: install from this local repo

Run from repo root:

```bash
bash scripts/install-gougoubi-create-prediction-skill.sh
```

This copies:

- `skills/gougoubi-create-prediction/SKILL.md`

to:

- `~/.codex/skills/gougoubi-create-prediction/SKILL.md`

## Option B: install from GitHub

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/gougoubi-create-prediction
```

## Verify

```bash
ls -la ~/.codex/skills/gougoubi-create-prediction
```

## Final step

Restart Codex/Cursor agent runtime to load the new skill.
