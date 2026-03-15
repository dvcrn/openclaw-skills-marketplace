# MemOS Cloud Skill

[English](README.md) | [中文](README_zh.md)

MemOS Cloud Server API skill. This skill allows Agents or developers to directly call the MemOS Cloud Platform API to retrieve, add, delete, and feedback on memories.

## Prerequisites

- **Python**: 3.x and above
- **Python Dependencies**: `requests` module (`pip3 install requests`)

## Install

### Option A — Command Line (Recommended)

```bash
npx skills add https://github.com/MemTensor/MemOS-Cloud-Skill
```

### Option B — Manual Install

1. Clone this repository to your local machine:
    ```bash
    git clone https://github.com/MemTensor/MemOS-Cloud-Skill.git
    ```
2. Manually copy the skill folder to your corresponding agent skills directory.

## Environment Variables

This step is critical. You must configure these variables before using the skill.

**Where to configure**

- You can configure these globally in your system environment (e.g., `~/.bashrc`, `~/.zshrc`).
- Or, you can configure them within your specific AI Agent or framework's environment settings (e.g., `.env` files for OpenClaw/Moltbot/Clawdbot).

### Required

- `MEMOS_API_KEY` (required; Token auth) — get it at [MemOS API Console](https://memos-dashboard.openmem.net/cn/apikeys/)
- `MEMOS_USER_ID` (required; A deterministic user-defined personal identifier, e.g., hashed email, employee ID) — **Do not use random or session IDs.**

```env
MEMOS_API_KEY=YOUR_TOKEN
MEMOS_USER_ID=YOUR_USER_ID
```

### Optional config

- `MEMOS_CLOUD_URL` (default: `https://memos.memtensor.cn/api/openmem/v1`)

### Quick setup (shell)

```bash
echo 'export MEMOS_API_KEY="mpg-..."' >> ~/.bashrc
echo 'export MEMOS_USER_ID="user-123"' >> ~/.bashrc
source ~/.bashrc
```

### Quick setup (Windows PowerShell)

```powershell
[System.Environment]::SetEnvironmentVariable("MEMOS_API_KEY", "mpg-...", "User")
[System.Environment]::SetEnvironmentVariable("MEMOS_USER_ID", "user-123", "User")
```

## How it Works / Usage

Once installed and configured, this skill empowers your AI Agent (e.g., Trae, Cursor, OpenClaw) to manage your long-term memories autonomously. Simply communicate with your Agent through natural language, and it will intelligently decide when to call the underlying MemOS APIs based on your conversations.

### 1. Add Message (`/v1/add/message`)

When you share preferences, facts, or instructions you want the Agent to remember, it will automatically extract the high-value content and save it to the MemOS cloud.

**Example Conversation:**
- **You:** "Please remember that my primary programming language is Python and I prefer dark mode."
- **Agent:** *(Recognizes intent -> Calls `add_message` skill)* "Got it! I've saved your preferences about Python and dark mode."

### 2. Search Memory (`/v1/search/memory`)

Before answering complex questions or when explicitly asked, the Agent will search your past memories to provide highly personalized responses.

**Example Conversation:**
- **You:** "Write a boilerplate script for my usual tech stack."
- **Agent:** *(Recognizes intent -> Calls `search` skill to retrieve your python preferences)* "Sure! Here is a set of Python boilerplate code..."

### 3. Delete Memory (`/v1/delete/memory`)

If a memory is outdated or incorrect, simply tell the Agent to forget it.

**Example Conversation:**
- **You:** "Forget my previous residential address, I've moved."
- **Agent:** *(Recognizes intent -> Calls `delete` skill)* "I have removed your old address from my memory."

### 4. Add Feedback (`/v1/add/feedback`)

You can correct the Agent's behavior, and it will reinforce its memory for future interactions.

**Example Conversation:**
- **You:** "Your last answer wasn't detailed enough. Next time, always provide code comments."
- **Agent:** *(Recognizes intent -> Calls `add_feedback` skill)* "Understood. I will add more details and code comments in the future."
