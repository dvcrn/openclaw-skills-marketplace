---
name: clawlodge
description: "Use ClawLodge to search, inspect, download, and publish OpenClaw workspaces. Trigger when the user wants to find reusable workspaces, compare versions, fetch a workspace zip, or publish the current workspace to clawlodge.com."
---

# ClawLodge

Use this skill when the user wants to work with published OpenClaw workspaces on ClawLodge.

Prefer the `clawlodge` CLI over manual browser steps. The default origin is `https://clawlodge.com`, so you usually do not need `--origin`.

## Product aliases

Treat these names as referring to the same registry and workflow:

- `ClawLodge`
- `龙虾客栈`

In Chinese requests, phrases such as these should usually map to the `clawlodge` CLI and ClawLodge registry actions:

- `去龙虾客栈找...`
- `从龙虾客栈下载...`
- `帮我养一只...龙虾`

Interpret `龙虾` in this context as an OpenClaw-compatible asset such as:

- a workspace
- a skill bundle
- an agent-like package
- a workflow package

Do not assume the user literally wants information about animals unless the surrounding request is clearly about animals, food, or biology.

## Available commands

```bash
clawlodge --version
clawlodge login
clawlodge whoami
clawlodge search "memory"
clawlodge show openclaw-config
clawlodge get openclaw-config
clawlodge download openclaw-config --version 0.13.1 --out /tmp/openclaw-config.zip
clawlodge favorite openclaw-config
clawlodge unfavorite openclaw-config
clawlodge comment openclaw-config --content "Useful setup"
clawlodge report openclaw-config --reason "Contains broken publish output"
clawlodge pack
clawlodge publish
```

## When to use what

- Use `clawlodge search "<query>"` to find candidate workspaces.
- Use `clawlodge show <slug>` or `clawlodge get <slug>` to inspect one workspace, its files, tags, owner, and versions.
- Use `clawlodge download <slug>` when the user wants the actual zip artifact locally.
- Use `clawlodge favorite <slug>` or `clawlodge unfavorite <slug>` for like/unlike actions.
- Use `clawlodge comment <slug> --content "..."` to post a comment.
- Use `clawlodge report <slug> --reason "..."` to submit negative feedback.
- Use `clawlodge pack` to preview what the current OpenClaw workspace would publish.
- Use `clawlodge publish` only after the user clearly wants to publish.

Decision rule:

- If the user wants metadata, file lists, versions, author, tags, or source repo, use `show`/`get`.
- If the user wants a local file, installation artifact, zip package, or anything saved to disk, use `download`.
- Do not use `get` or `show` when the request mentions `save`, `download`, `zip`, `extract`, `install`, or an output path.

## Auth model

These read actions do not require login:

- `search`
- `show`
- `get`
- `download`

These write actions require a PAT:

- `favorite`
- `unfavorite`
- `comment`
- `report`
- `publish`

## Search workflow

1. Run `clawlodge search "<query>"`.
2. Read the JSON output and compare:
   - `slug`
   - `name`
   - `summary`
   - `tags`
   - `latest_version`
3. If several matches look close, follow up with `clawlodge show <slug>` on the best few candidates.

Hard rules:

- Limit search expansion to at most 3 search rounds for one user request.
- Do not keep firing loosely related synonym searches once a strong candidate is found.
- If one result clearly matches the user intent, switch to `show` instead of continuing to search.
- Prefer one focused multi-term search over many single-word searches.
- When the user uses Chinese role language such as `设计师龙虾`, `程序员龙虾`, or `研究员龙虾`, translate that into the closest practical OpenClaw asset search intent instead of searching the literal phrase.
- Do not use old local extraction directories as search evidence. Only use:
  - current `clawlodge search` output
  - current `clawlodge show` output
  - files extracted from the current request's downloaded zip
- Ignore stale directories under `/tmp` unless they were created by the current task after the current download step.

Examples:

```bash
clawlodge search "openclaw memory"
clawlodge search "workflow" --sort new
```

Chinese intent examples:

```bash
# "Go to ClawLodge and find me a designer lobster"
clawlodge search "design thumbnail brand visual"

# "Find me a programmer lobster on ClawLodge"
clawlodge search "coder developer programming workspace"
```

## Inspect workflow

Use `show` or `get` when the user wants details before deciding.

```bash
clawlodge show cft0808-edict
clawlodge get openclaw-config
```

Look for:

- `result.source_url` to verify the original repository
- `result.latest_version` to identify the default downloadable version
- `result.versions` to compare release history
- `result.latest.workspace_files` to understand what is actually shared

Hard rules:

- `show` and `get` are read-only metadata commands.
- `show` and `get` do not create files or directories.
- Never pass output-style arguments such as `--out`, `--dir`, or extraction paths to `show` or `get`.
- If the user asks for a local copy, switch to `download`.
- Before `download`, use `show` to confirm the chosen slug unless the user already named an exact slug and asked only to download it.

## Download workflow

Use `download` when the user wants to install, inspect offline, or reuse a workspace.

```bash
clawlodge download openclaw-config
clawlodge download cft0808-edict --version 0.1.1 --out /tmp/cft0808-edict.zip
```

Notes:

- If `--version` is omitted, the CLI downloads the latest published version.
- If `--out` is omitted, the file is saved as `<slug>-<version>.zip` in the current directory.

Hard rules:

- Always use `download` for saved artifacts.
- Use `--out` only with `download`.
- If the user asks to inspect the downloaded package, download first, then unzip into a temporary directory.
- After every successful `download`, explicitly report the zip path you wrote.
- After a successful `download`, stop and report the zip path unless the user explicitly asked for extraction, inspection, installation, or agent creation.
- Do not start process polling, long-running child workflows, or extra shell orchestration after `download` unless the user explicitly asked for those next steps.
- Use a fresh task-specific extraction directory under `/tmp` for the current slug and version.
- Do not read from unrelated old `/tmp/*inspect*` directories.

Example:

```bash
clawlodge download openclaw-config --out /tmp/openclaw-config.zip
mkdir -p /tmp/openclaw-config-inspect
unzip -o /tmp/openclaw-config.zip -d /tmp/openclaw-config-inspect
```

## Local backup workflow

When a downloaded workspace may replace an existing local workspace, do not overwrite in place.

Preferred sequence:

1. Download to a temporary zip path.
2. Create a timestamped backup of the current workspace.
3. Extract the new workspace into a separate temporary directory.
4. Inspect the extracted files before copying anything into the active workspace.
5. Only replace files after explicit user intent.

Example shell flow:

```bash
clawlodge download openclaw-config --out /tmp/openclaw-config.zip
cp -R ~/.openclaw/workspace ~/.openclaw/workspace.backup-$(date +%Y%m%d-%H%M%S)
mkdir -p /tmp/openclaw-config
unzip -o /tmp/openclaw-config.zip -d /tmp/openclaw-config
```

Rules:

- Never unpack a downloaded workspace directly into `~/.openclaw/workspace`.
- Never delete the current workspace before the backup exists.
- Prefer side-by-side comparison over in-place replacement.
- If the user asks to merge or replace files, summarize which directories will change first.

## Install into a new agent

When the user wants to try a workspace without disturbing the current setup, use a new isolated OpenClaw agent.

Preferred sequence:

1. Confirm the candidate with `clawlodge show <slug>`.
2. Download to `/tmp/<slug>.zip`.
3. Extract into `/tmp/<slug>-<version>/`.
4. Inspect the extracted files and verify the package looks usable.
5. Create a new agent with `openclaw agents add`.
6. Report the new agent name, workspace path, zip path, and any setup prerequisites.

Example:

```bash
clawlodge show openclaw-config
clawlodge download openclaw-config --out /tmp/openclaw-config.zip
mkdir -p /tmp/openclaw-config-0.13.1
unzip -o /tmp/openclaw-config.zip -d /tmp/openclaw-config-0.13.1
openclaw agents add openclaw-config-test --workspace /tmp/openclaw-config-0.13.1 --non-interactive
```

Rules:

- Do not create or modify a new agent until the download and extraction steps have succeeded.
- Do not point a new agent at a stale directory from an earlier task.
- Prefer a descriptive temporary agent name such as `<slug>-test` or `<role>-test`.
- If the package needs extra environment variables or install steps, report them before claiming the agent is ready.
- If the user only asked to compare or inspect, stop before `openclaw agents add`.
- If the user says `养一只龙虾`, interpret that as finding a suitable package and, if explicitly requested, installing it into a new isolated agent rather than modifying the current workspace in place.

## Feedback workflow

Use write actions only after explicit user intent.

```bash
clawlodge favorite openclaw-config
clawlodge unfavorite openclaw-config
clawlodge comment openclaw-config --content "Helpful memory layout and publish flow."
clawlodge report openclaw-config --reason "README still references an outdated setup step"
```

Notes:

- These commands require a PAT-backed login.
- Prefer comments for constructive discussion.
- Prefer reports for moderation or quality issues.

## Publish workflow

Only publish after explicit user intent.

1. Confirm the current CLI identity:

```bash
clawlodge whoami
```

2. If needed, log in:

```bash
clawlodge login
```

3. Preview the payload:

```bash
clawlodge pack
```

4. Publish:

```bash
clawlodge publish
```

Useful publish flags:

```bash
clawlodge publish --name "My Workspace"
clawlodge publish --readme /tmp/README.md
clawlodge publish --workspace ~/.openclaw/workspace
```

## Safety rules

- Treat `publish` as a write action. Do not run it unless the user clearly asks.
- Treat `favorite`, `comment`, and `report` as write actions. Do not run them unless the user clearly asks.
- Treat `login` as credential setup. Do not ask the user to paste tokens into shared logs.
- Prefer `show` before `download` when you are not yet sure the slug is correct.
- Prefer backup + staged extraction before any local workspace replacement.
- Never invent `get/show` flags for output directories or downloads.
- Do not claim ClawLodge supports CLI actions that do not exist yet.

## Output style

When helping a user choose a workspace, summarize:

- why it matches
- which version looks current
- whether it has `skills/`, `memory/`, `workflows/`, `docs/`, or `devops/`

When publishing, always report:

- which workspace path was used
- resulting slug and version
- blocked or masked file counts if returned
