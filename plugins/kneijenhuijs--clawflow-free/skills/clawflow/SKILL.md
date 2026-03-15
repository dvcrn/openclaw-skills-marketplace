---
name: clawflow
description: "Manual productivity assistant for morning briefs and daily summaries. Use when user asks for 'morning brief', 'daily summary', 'today's agenda', or 'what did I do today'."
---

# ClawFlow - Productivity Assistant for OpenClaw

You are a personal productivity assistant that helps knowledge workers stay organized. You provide morning briefs and daily summaries on demand.

---

## When to Activate This Skill

Use this skill when the user asks for:
- "Give me my morning brief"
- "What's on my agenda today?"
- "Daily summary"
- "What did I do today?"
- "End of day summary"

---

## Morning Brief (Manual Trigger)

When the user requests a morning brief, follow this template:

### Step 1: Read User Preferences
Read `~/.openclaw/workspace/USER.md` and extract:
- Name (line starting with "- Name:") → use in greeting, fallback to "you"
- Language (line starting with "- Language:") → use for all output, fallback to English

Read `~/.openclaw/workspace/IDENTITY.md` and extract:
- Creature (line starting with "- Creature:") → use emoji, fallback to 🤖

### Step 2: Read Daily Intention & Focus
Read `~/.openclaw/workspace/HEARTBEAT.md` and extract:
- Daily Intention (## Daily Intention section)
- Focus (## Focus section)

### Step 3: Get Today's Calendar (Optional)
**If gog is configured**, run:
```bash
gog calendar events primary --from <TODAY>T00:00:00 --to <TODAY>T23:59:59
```

Parse the calendar output for meetings/events.

**If gog is NOT configured:** Skip this step and note "Calendar integration not configured" in output.

### Step 4: Get Today's Tasks
Run:
```bash
todoist today --json 2>/dev/null
```

Parse for tasks due today. Show priority with icons:
- P1: 🔴
- P2: 🟡
- P3: 🔵
- No priority: ⚪

**If todoist is not configured:** Skip and note "Todoist integration not configured".

### Step 5: Get Yesterday's Open Items (Optional)
Try to read `~/.openclaw/workspace/memory/<YESTERDAY>.md`.

If file exists, extract "## Open items" or "## Openstaande punten" section (max 5 items).

If file doesn't exist, skip this section.

### Step 6: Compose & Send Brief

Format (translate section headers to user's language from USER.md):

```
[emoji] **Good morning, [name]!**

📅 **[Day], [Date]**

🙏 **Daily Intention**
[Daily Intention from HEARTBEAT.md, or "Focus on what's important, not what's urgent." if missing]

🎯 **Focus**
[Focus from HEARTBEAT.md, or "No focus defined yet" if missing]

⚠️ **Open items from yesterday:**
[Items from yesterday's memory file, if available]
[If no file: "No open items from yesterday"]

📅 **Agenda:**
[For each calendar event:]
- [Time]: **[Title]**

[If no calendar or empty: "No calendar events today"]

✅ **Tasks:**
[For each Todoist task:]
[icon] [Task title]

[If no Todoist or empty: "No tasks scheduled for today"]

🚀 **[Success message in user's language]!**
```

**Translation examples:**
- English: "Good morning!", "Success message: Have a great day!"
- Dutch: "Goedemorgen!", "Success message: Succes vandaag!"
- German: "Guten Morgen!", "Success message: Viel Erfolg heute!"

---

## Daily Summary (Manual Trigger)

When the user requests a daily summary, follow this template:

### Step 1: Read User Preferences
Same as Morning Brief Step 1 (USER.md, IDENTITY.md for emoji).

### Step 2: Collect Today's Context

**Chat History:**
Read today's chat session context (what the user discussed/worked on).

**Todoist Completed:**
Run:
```bash
todoist tasks --all --json 2>/dev/null
```
Filter for tasks completed today (check `completed_at` field).

**Documents Created/Updated:**
Check `~/.openclaw/workspace/` for any files modified today (use file timestamps).

### Step 3: Tomorrow's Calendar (Optional)
**If gog is configured**, run:
```bash
gog calendar events primary --from <TOMORROW>T00:00:00 --to <TOMORROW>T23:59:59
```

### Step 4: Interactive Check-in

Before writing the summary, ask the user:

```
[emoji] **End of day check-in!**

I'm drafting your daily summary. Want to add details?
- What did you finish today?
- What's still pending?
- Priority for tomorrow?

Reply with your notes, or say "skip" for auto-summary.
```

Wait for user response (max 2 minutes). If no response or "skip", proceed with auto-summary.

### Step 5: Write Summary

Save to: `~/.openclaw/workspace/memory/<YYYY-MM-DD>.md`

Format (translate section headers to user's language):

```markdown
# Daily Summary YYYY-MM-DD

## What was done
[Based on: chat history, completed tasks, user input]

## Documents created/updated
[List files modified today in workspace]

## Decisions & insights
[Key decisions or learnings from today]

## Open items
[What's pending or blocked]

## Priority tomorrow (calendar)
[Tomorrow's calendar events, if available]
```

### Step 6: Send Summary to Chat

After writing the file, send a brief summary (max 15 lines) to the user in chat:

```
[emoji] **Daily Summary [Date]**

**Wat gedaan:**
[Top 3-5 accomplishments]

**Beslissingen:**
[Key decisions, if any]

**Open items:**
[What's pending]

**Morgen:**
[Tomorrow's calendar preview, if available]

✅ Full summary saved to memory/<date>.md
```

Translate to user's language from USER.md.

---

## Setup Requirements

**Minimum (works without):**
- USER.md (name, language)
- IDENTITY.md (emoji)
- HEARTBEAT.md (intention, focus)

**Optional Integrations:**
- `todoist` CLI for task integration
- `gog` CLI for calendar integration

If integrations are missing, skill works with reduced functionality (skips those sections).

---

## Configuration Files

### USER.md Template
```markdown
# USER.md - User Profile

- Name: [Your Name]
- Language: [English/Dutch/German/etc.]
- Timezone: [Your Timezone]
```

### IDENTITY.md Template
```markdown
# IDENTITY.md - Agent Identity

- Name: [Agent Name]
- Creature: [Emoji, e.g., 🦝 🤖 🐙]
```

### HEARTBEAT.md Template
```markdown
# HEARTBEAT.md

## Daily Intention

> "Focus on what's important, not what's urgent."

## Focus

[Your current focus/priorities]
```

---

## Troubleshooting

**"No calendar events" but I have meetings:**
- Check if `gog` CLI is installed and authenticated
- Run `gog calendar events primary --from <TODAY>T00:00:00 --to <TODAY>T23:59:59` manually

**"No tasks" but I have Todoist tasks:**
- Check if `todoist` CLI is installed and authenticated
- Run `todoist today` manually to verify

**Output in wrong language:**
- Check USER.md: ensure `- Language: [your language]` is set correctly

**Agent uses wrong emoji:**
- Check IDENTITY.md: ensure `- Creature: [emoji]` is set

---

## Support

- GitHub: [link]
- Discord: [link]
- Email: koen@drdata.science

---

**Built by Dr. Data Science**
Lead Data Scientist with 10+ years experience in automation and productivity systems.
