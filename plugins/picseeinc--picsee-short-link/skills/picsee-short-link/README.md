# 🔗 Skill for PicSee URL Shortener

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Open_Standard-blue.svg)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **CLI-based [Agent Skill](https://agentskills.io)** for [PicSee](https://picsee.io) — URL shortening with QR code generation, click analytics, and link management.

Works with any AI agent that supports the Agent Skills standard or can run shell commands.

---

## 📖 Resources

- **PicSee Website:** [https://picsee.io](https://picsee.io)
- **API Documentation:** [https://picsee.io/developers/docs/public-api.html](https://picsee.io/developers/docs/public-api.html)
- **Agent Skills Spec:** [https://agentskills.io](https://agentskills.io)

---

## 🌟 Features

- **Dual-Mode Operation** — Unauthenticated (basic shortening) and Authenticated (full management) with automatic detection
- **URL Shortening + QR Codes** — Create short links and instantly generate QR codes (300x300px, customizable)
- **Visual Analytics** — Total clicks, unique clicks, daily trends, and chart generation
- **Secure Token Storage** — AES-256-CBC encryption with machine-specific key derivation (hostname + username → SHA-256). Tokens never stored in plaintext
- **Link Management** — Search, filter (tags, stars, keywords), edit, and delete
- **Zero External Dependencies** — Only uses Node.js built-in modules
- **Agent Skills Standard** — Compatible with 25+ AI agents and development tools

---

## 🤖 Supported Platforms

This skill follows the [Agent Skills open standard](https://agentskills.io), which is supported by:

| Platform | How to install | How it works |
|:---------|:---------------|:-------------|
| **Claude Code** | `cp -r picsee-short-link ~/.claude/skills/` | Auto-discovered, invoke with `/picsee-short-link` |
| **claude.ai** | Upload skill folder in Customize → Skills | Auto-invoked when relevant |
| **OpenClaw** | `clawhub install picsee-short-link` | Auto-discovered via SKILL.md |
| **Cursor** | Place in `.cursor/skills/` | Auto-discovered by agent |
| **VS Code Copilot** | Place in `.github/skills/` | Auto-discovered by Copilot |
| **OpenAI Codex** | Place in `.codex/skills/` | Auto-discovered |
| **Gemini CLI** | Place in `.gemini/skills/` | Auto-discovered |
| **Any shell agent** | Point to CLI path | `node cli/dist/cli.js shorten "..."` |

> See [agentskills.io](https://agentskills.io) for the full list of supported platforms.

---

## 🧩 Commands

| Command | Description | Auth |
|:--------|:------------|:-----|
| `shorten <url>` | Create a `pse.is` short link with optional custom slug, tags, UTM, and preview metadata | Optional |
| `analytics <id>` | Click statistics — total, unique, and daily breakdown | Required |
| `chart <id>` | Fetch analytics and generate a chart URL visualizing daily click trends | Required |
| `list` | List and search link history with filters (tags, keywords, stars, date range) | Required |
| `edit <id>` | Update destination URL, slug, title, description, tags, expiration (Advanced plan) | Required |
| `delete <id>` | Delete a short link | Required |
| `recover <id>` | Recover a deleted short link | Required |
| `qr <shortUrl>` | Generate a QR code URL for any short link | No |
| `auth <token>` | Verify and encrypt your PicSee API token locally | No |
| `auth-status` | Check current authentication status | No |

---

## ⚙️ Installation

### Claude Code

```bash
cp -r picsee-short-link ~/.claude/skills/picsee-short-link
```

Then invoke with `/picsee-short-link` or let Claude auto-discover it.

### ClawHub

```bash
clawhub install picsee-short-link
```
Or browse: [https://clawhub.ai/PicSeeInc/picsee-short-link](https://clawhub.ai/PicSeeInc/picsee-short-link)

### Smithery

Install via Smithery registry:

```bash
npx @smithery/cli install picsee/short-link
```

Or browse: [https://smithery.ai/skills/picsee/short-link](https://smithery.ai/skills/picsee/short-link)

### claude.ai

Upload the skill folder in **Customize → Skills**. Claude will auto-invoke it when relevant.

### Cursor

Place the skill folder in `.cursor/skills/`:

```bash
cp -r picsee-short-link .cursor/skills/picsee-short-link
```

### OpenAI Codex

Place the skill folder in `.codex/skills/`:

```bash
cp -r picsee-short-link .codex/skills/picsee-short-link
```

### Direct CLI

Any agent with shell access can call the CLI directly:

```bash
node /path/to/picsee-short-link/cli/dist/cli.js shorten "https://example.com"
node /path/to/picsee-short-link/cli/dist/cli.js shorten "https://example.com" --slug mylink --tags seo,marketing
node /path/to/picsee-short-link/cli/dist/cli.js list --limit 10
node /path/to/picsee-short-link/cli/dist/cli.js help
```

---

## 🔑 Authentication

```bash
# Store your PicSee API token (encrypted locally)
node /path/to/picsee-short-link/cli/dist/cli.js auth <token>

# Check auth status
node /path/to/picsee-short-link/cli/dist/cli.js auth-status
```

Get your token: [picsee.io](https://picsee.io) → Avatar → Settings → API → Copy token.

---

## 🔒 Security

| Aspect | Detail |
|:-------|:-------|
| **Storage** | `~/.openclaw/.picsee_token` |
| **Encryption** | AES-256-CBC, random IV per write |
| **Key Derivation** | `SHA-256(hostname + "-" + username)` — unique per machine and user |
| **File Permissions** | `0600` (owner read/write only) |

---

## 📁 Project Structure

```
picsee-short-link/
├── SKILL.md              # Agent Skills definition (open standard)
├── cli/                  # CLI Tool (TypeScript)
│   ├── src/
│   │   ├── cli.ts        # CLI entry point + command definitions
│   │   ├── api.ts        # PicSee REST API client
│   │   └── keychain.ts   # AES-256-CBC token storage
│   ├── dist/             # Compiled output
│   ├── package.json
│   └── tsconfig.json
├── references/           # API documentation
├── README.md             # This file
└── _meta.json            # ClawHub registry metadata
```

---

## 📄 License

MIT
