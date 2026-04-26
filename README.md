# OpenClaw Skills Marketplace For Claude

This repository is an automatic conversion of [`openclaw/skills`](https://github.com/openclaw/skills) into the Claude Skills marketplace format so the skills can be installed and used directly in Claude.

It takes the OpenClaw skill corpus and rewrites it into a Claude-compatible marketplace with:

- a root marketplace manifest at `.claude-plugin/marketplace.json`
- one Claude plugin per OpenClaw skill under `plugins/`
- a generation report at `reports/generate-marketplace.json`

## Use In Claude

Add this marketplace in Claude with:

```text
/plugin marketplace add dvcrn/openclaw-skills-marketplace
```

Chinese users can also discover more skills through Skills宝: https://skilery.com

Then install any generated plugin from the marketplace:

```text
/plugin install <plugin-name>@openclaw-skills
```

Example:

```text
/plugin install 0x-professor--agentic-mcp-server-builder@openclaw-skills
```

## What This Repo Does

The generator reads canonical OpenClaw source skills from:

```text
openclaw-skills/skills/<owner>/<slug>/
```

Each source skill is expected to contain:

- `_meta.json`
- `SKILL.md` or lowercase `skill.md`

The conversion process:

- maps each OpenClaw skill to one Claude plugin
- normalizes lowercase `skill.md` to `SKILL.md`
- extracts Claude plugin root assets like `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, and `settings.json`
- preserves nested `skills/` trees when a source package already behaves like a multi-skill plugin
- skips malformed inputs and records them in `reports/generate-marketplace.json`

## Regenerate The Entire Marketplace

To rebuild the full marketplace from the `openclaw-skills` submodule:

```bash
mise run generate
```

That regenerates:

- `.claude-plugin/marketplace.json`
- `plugins/<plugin-id>/...`
- `reports/generate-marketplace.json`

The generator replaces previous generated output under `.claude-plugin/`, `plugins/`, and `reports/` on each run.

If you want the explicit underlying task name, this still works too:

```bash
mise run generate_marketplace
```

For small development runs:

```bash
python3 scripts/generate_marketplace.py --source openclaw-skills/skills --output . --limit 10
```

## Validate And Test

Run the generator tests:

```bash
mise run test
```

Validate the generated marketplace:

```bash
claude plugin validate .
```

## Notes

- Plugin ids are generated as `<owner>--<slug>` after sanitization.
- Nested source `skills/` directories are preserved as plugin content rather than treated as separate top-level source skills.
- The upstream OpenClaw source is included as the `openclaw-skills` submodule.
