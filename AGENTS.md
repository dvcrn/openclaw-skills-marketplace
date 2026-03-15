- Repo: <owner>/openclaw-claude-skills-marketplace

# Marketplace Structure

This repository is a Claude Code plugin marketplace. Its job is to publish a root marketplace catalog and one or more plugin directories that Claude Code can install.

Use the official Claude plugin layout as the source of truth. Use `~/src/skills` as a content and organization reference, not as a replacement for the Claude marketplace spec.

## Required Root Layout

```text
.
├── .claude-plugin/
│   └── marketplace.json
├── AGENTS.md
├── README.md
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── skills/
        │   └── <skill-name>/
        │       └── SKILL.md
        ├── commands/
        ├── agents/
        ├── hooks/
        │   └── hooks.json
        ├── scripts/
        ├── .mcp.json
        ├── .lsp.json
        └── settings.json
```

Only `.claude-plugin/plugin.json` belongs inside a plugin’s `.claude-plugin/` directory. `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, and `settings.json` must live at the plugin root.

## Required Files

### Root marketplace manifest

Path: `.claude-plugin/marketplace.json`

This file is required. It defines:

- `name`: marketplace identifier, kebab-case, unique, not an Anthropic-reserved name
- `owner`: maintainer object, at minimum `name`
- `plugins`: array of plugin entries

Each plugin entry must have at minimum:

- `name`
- `source`

For plugins stored in this repository, use relative sources such as:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "Short description"
}
```

### Plugin manifest

Path: `plugins/<plugin-name>/.claude-plugin/plugin.json`

Claude Code can infer some metadata without this file, but this repository should require it for every plugin so names, versions, and descriptions stay explicit and consistent.

Minimum required field by Claude Code:

- `name`

Repository policy for this marketplace:

- always include `name`
- always include `description`
- always include `version`
- include `author.name`
- include `author.email` when available
- include `homepage` and `repository` when the plugin has public docs or source

Example:

```json
{
  "name": "my-plugin",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Maintainer Name",
    "email": "maintainer@example.com"
  }
}
```

### Skill files

Path: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`

Every skill must live in its own directory and expose a `SKILL.md`. Use frontmatter plus instruction body.

Minimum frontmatter we should require:

- `name`
- `description`

Common optional frontmatter:

- `disable-model-invocation`

Example:

```md
---
name: code-review
description: Review code for bugs, security issues, and maintainability problems.
---

Review the provided code and report actionable findings.
```

## Optional Plugin Files

These are supported by Claude Code and should be added only when the plugin needs them:

- `commands/`: legacy command markdown files
- `agents/`: custom agent definitions
- `hooks/hooks.json`: hook configuration
- `.mcp.json`: MCP server definitions
- `.lsp.json`: LSP server definitions
- `settings.json`: plugin-default settings, currently mainly `agent`
- `scripts/`: helper scripts used by hooks or other plugin assets

## Repo-Specific Convention From `~/src/skills`

The sample repository at `~/src/skills` adds some useful content conventions that are not required by Claude Code itself:

- `plugins/<plugin>/skills/<skill>/references/`
- `plugins/<plugin>/skills/<skill>/agents/openai.yaml`

We can keep those when they are useful, but they are internal repo conventions. They are not what makes this repository a valid Claude marketplace.

## `.claude` vs `.claude-plugin`

Do not confuse these:

- `.claude-plugin/` is part of the marketplace and plugin authoring format. This repository needs it.
- `.claude/` is for Claude Code settings in a user home directory or a consuming project. This repository does not need a `.claude/` directory just to function as a marketplace.

Relevant install scopes from the docs:

- user scope writes to `~/.claude/settings.json`
- project scope writes to `.claude/settings.json` in the consumer project
- local scope writes to `.claude/settings.local.json` in the consumer project

That means `.claude/settings.json` matters when someone installs plugins from this marketplace into another project. It is not a required artifact of the marketplace repository itself.

## Naming And Versioning Rules

- Marketplace names must be kebab-case and must not imitate Anthropic-owned marketplace names.
- Plugin names must be unique across the marketplace and kebab-case.
- Skill directory names should match the skill’s `name` unless there is a strong reason not to.
- Versions should be semantic versions.
- Keep the plugin `name` in `plugin.json` aligned with the corresponding marketplace entry `name`.

## Path Rules

- Use relative paths in marketplace and plugin manifests.
- Do not rely on files outside the plugin directory with paths like `../shared-utils`.
- Claude Code copies installed plugin directories into a cache, so external references will break.
- If multiple plugins need shared content, duplicate it intentionally or use symlinks that resolve inside the copied plugin tree.

## Discovery And Installation Model

Consumers use marketplaces in two steps:

1. Add the marketplace
2. Install individual plugins from it

That means this repository must optimize for discoverability as well as validity:

- every plugin should have a clear `description`
- every plugin should have stable naming
- plugins should include `homepage` in `plugin.json` when possible because users are told to inspect plugin homepages before installing

Common install paths from the docs:

- GitHub repo: `/plugin marketplace add owner/repo`
- Other git host: `/plugin marketplace add https://gitlab.com/company/plugins.git`
- Local path: `/plugin marketplace add ./my-marketplace`
- Direct manifest URL: `/plugin marketplace add https://example.com/marketplace.json`

This implies the repository should be usable both as:

- a git-hosted marketplace repo
- a local development marketplace on disk
- optionally a hosted `marketplace.json` endpoint

## Installation Scopes In Consumer Projects

Plugin installation scopes affect where Claude writes settings in the consuming environment:

- user scope: installs for one user across projects
- project scope: shared for collaborators and written to `.claude/settings.json`
- local scope: local-only for one user in a project

This repository is not required to contain `.claude/settings.json`, but marketplace authors should understand that project-scope installs modify that file in consumer repositories.

## Team Distribution

Teams can pre-configure known marketplaces in a consuming repository’s `.claude/settings.json` using `extraKnownMarketplaces`. That means this marketplace should keep its source location stable once published.

Example consumer-side configuration from the docs:

```json
{
  "extraKnownMarketplaces": {
    "my-team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}
```

## Auto-Update Expectations

- Official Anthropic marketplaces auto-update by default.
- Third-party marketplaces and local development marketplaces do not auto-update by default.
- When a marketplace or plugin updates, Claude may prompt users to run `/reload-plugins`.

This means releases in this repository should favor compatibility and clear versioning. Users will not necessarily receive updates immediately unless they refresh the marketplace or enable auto-update.

## Security Expectations

Plugins and marketplaces are highly trusted and can execute arbitrary code with the user’s privileges. Because of that:

- do not include unnecessary executables or scripts
- keep plugin contents minimal and auditable
- document external systems or MCP servers clearly
- prefer transparent descriptions over vague marketing copy
- include a `homepage` or repository URL whenever possible so users can review the source

## Validation And Local Testing

Validate the marketplace from the repo root:

```bash
claude plugin validate .
```

Test the marketplace locally:

```bash
/plugin marketplace add .
/plugin install <plugin-name>@<marketplace-name>
```

Test an individual plugin directly during development:

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

Then reload in-session after edits:

```text
/reload-plugins
```

## Minimum Done Criteria

A change is not complete unless all of the following are true:

- `.claude-plugin/marketplace.json` exists and validates
- every listed plugin has `plugins/<plugin-name>/.claude-plugin/plugin.json`
- every shipped skill has `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- plugin names are unique and match between `marketplace.json` and `plugin.json`
- no plugin components are incorrectly nested inside `.claude-plugin/`
- local validation has been run with `claude plugin validate .`

## Recommended First Scaffold

When bootstrapping this repository, create these files first:

- `.claude-plugin/marketplace.json`
- `README.md`
- `AGENTS.md`
- `plugins/<first-plugin>/.claude-plugin/plugin.json`
- `plugins/<first-plugin>/skills/<first-skill>/SKILL.md`

Add optional files only when the plugin actually needs commands, agents, hooks, MCP servers, LSP servers, or default settings.

## Sources

- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/discover-plugins
- https://code.claude.com/docs/en/plugin-marketplaces
- https://code.claude.com/docs/en/plugins-reference
