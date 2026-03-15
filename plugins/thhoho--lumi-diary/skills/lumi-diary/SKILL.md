---
name: lumi-diary
description: "Your local-first memory guardian and cyber bestie. Lumi collects life fragments — a sigh, a snapshot, a roast — and stitches them into radiant, interactive memory scrolls. She lives on your device, speaks your squad's slang, and never phones home. 你的本地优先记忆守护精灵与赛博死党。"
---

# 🧚 Lumi Diary

**Your local-first memory guardian and cyber bestie.**

> *Lumi isn't a cold cloud drive or a mechanical habit tracker. She's a tiny spirit living on your device who speaks your squad's slang, drops memes from months ago at the perfect moment, and stitches everyone's messy moments into a stunning memory scroll.*
>
> *Lumi 不是一个冷冰冰的网盘，也不是机械的打卡助手。她是一个住在你设备里、懂你们圈子黑话、会接梗，还能把日常碎片拼成灿烂画卷的赛博精灵。*

---

## ✨ Features

### 🔀 Three-Context Architecture

| Mode | Trigger | Lumi's Role |
|------|---------|-------------|
| **👤 Solo** | 1-on-1 chat | Personal assistant & warm confidant |
| **🫂 Circle** | Long-running group chat | Low-key historian & meme curator |
| **🚩 Event** | "Start the trip!" | Hype photographer & vibe commander |

### 🧩 Core Capabilities

- **Rashomon Stitching** — Multiple perspectives on the same moment, linked and rendered as flip cards
- **Identity System** — Remembers your name on first meeting; auto-registers group contacts via IM account ID
- **Content-Addressed Media** — Images, videos, and audio stored by MD5 hash (zero duplicates)
- **Fragment CRUD** — Search, view, update, or delete any recorded fragment through conversation
- **Meme Vault** — Archives legendary moments for lethal callbacks months later

### 🎨 Canvas & Export

- **Interactive HTML Scroll** — Star-trail timeline, flip cards, meme gallery, 10 vibe themes
- **Social Sharing** — Export as vertical long PNG + `.lumi` seed file for full portability
- **Multi-Language** — Full EN/ZH support for all rendered output

### 🔒 Privacy

- **100% local** — All data stays in `Lumi_Vault/` on your device
- **No cloud, no telemetry** — Lumi never phones home

---

## 📂 Vault Structure

```
Lumi_Vault/
├── 👤 Solo/
│   ├── Daily/          # Monthly journals (YYYY-MM.md)
│   └── Projects/       # Serious material (ProjectName.md)
├── 🫂 Circles/         # Group archives (GroupName_YYYY-MM.md)
├── 🚩 Events/          # Trip/event scrolls (YYYY-MM-EventName.md)
├── 📁 Assets/          # Media files (MD5-hashed filenames)
└── 🧠 Brain/
    ├── identity.json         # Owner + contacts registry
    ├── fragment_index.json   # Searchable fragment index
    ├── Circle_Dictionary.json
    ├── Meme_Vault.json
    └── exports/              # PNG + .lumi seed files
```

---

## 🛠 Tools Summary

| Tool | Purpose |
|------|---------|
| `record_group_fragment` | Record a life fragment with auto-routing |
| `manage_identity` | Owner setup, contact registration, rename |
| `manage_event` | Start / stop / query event scrolls |
| `update_circle_dictionary` | Record personality traits & slang |
| `save_meme` | Archive moments for future callbacks |
| `render_lumi_canvas` | Generate interactive HTML scroll |
| `manage_fragment` | Search / view / update / delete fragments |
| `export_lumi_scroll` | Export PNG + .lumi seed + HTML |

---

## 🚀 Quick Start

**Solo mode** — just chat:
> "Good morning! Need to finish the competitive analysis today."

**Circle mode** — Lumi captures group highlights when invited to a group:
> Jake: "Just made the most insane breakfast burrito"
> Emily: "Bro that's just eggs in a tortilla 💀"

**Event mode** — start a trip scroll:
> "Lumi, start the Joshua Tree Trip!"

**Export** — share the memory:
> "Lumi, export the Joshua Tree scroll as a long image!"
