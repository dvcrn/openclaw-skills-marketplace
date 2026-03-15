---
name: xhs-cli
description: "Install and use the `xhs-cli` terminal client for Xiaohongshu (小红书, RedNote, XHS). Use when Codex needs shell-driven Xiaohongshu operations such as checking login state, searching notes, reading note details, inspecting user profiles, browsing feed/topics, listing favorites, liking/favoriting/commenting, or publishing posts from the terminal."
---

# Xiaohongshu CLI

Use this skill for terminal-first Xiaohongshu work through `xhs-cli`.
Prefer shell commands over browser automation when the task fits the CLI.

## Quick Start

1. Check whether `xhs` is already installed with `xhs --version`.
2. If it is missing, install it with `uv tool install xhs-cli`.
3. If it is present but outdated, prefer `uv tool upgrade xhs-cli`.
4. Check auth with `xhs status`.
5. If auth is missing or stale, run `xhs login`.
6. Prefer `--json` when results will be parsed, summarized, or reused in later commands.

## Install

Prefer `uv`:

```bash
uv tool install xhs-cli
uv tool upgrade xhs-cli
```

Fallback to `pipx` if `uv` is unavailable:

```bash
pipx install xhs-cli
pipx upgrade xhs-cli
```

Only use a source checkout when the user is explicitly developing or patching the CLI itself:

```bash
git clone https://github.com/jackwener/xhs-cli.git
cd xhs-cli
uv sync
```

## Auth

Prefer `xhs login` first. It tries saved cookies, then local Chrome cookies, then QR login.

Use these checks in order:

```bash
xhs status
xhs login
xhs whoami --json
```

Do not ask the user to paste raw cookies into chat logs.
Only use `xhs login --cookie ...` if the user explicitly wants manual cookie input and can provide it locally.

## Core Workflows

### Search and Read

```bash
xhs search "coffee"
xhs search "coffee" --json
xhs read NOTE_ID
xhs read NOTE_ID --comments --json
```

Use `search` first when the user needs candidate notes.
Use `read` after a note ID is known.

### Profile and Network

```bash
xhs whoami --json
xhs user USER_ID --json
xhs user-posts USER_ID --json
xhs followers USER_ID --json
xhs following USER_ID --json
```

Use `whoami --json` to discover the current account's internal `userId`.

### Feed, Topics, and Favorites

```bash
xhs feed --json
xhs topics "travel" --json
xhs favorites --max 10 --json
```

Use `feed` for recommendation browsing.
Use `topics` for hashtag discovery.
Use `favorites` to inspect saved items.

### Interaction

Run `xhs status` before write actions.
For note actions, prefer working from IDs already returned by `search`, `feed`, or `read`.

```bash
xhs like NOTE_ID
xhs like NOTE_ID --undo
xhs favorite NOTE_ID
xhs favorite NOTE_ID --undo
xhs comment NOTE_ID "Helpful post."
xhs delete NOTE_ID
```

### Publish

```bash
xhs post "Title" --image ./cover.jpg --content "Body text"
xhs post "Title" --image ./a.jpg --image ./b.jpg --content "Body text" --json
```

Use `post` only after auth is confirmed.

## Response Style

Lead with the exact `xhs` command to run.
Keep flags minimal.
Prefer a short happy-path command before optional variants.
If the user still needs IDs, guide them to `search`, `feed`, or `whoami --json` first.

## Reference

Read `references/commands.md` when the user needs:

- full command coverage
- JSON-oriented examples
- installation variants
- publish examples
- troubleshooting guidance
