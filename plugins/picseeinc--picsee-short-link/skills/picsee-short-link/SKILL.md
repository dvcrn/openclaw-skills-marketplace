---
name: picsee-short-link
description: "PicSee URL shortener with QR code generation, analytics charts, and link management via CLI. Use when the user asks to shorten a URL, generate QR codes, visualize analytics, list/search links, or mentions PicSee. Supports unauthenticated mode (basic shortening + QR codes + charts) and authenticated mode (full analytics, editing, search). Token stored with AES-256-CBC encryption."
---

# PicSee Short Link

URL shortener with **QR code generation**, **analytics charts**, and link management via **CLI**.

Works with any agent that can run shell commands (OpenClaw, Claude Code, Codex, etc.).

---

## CLI Path

```
node ~/.openclaw/workspace/skills/picsee-short-link/cli/dist/cli.js
```

For brevity, examples below use `picsee` as alias.

---

## Quick Reference

### Shorten a URL
```bash
picsee shorten "https://example.com/long-url"
picsee shorten "https://example.com" --slug mylink
picsee shorten "https://example.com" --slug mylink --domain pse.is --title "My Title" --tags seo,marketing
```

### Analytics
```bash
picsee analytics mylink
```

### Generate Analytics Chart
```bash
picsee chart mylink
```
Fetches analytics and returns a QuickChart URL visualizing daily clicks.

### Generate QR Code
```bash
picsee qr "https://pse.is/mylink"
picsee qr "https://pse.is/mylink" --size 500
```

### List Links
```bash
picsee list
picsee list --limit 10
picsee list --start "2026-03-31T23:59:59" --keyword "campaign"
picsee list --tag seo --starred
```

`--start` queries backward from that time (default: now). **Use the END of the period**, e.g. `2026-03-31T23:59:59` for March 2026.

### Edit a Link
```bash
picsee edit mylink --url "https://new-destination.com"
picsee edit mylink --slug newslug --title "New Title" --tags a,b,c
```
Requires Advanced plan.

### Delete / Recover
```bash
picsee delete mylink
picsee recover mylink
```

### Authentication
```bash
picsee auth <token>
picsee auth-status
```
Token source: https://picsee.io → avatar → Settings → API → Copy token.

### Help
```bash
picsee help
```

---

## Full Options

### `shorten`
| Flag | Description |
|------|-------------|
| `--slug <slug>` | Custom slug (3-90 chars) |
| `--domain <domain>` | Short link domain (default: `pse.is`) |
| `--title <title>` | Preview title (Advanced plan) |
| `--desc <desc>` | Preview description (Advanced plan) |
| `--image <url>` | Preview thumbnail (Advanced plan) |
| `--tags t1,t2` | Comma-separated tags (Advanced plan) |
| `--utm s:m:c:t:n` | UTM params — source:medium:campaign:term:content |

### `list`
| Flag | Description |
|------|-------------|
| `--start <time>` | Query backward from this time (default: now) |
| `--limit <n>` | Results per page (1-50, default 50) |
| `--keyword <kw>` | Search title/description (Advanced, 3-30 chars) |
| `--tag <tag>` | Filter by tag (Advanced) |
| `--url <url>` | Filter by exact destination URL |
| `--slug <slug>` | Filter by exact slug |
| `--starred` | Starred links only |
| `--api-only` | API-generated links only |
| `--cursor <mapId>` | Pagination cursor |

### `edit`
| Flag | Description |
|------|-------------|
| `--url <url>` | New destination URL |
| `--slug <slug>` | New slug |
| `--domain <domain>` | New domain |
| `--title <title>` | New preview title |
| `--desc <desc>` | New preview description |
| `--image <url>` | New preview thumbnail |
| `--tags t1,t2` | New tags |
| `--expire <iso>` | Expiration time (ISO 8601) |

---

## Auth Modes

| Mode | API Host | Features |
|------|----------|----------|
| **Unauthenticated** | `chrome-ext.picsee.tw` | Create short links only |
| **Authenticated** | `api.pics.ee` | Create + analytics + list + search + edit + delete |

Auto-detected: if encrypted token exists at `~/.openclaw/.picsee_token`, authenticated mode is used.

---

## Security

- **Token encryption**: AES-256-CBC, IV stored alongside ciphertext
- **Key derivation**: `SHA-256(random-salt + hostname + "-" + username)` — the 32-byte random salt is generated once and stored at `~/.openclaw/.picsee_salt` (mode `0600`), making the key unpredictable even if hostname/username are known
- **File permissions**: `0600` on both token and salt files

---

## Agent Recipes (Post-Processing)

### Download QR Code as Image

After `picsee qr`, download and send the image:

```bash
mkdir -p ~/.openclaw/workspace/skills/picsee-short-link/tmp
curl -s -o ~/.openclaw/workspace/skills/picsee-short-link/tmp/<ENCODE_ID>_qr.png "<originalQrUrl>"
```

Send via `message` tool with `filePath: "~/.openclaw/workspace/skills/picsee-short-link/tmp/<ENCODE_ID>_qr.png"`.

### Download Chart as Image

After `picsee chart`, download and send the image:

```bash
mkdir -p ~/.openclaw/workspace/skills/picsee-short-link/tmp
curl -s -o ~/.openclaw/workspace/skills/picsee-short-link/tmp/<ENCODE_ID>_chart.png "<originalChartUrl>"
```

Send via `message` tool with `filePath: "~/.openclaw/workspace/skills/picsee-short-link/tmp/<ENCODE_ID>_chart.png"`.
