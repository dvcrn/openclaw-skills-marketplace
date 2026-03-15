# OpenClaw Claude Marketplace

This repository converts the upstream `openclaw/skills` repository into a Claude Code plugin marketplace.

## Source Layout

The generator reads canonical source skills from:

```text
openclaw-skills/skills/<owner>/<slug>/
```

Each source skill is expected to contain:

- `_meta.json`
- `SKILL.md` or lowercase `skill.md`

The generator treats each canonical source skill as one Claude plugin. It normalizes lowercase `skill.md`, extracts plugin-root assets like `agents/`, `hooks/`, `.mcp.json`, and `settings.json`, and writes skipped-skill details to `reports/generate-marketplace.json`.

## Generate

```bash
mise run generate_marketplace
```

That writes:

- `.claude-plugin/marketplace.json`
- `plugins/<plugin-id>/...`
- `reports/generate-marketplace.json`

For development runs you can call the script directly:

```bash
python3 scripts/generate_marketplace.py --source openclaw-skills/skills --output . --limit 10
```

## Test

```bash
mise run test
```

## Notes

- Plugin ids are generated as `<owner>--<slug>` after sanitization.
- Nested source `skills/` directories are preserved as plugin content rather than treated as new top-level plugins.
- The generator replaces previous generated output under `.claude-plugin/`, `plugins/`, and `reports/` on each run.

