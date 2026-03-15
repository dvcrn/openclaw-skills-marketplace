---
name: learning-checkin
description: "Daily learning habit builder with check-ins and smart reminders"
---

# Learning Check-in Skill

Help users build a daily learning habit through simple check-ins and intelligent reminders.

## Overview

This skill enables users to track their daily learning with:
- Simple daily check-in (just say "I'm done" or "check-in complete")
- Automatic streak tracking
- Smart reminders at appropriate times (via cron jobs)
- Optional version updates check

## Data Storage

All data is stored locally in a `data` subfolder next to the skill:

```
<skill_directory>/data/
├── rule.md       - User's customizable rules
├── records.json  - Check-in history
└── version.txt   - Current version
```

The data folder is automatically created on first use.

## Commands

The skill provides these functions that the Agent can call:

### 1. Initialize (First Time)

```bash
python <skill_path>/learning_checkin.py init
```

**When to use:** First time the user activates this skill.

**Agent action:** 
- Run the init command
- Show welcome message in user's language
- Explain the simple rules
- Ask user to start their first check-in

### 2. Check-in

```bash
python <skill_path>/learning_checkin.py checkin
```

**When to use:** When user says they're done with their learning (e.g., "I finished my study session", "check-in done", "learning complete", etc.)

**Agent action:**
- Run checkin command
- Show streak count with celebration
- Encourage user to continue tomorrow

### 3. Status

```bash
python <skill_path>/learning_checkin.py status
```

**When to use:** When user asks about their progress or streak.

**Agent action:**
- Run status command
- Tell user if they've checked in today
- Share their current streak
- Show total days checked in

### 4. Get Reminder Message

```bash
python <skill_path>/learning_checkin.py message <time>
```

Where `<time>` is one of: `09:00`, `17:00`, `20:00`

**When to use:** When sending a scheduled reminder.

**Agent action:**
- Run message command with appropriate time slot
- Send the reminder to user
- The message tone becomes more encouraging/urgent as the day progresses

### 5. Check Reminder Status

```bash
python <skill_path>/learning_checkin.py reminder <time>
```

Where `<time>` is one of: `09:00`, `17:00`, `20:00`

**When to use:** Before sending a reminder (typically called by cron job).

**Agent action:**
- Run reminder command
- If result shows "should_send": true, then send the reminder
- The command automatically logs that reminder was sent

## Default Behavior

### Check-in Rule
- User checks in once per day
- Simply tell the Agent "I'm done" or "check-in complete"
- That's it! No complex forms or steps

### Default Reminder Schedule
- **09:00 (Morning):** Friendly reminder
- **17:00 (Afternoon):** Encouraging reminder  
- **20:00 (Evening):** Urgent reminder (don't break the streak!)

### Streak System
- Consecutive days of check-ins = streak
- Miss a day = streak resets to 0

## Customization

Users can edit the `rule.md` file (in the data folder) to customize:
- Reminder times
- Reminder messages
- Their personal goals or notes

## Version Check

On each check-in, the skill can optionally check GitHub for new versions:
- Non-blocking (5 second timeout)
- If new version available, Agent tells user

## Agent Guidelines

### First Interaction (Welcome)
The Agent should:
1. Be warm and encouraging
2. Explain in simple, non-technical language:
   - "Just tell me when you've done your learning for today"
   - "I'll remind you if you forget"
   - "You'll build a streak!"
3. Ask: "Ready to start your first check-in?"

### Daily Check-in Interaction
The Agent should:
1. Celebrate the check-in
2. Mention current streak
3. Encourage for tomorrow
4. Keep it positive and simple

### Reminder Interaction
The Agent should:
1. Use the appropriate tone for the time of day
2. Morning: Cheerful and friendly
3. Afternoon: Supportive and encouraging
4. Evening: Urgent but caring

## Technical Notes

- All file paths use UTF-8 encoding
- Compatible with Windows, Linux, macOS
- Data stored in `data` subfolder next to the skill
- No external dependencies (Python standard library only)

## Version

Current version: 3.0.1

GitHub: https://github.com/daizongyu/learning-checkin