---
name: openclaw-scrapefun
description: "Use this skill when OpenClaw needs to operate a scrapefun server through regular business APIs: authenticate with access key or app token, inspect libraries and metadata stats, run scrape and WebDAV endpoints, and report results without using /api/openclaw/*."
---

# OpenClaw Scrapefun

## Overview

Use this skill when the task is about operating a `scrapefun` instance through its regular business APIs. Treat the skill as an API operation guide, not as a content-source guide.

Default API base is `http://localhost:4000`.

API key

- Preferred env: `OPENCLAW_ACCESS_KEY`
- OpenClaw dashboard `Save key` writes to `skills.entries["openclaw-scrapefun"].apiKey`
- OpenClaw may also expose that value as `skills.entries["openclaw-scrapefun"].env.OPENCLAW_ACCESS_KEY`
- Never use `OPENCLAW_SCRAPEFUN_API_KEY` in this skill

Preferred auth order:

1. Use `X-OpenClaw-Key` if the user has configured an OpenClaw access key in Settings.
2. Fall back to `POST /api/auth/login` only when no access key is available.

Read [references/api.md](./references/api.md) only when you need endpoint shapes or payload examples.

## Workflow

### 1. Authenticate

Preferred method:

- Send `X-OpenClaw-Key: <access key>` on protected `/api/*` business endpoints.

Fallback method:

- `POST /api/auth/login`
- Send `username` and `password`
- Reuse the returned `Authorization: Bearer <token>` on later requests

Rules:

- Prefer `X-OpenClaw-Key` when `OPENCLAW_ACCESS_KEY` or the saved skill apiKey is available
- Do not ask for username/password if a valid access key is already available
- If neither access key nor admin credentials are available, ask for one of them before continuing

### 2. Load libraries and context

- `GET /api/libraries`

Use returned libraries (`name`, `type`, `sourceMode`, `path`) to decide targets. Prefer explicit user input. If the target must be inferred, state that clearly.

### 3. Query counts and status

- Library/global counts:
  - `GET /api/metadata/stats`
  - `GET /api/metadata/count` (optional fallback)

For "how many movies":

1. Filter libraries where `type === "movie"`.
2. Read `directories[library.name]` from `/api/metadata/stats`.
3. Sum matched values and return per-library + total movie count.

### 4. Run regular scrape and WebDAV operations

Use standard endpoints according to request type:

- Search metadata candidates:
  - `GET /api/scrape/search`
- Match content to metadata:
  - `POST /api/scrape/match-folder`
  - `POST /api/scrape/match`
- Rescan/update media index:
  - `POST /api/scrape/webdav/scan`
  - `POST /api/scrape/webdav/update`
- File operations:
  - `POST /api/settings/webdav/move`
  - `POST /api/settings/webdav/move_thunder_batch`
  - `POST /api/settings/webdav/rename`
  - `POST /api/settings/webdav/add_offline_download`
- OpenClaw-exposed library scan:
  - `POST /api/openclaw/libraries/scan`
  - Preferred payload: `{ "libraryName": "<library name>" }`
  - Optional explicit payload: `{ "path": "<path or path[]>", "scraper": "<scraper>", "type": "<movie|tv>" }`

Rules:

- Send only required fields for each endpoint
- Use explicit library/path/scraper inputs from user or prior API results
- If required fields are missing, stop and ask for them

### 5. Prohibited endpoints in this skill

Do not use these endpoints in this skill:

- `/api/openclaw/bootstrap/status`
- `/api/openclaw/connect/context`
- `/api/openclaw/tasks/*`
- `/api/openclaw/workflows/*`
- `/api/openclaw/jobs/*`
- `/api/openclaw/sites/*`

Also do not rely on `OPENCLAW_URL` remote delegation flow.
Never use header names other than `X-OpenClaw-Key` for access key auth.
The only allowed `/api/openclaw/*` endpoint in this skill is `POST /api/openclaw/libraries/scan`.

## Response Style

When acting through this skill:

- State the auth method explicitly: `X-OpenClaw-Key` or bearer token
- State the endpoint and payload shape explicitly
- Mention when any choice is inferred rather than provided
- Keep responses constrained to API parameters and returned results
- Surface blockers directly: missing key/token, missing required fields, missing target library/path

## Examples

### Movie counts

User request:

`我想看下有多少电影`

Execution pattern:

1. `GET /api/libraries`
2. Keep libraries with `type === "movie"`
3. `GET /api/metadata/stats`
4. Sum `directories[library.name]` for movie libraries
5. Return per-library counts + total

### Folder match and refresh

User request:

`把这个目录匹配并刷新`

Execution pattern:

1. `POST /api/scrape/match-folder` with explicit `path` and scraper params
2. `POST /api/scrape/webdav/scan`
3. `POST /api/scrape/webdav/update`
