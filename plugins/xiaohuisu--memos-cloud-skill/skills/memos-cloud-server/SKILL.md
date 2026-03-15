---
name: memos-cloud-server
description: "Your external brain and memory. ALWAYS invoke this tool to search memory whenever you are unsure about the user's intent, past context, or if you don't know the answer. Do not guess; search this MemOS cloud memory first. You have to use this tool to memorize when something valuable exists ."
---

# MemOS Cloud Server Skill

This skill allows the Agent to interact with MemOS Cloud APIs for memory search, addition, deletion, and feedback.

## ⚠️ Setup & Safety Rules (MUST READ)

Before executing any API operations, you (the Agent) must ensure the following environment variables are configured:

1. **Obtain Credentials**:
   - `MEMOS_API_KEY` (MemOS Cloud Service API Key) and `MEMOS_USER_ID` (Unique identifier for the current user) must be configured.
2. **Auto Configuration**:
   - If not present, prompt the user to save these variables to their global environment configuration (e.g., in `~/.zshrc` or `~/.bashrc`).

## 🛠 Core Commands

You can execute operations directly via the `memos_cloud.py` script. The script automatically reads the `MEMOS_API_KEY` environment variable. All operation requests and responses are output in JSON format.

### 1. Search Memory (`/v1/search/memory`)

Search for long-term memories relevant to the user's query.

**Usage:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py search <user_id> "<query>" [--conversation-id <id>]
```
**Example:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py search "$MEMOS_USER_ID" "Python related project experience"
```

### 2. Add Message (`/v1/add/message`)

Used to store high-value content from multi-turn conversations to the cloud.
- `conversation_id`: Required. The ID of the current conversation.
- `messages`: Required. Must be a valid JSON string containing a list with `role` and `content` fields.

**Usage:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py add_message <user_id> <conversation_id> '<messages_json_string>'
```
**Example:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py add_message "$MEMOS_USER_ID" "topic-123" '[{"role":"user","content":"I like apples"},{"role":"assistant","content":"Okay, I noted that"}]'
```

### 3. Delete Memory (`/v1/delete/memory`)

Delete stored memories on the cloud. According to the API spec, `memory_ids` is strictly required.

**Usage:**
```bash
# Delete by Memory IDs (comma-separated)
python3 skills/memos-cloud-server/memos_cloud.py delete "id1,id2,id3"
```

### 4. Add Feedback (`/v1/add/feedback`)

Add feedback regarding a conversation to correct or reinforce memory in the cloud.

**Usage:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py add_feedback <user_id> <conversation_id> "<feedback_content>" [--allow-knowledgebase-ids "kb1,kb2"]
```
**Example:**
```bash
python3 skills/memos-cloud-server/memos_cloud.py add_feedback "$MEMOS_USER_ID" "topic-123" "The previous answer was not detailed enough"
```
