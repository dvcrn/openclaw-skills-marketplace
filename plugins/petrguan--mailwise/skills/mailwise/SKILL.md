---
name: mailwise
description: "Search and analyze email issue threads from a local knowledge base. Use when the user asks about past bugs, incidents, or wants to find how experienced engineers solved similar issues. Triggers on questions like \"have we seen this before\", \"similar issues\", \"how did we fix\", \"root cause analysis\", \"past incidents\"."
homepage: https://github.com/PetrGuan/MailWise
---

# MailWise — Email Issue Knowledge Base

Search and analyze your team's email issue threads. MailWise indexes EML files, tags expert engineers' replies, and uses RAG to help you learn from how experienced engineers investigated and resolved past issues.

## When to use this skill

- User asks about **similar past issues** or bugs
- User wants to know **how an issue was resolved before**
- User pastes a **bug report** and wants analysis based on team history
- User asks about **root cause patterns** or debugging approaches
- User wants to find what **expert engineers** said about a topic

## Commands

### Search for similar issues

Find past issues matching a description. Returns ranked results with expert tags.

```bash
mailwise search "describe the issue here" --show-body
```

Options:
- `--show-body` — show a preview of each matching message
- `--expert-only` — only show replies from expert engineers
- `-k N` — number of results (default: 10)

Example:
```bash
mailwise search "email sync failure after folder migration" --show-body
mailwise search "calendar not updating on Mac" --expert-only -k 5
```

### Deep analysis with RAG

Retrieve similar past issues and ask Claude to synthesize expert insights, root cause patterns, and debugging approaches.

```bash
mailwise analyze "paste full bug report or issue description here"
```

Options:
- `-k N` — number of similar issues to feed to Claude (default: 5, increase for broader analysis)

**Tip:** For best results, paste the FULL bug report content, not just a title. More context (error codes, logs, environment details) produces better matches.

Example:
```bash
mailwise analyze "User on Mac Outlook moves emails from Inbox to local folder. Emails disappear but reappear after 30 minutes. No DeleteMessage in HxLogs."
mailwise analyze "$(cat bug_report.txt)" -k 10
```

### View a full email thread

After finding an issue via search, view the complete parsed thread with all replies and expert tags.

```bash
mailwise show <EMAIL_ID>
```

### Check index status

```bash
mailwise stats
```

Shows: total indexed emails, thread messages, expert messages, expert coverage percentage.

### Index new emails

When the user adds new EML files or wants to refresh the index:

```bash
mailwise index
```

This is incremental — only processes new or changed files. Safe to run repeatedly.

### Manage expert engineers

```bash
mailwise experts list
mailwise experts add engineer@company.com --name "Jane Doe"
mailwise experts remove engineer@company.com
```

Expert engineers' replies get `[Expert]` tags and boosted scores in search results.

## Typical workflow

1. User describes an issue or pastes a bug report
2. Run `mailwise search "..." --show-body` to find similar past issues
3. If promising results found, run `mailwise analyze "..."` for deep RAG analysis
4. Use `mailwise show <ID>` to read full threads of interest
5. Summarize findings: root cause patterns, debugging steps, and next actions

## Setup requirements

Before first use, the user needs to:

1. Install MailWise:
   ```bash
   pip install git+https://github.com/PetrGuan/MailWise.git
   ```
2. Clone the repo for config files:
   ```bash
   git clone https://github.com/PetrGuan/MailWise.git && cd MailWise
   cp config.example.yaml config.yaml
   ```
3. Edit `config.yaml`: set `eml_directory` and add expert engineers
4. Put `.eml` files in the configured directory
5. Run `mailwise index` to build the initial index

## Important notes

- All indexing and search runs locally (no data sent to external APIs)
- The `analyze` command requires Claude Code to be installed and authenticated
- The index is stored in a local SQLite database
- Markdown versions of all parsed threads are written to the `markdown/` directory
