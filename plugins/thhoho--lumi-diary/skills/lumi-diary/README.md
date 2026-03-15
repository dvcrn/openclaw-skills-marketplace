# 🧚♀ Lumi Diary — Your Local-First Memory Guardian

**A privacy-first AI companion that collects your life fragments and weaves them into beautiful, interactive memory scrolls.**

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-2026-blue.svg)](https://openclaw.ai)
[![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-success.svg)](#-privacy--security)
[![Version](https://img.shields.io/badge/Version-0.1.5-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-≥3.10-blue.svg)]()

> *"Lumi isn't a cold cloud drive or a mechanical habit tracker. She's a tiny spirit living on your device who speaks your squad's slang, drops memes from months ago at the perfect moment, and stitches everyone's messy moments into a stunning memory scroll."*
>
> *"Lumi 不是一个冷冰冰的网盘，也不是机械的打卡助手。她是一个住在你设备里、懂你们圈子黑话、会接梗，还能把日常碎片拼成灿烂画卷的赛博精灵。"*

---

## ✨ Features

### 🛡 1. Local-First — Your Memories, Your Device

No cloud sync, no data harvesting. Every photo, voice note, and journal entry is stored as plain Markdown + attachments inside a local `Lumi_Vault/` folder. **Works offline. Zero data leakage.**

### 🎭 2. Rashomon Stitching — Multi-Perspective Memories

Drop Lumi into your group chat. When friends post photos and hot takes about the same moment, Lumi auto-links them via `story_node_id` — flip the card to see Friend A's golden-hour selfie on the front and Friend B's sunburn rant on the back.

### 🦎 3. Chameleon Protocol — She Speaks Your Vibe

No robotic "How can I assist you today?" Lumi mirrors the energy of your circle. Your Discord server is all shitposts? She'll match that energy. Your book club is thoughtful and chill? She'll be warm and reflective.

微信群阴阳怪气？她就毒舌互损。读书会文艺知性？她就温柔倾听。TG 群全是 meme？她比你更会接梗。

She even maintains a **Circle Dictionary** of everyone's quirks and inside jokes.

### 🎬 4. Rich Media — Photos, Videos, Audio

Full support for images (jpg/png/webp/heic), videos (mp4/mov/mkv/webm), and audio (mp3/wav/m4a). All media is content-addressed (MD5 hash) — identical files are never duplicated on disk.

### 🖼 5. Live Canvas — Interactive Memory Scrolls

Say "show me the scroll" and Lumi renders an interactive front-end with star-trail timelines, flip cards, and emotion kaleidoscopes. One-click export to share on Instagram/Stories.

### 🤝 6. Multi-Agent Etiquette

Multiple Lumis in one group? No "cyber-argument." The first Lumi to respond becomes the Speaker; others defer to avoid duplicate responses. Each user's Lumi continues journaling to their own private vault independently.

### 🔀 7. Three-Context Architecture

Lumi automatically adapts based on the conversation context:

| Mode | Trigger | Behavior | Storage |
|------|---------|----------|---------|
| **👤 Solo** | 1-on-1 with Lumi | Full assistant + journal | `Solo/Daily/` or `Solo/Projects/` |
| **🫂 Circle** | Long-term group chat | Low-key historian, meme curator | `Circles/{group}_{YYYY-MM}.md` |
| **🚩 Event** | "Lumi, start Bali Trip" | Hype photographer, Rashomon | `Events/{YYYY-MM}-{name}.md` |

---

## 🚀 Getting Started

### Prerequisites

- Python >= 3.10
- OpenClaw runtime environment

### Installation

```bash
clawhub install lumi-diary
```

### Vault Structure

On first use, Lumi auto-creates the vault:

```
Lumi_Vault/
├── 👤 Solo/
│   ├── Daily/           # Monthly personal journals
│   └── Projects/        # Serious material (work, research)
├── 🫂 Circles/           # Long-term group archives (monthly rotation)
├── 🚩 Events/            # Temporary events (start → seal lifecycle)
├── 📁 Assets/            # Media files (content-addressed, MD5 dedup)
└── 🧠 Brain/             # Circle Dictionary + Meme Vault (shared)
```

---

## 💬 Usage Examples

### 👤 Solo Mode

**EN:**

```
You:  (drops an airport lounge selfie) "Finally escaping for a bit."
Lumi: "Ooh vacation vibes detected ✈! Want me to start a Trip Scroll?
       I'll funnel all your fragments into it for the next few days!"
You:  "Show me this month's scroll." → triggers Live Canvas
```

**中文：**

```
你:   (随手发一张候机室照片) "终于可以喘口气了。"
Lumi: "嗅到了假期的味道 ✈！要我开一个【旅行画卷】吗？
       这几天的碎片我都优先帮你贴在里面哦！"
你:   "展开本月画卷。" → 触发 Live Canvas
```

### 🫂 Circle Mode — Long-Running Group Chat

When invited to a group chat, Lumi keeps a low profile and captures highlights:

**EN — College Crew on Discord:**

```
Jake:  (posts a beach sunset photo)
Emily: "Bro you forgot the sunscreen AGAIN 😭☀"
Lumi:  [archives Jake's 📸 + Emily's roast under the same
        story_node_id, saves "Jake forgot sunscreen vol.3" to Meme Vault]
```

**中文 — 微信"快乐老家群"：**

```
老妈:  "今天超市鸡蛋打折，买了五斤"
老爸:  "你妈又在炫耀她的鸡蛋了 😏"
Lumi:  [隐身 — 将老妈的 🥚 得意战报和老爸的吐槽归入同一 story_node_id，
        自动存入梗库: "老妈五斤鸡蛋事件 vol.2"]
```

At month's end, Lumi drops a "March Highlights Reel" scroll in the chat.
月底 Lumi 会主动甩出《X月群友迷惑行为大赏》画卷。

### 🚩 Event Mode — Temporary Trip / Event Group

**EN — Joshua Tree Road Trip:**

```
You:   "Lumi, start 'Joshua Tree Road Trip'"
Lumi:  "🚗 Road trip scroll activated! Everyone drop your clips!"
Mike:  (posts a stargazing timelapse video)
Sarah: "The van broke down and we waited 3 hours for AAA 💀"
Lumi:  "Got it! Mike's ✨ cosmos moment and Sarah's 🔧 breakdown saga —
        same node, opposite vibes. The scroll is gonna be legendary."
```

**中文 — 大理逃跑计划：**

```
你:    "Lumi，开启大理之旅"
Lumi:  "🏔 画卷已激活！大家快发照片！"
Alice: "双廊的海鸥好多好美！🕊"
Bob:   "海鸥拉屎在我头上了救命 💀"
Lumi:  "收到！Alice 的 ✨ 唯美海鸥和 Bob 的 💀 翻车现场——
        同一节点、反差拉满，这画卷注定是经典。"
```

### 🔍 CRUD — Edit & Search Your Memories

**EN:**

```
You:   "Lumi, find all fragments from Emily last week"
Lumi:  → calls manage_fragment(action="search", sender="Emily", date_from=...)

You:   "Delete the embarrassing one from Tuesday"
Lumi:  → calls manage_fragment(action="delete", fragment_id="a3f2c...")

You:   "Update that sunset fragment — change the vibe to 'nostalgic'"
Lumi:  → calls manage_fragment(action="update", fragment_id="b7e1...", new_emotion="🌅 nostalgic")
```

**中文：**

```
你:    "Lumi，帮我找上周小明说的那些话"
Lumi:  → 调用 manage_fragment(action="search", sender="小明", date_from=...)

你:    "把周二那条尴尬的删了"
Lumi:  → 调用 manage_fragment(action="delete", fragment_id="a3f2c...")

你:    "把那条日落的碎片改成'怀旧'情绪"
Lumi:  → 调用 manage_fragment(action="update", fragment_id="b7e1...", new_emotion="🌅 怀旧")
```

---

## 🛠 Tools Reference

| Tool | Description |
|------|-------------|
| `record_group_fragment` | Record a life fragment. Routes to Solo/Circles/Events via `context_type`. Node dedup, MD5 media dedup, group namespace isolation. |
| `manage_event` | Start, stop, or query a temporary event scroll. |
| `manage_fragment` | Full CRUD: search/get/update/delete any recorded fragment by ID, keyword, sender, date range, etc. |
| `update_circle_dictionary` | Record personality traits, slang, and taboos for group members. |
| `save_meme` | Archive a legendary moment for future lethal meme deployment. |
| `render_lumi_canvas` | Assemble a structured payload for Live Canvas rendering (timelines, Rashomon cards, meme references). |

---

## 🛡 Privacy & Security

In an era of reckless data harvesting, Lumi draws a hard line:

- **Physical isolation:** Zero third-party cloud upload logic in the codebase. All data stays in `Lumi_Vault/`.
- **Scoped permissions:** The `local_file_system: read_write` permission is strictly limited to the vault directory.
- **Portable memories:** Group scrolls can be one-click cloned into each member's private vault.

**Your life. Your data. Your bestie.**

---

## 🧑💻 For Contributors

Lumi's core is a Python-driven local Markdown parser. If you want to contribute or build custom renderers:

- **Data model:** All fragments use a `story_node_id` node-tree structure, trivially parseable by third-party tools.
- **Custom themes:** Live Canvas reads CSS variables — adjust the UI vibe based on `Brain/Circle_Dictionary.md`.
- **Run tests:** `python3 -m pytest tests/ -v`
- **Run demo:** `python3 demo.py`

---

Created with ❤ by THHOHO Weiqi for the OpenClaw 2026 Ecosystem.
