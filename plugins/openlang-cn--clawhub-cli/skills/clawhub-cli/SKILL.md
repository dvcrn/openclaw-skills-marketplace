---
name: clawhub-cli
description: "Use the ClawHub CLI to search, install, update, and publish agent skills from clawhub.ai. Use when you need to fetch new skills on the fly, sync installed skills to the latest or a specific version, or publish new or updated skill folders with the npm-installed ClawHub CLI."
---

# ClawHub CLI Helper

This skill guides the agent on how to use the **ClawHub CLI** to manage skills from the public ClawHub registry.

## When to Use

Use this skill when:

- The user wants to **search** for skills on ClawHub by name or natural language.
- The user wants to **install** a skill from ClawHub into a local workspace.
- The user wants to **update** installed skills to the latest or a specific version.
- The user wants to **publish** or **sync** local skill folders to ClawHub.

## Requirements

- ClawHub CLI installed globally, for example:

```bash
npm i -g clawhub
```

or

```bash
pnpm add -g clawhub
```

- User is logged in:

```bash
clawhub login
```

or

```bash
clawhub login --token <api-token>
```

## Common Workflows

### Search for skills

When the user wants to discover skills (for example "Postgres backup", "Git tools"):

```bash
clawhub search "your query"
```

You can suggest concrete queries or slugs based on what the user describes.

### Install a skill

To install a skill by slug into the current workspace (default `skills` directory under workdir):

```bash
clawhub install <skill-slug>
```

Examples:

```bash
clawhub install postgres-backup-tools
```

Use `--version <semver>` if the user needs a specific version instead of latest.

### List installed skills

To show what is currently installed according to the ClawHub lockfile:

```bash
clawhub list
```

### Update installed skills

To update all installed skills to their latest tagged versions:

```bash
clawhub update --all
```

To update a single skill:

```bash
clawhub update <skill-slug>
```

Use `--version <semver>` if the user needs to pin a specific version.

### Publish a single local skill

Given a local skill folder with a `SKILL.md`, for example `skills/my-skill`, recommend a command like:

```bash
clawhub publish ./skills/my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 0.1.0 \
  --tags latest
```

Adjust:

- `./skills/my-skill` to the user’s actual folder path.
- `slug` to a unique, lowercase, hyphenated identifier.
- `version` to a valid semver string (`0.1.0`, `1.0.0`, etc.).
- `tags` to appropriate labels (`latest`, `beta`, `internal`, and so on).

### Sync many skills at once

If the user has many skill folders under a root (for example `skills/`), suggest:

```bash
clawhub sync --all
```

Optional flags:

- `--tags latest` to tag new/updated versions.
- `--changelog "Update skills"` in non-interactive runs.
- `--bump patch|minor|major` for automatic version increments on existing skills.
- `--dry-run` to see what would be uploaded without actually publishing.

## Verification and Troubleshooting

After suggesting commands:

- Ask the user to check CLI output for errors.
- For publish/sync, optionally suggest:
  - `clawhub list` to verify local records.
  - Opening `clawhub.ai` and searching by slug or display name.
- If an error occurs (for example slug already exists, version conflict, not logged in), explain what it means and propose a corrected command (new slug, bumped version, or re-login).

