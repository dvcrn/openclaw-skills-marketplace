# Learning Checkin Skill - Design Document

## 1. Overview

This skill helps users build a daily learning habit through check-ins and reminders.

## 2. File Structure

```
D:\workspace\learning-checkin\
├── rule.md           # User configurable rules
├── records.json      # Check-in history
├── version.txt       # Current version
└── reminder_log.json # Reminder history (optional)
```

## 3. Core Features

### 3.1 First Time Setup (init)
- Welcome message in user's native language
- Initialize data directory
- Guide user to start first check-in

### 3.2 Daily Check-in (checkin)
- User says "check-in done" or similar phrase
- Record timestamp
- Show streak count
- Positive encouragement

### 3.3 Reminders
- Default times: 9:00 AM, 5:00 PM, 8:00 PM
- Tone increases in urgency throughout the day
- Skip if already checked in today

### 3.4 Version Check
- Check GitHub for new version on each check-in
- Non-blocking (timeout 5s)
- Show update message if new version available

## 4. Data Format

### rule.md
```markdown
# Learning Check-in Rules

## Check-in Times
- 09:00 - Morning reminder
- 17:00 - Afternoon reminder
- 20:00 - Evening reminder

## Messages
[Customizable per time slot]
```

### records.json
```json
{
  "checkins": [
    {"date": "2024-01-15", "timestamp": "2024-01-15T09:30:00"},
    {"date": "2024-01-16", "timestamp": "2024-01-16T20:15:00"}
  ]
}
```

## 5. Agent Interaction Guide

### For First Time Users
Agent should:
1. Show welcome message
2. Explain rules in simple language
3. Ask user to start first check-in

### For Daily Check-in
When user says they completed their learning:
1. Call checkin function
2. Show streak count
3. Encourage for tomorrow

### For Reminders
When cron triggers reminder:
1. Check if user already checked in today
2. If not, send reminder with appropriate tone
3. Log reminder sent

## 6. Version History

- v1.0.0 - Initial release