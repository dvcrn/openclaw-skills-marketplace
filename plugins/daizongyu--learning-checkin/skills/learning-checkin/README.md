# Learning Check-in

A daily learning habit tracker skill for CoPaw/OpenClaw agents.

## Features

- **Simple Check-in**: Just tell your agent "I'm done" or "check-in complete"
- **Streak Tracking**: Build your consecutive day streak
- **Smart Reminders**: Morning, afternoon, and evening reminders (via cron)
- **Customizable**: Edit rules to fit your schedule
- **Automatic Updates**: Optional version check on each check-in

## Installation

This skill follows the OpenClaw/OpenClaw skill standard installation method.

### Installing the Skill

1. Copy this skill folder to your agent's skill storage directory
   
   The exact path depends on your agent configuration. Typically:
   - Copy the `learning-checkin` folder to wherever your agent stores skills

2. The skill will automatically initialize its data folder on first use.

### Setting Up Reminders (Optional)

If you want to receive automatic reminders, set up cron jobs using the agent's cron command:

```bash
# Morning reminder at 9:00
<command> cron create --type agent --name "Learning Check-in Morning" \
  --cron "0 9 * * *" --channel <your_channel> \
  --text "Check if user needs reminder for learning check-in"

# Afternoon reminder at 17:00
<command> cron create --type agent --name "Learning Check-in Afternoon" \
  --cron "0 17 * * *" --channel <your_channel> \
  --text "Check if user needs reminder for learning check-in"

# Evening reminder at 20:00
<command> cron create --type agent --name "Learning Check-in Evening" \
  --cron "0 20 * * *" --channel <your_channel> \
  --text "Check if user needs reminder for learning check-in"
```

Replace `<command>` with your agent's command (e.g., `copaw`, `openclaw`, or your agent's default command).
Replace `<your_channel>` with your messaging channel (console, discord, dingtalk, etc.).

## Usage

Simply tell your agent:

- **First time:** "I want to use the learning check-in skill"
- **Daily check-in:** "I'm done with my learning" or "check-in complete"
- **Check progress:** "What's my streak?" or "How am I doing?"

## Quick Start

### 1. First Time Setup

The first time you activate this skill, tell your agent:
"I want to use the learning check-in skill"

The agent will:
- Welcome you and explain the rules
- Set up your data folder automatically
- Ask you to start your first check-in

### 2. Daily Check-in

After completing your daily learning, tell your agent:
- "I'm done with my learning"
- "Check-in complete"
- "I finished studying"

Your agent will:
- Record your check-in
- Tell you your current streak
- Encourage you for tomorrow

### 3. Reminders (Optional)

If you set up cron jobs for reminders, you'll receive messages at:
- **09:00** - Friendly morning reminder
- **17:00** - Encouraging afternoon reminder  
- **20:00** - Urgent evening reminder

## Data Storage

Your check-in data is stored locally in the skill's data folder:

```
<skill_directory>/data/
├── rule.md       - Your personalized rules
├── records.json  - Check-in history
└── version.txt   - Current skill version
```

The data folder is automatically created when you first use the skill.

## Customization

Edit the `rule.md` file (in the data folder) to customize:
- Reminder times
- Reminder messages
- Your personal goals

## Technical Requirements

- Python 3.x
- No external dependencies (uses standard library only)
- Works on Windows, Linux, and macOS

## Version

Current: **3.0.1**

## GitHub

https://github.com/daizongyu/learning-checkin

## License

MIT