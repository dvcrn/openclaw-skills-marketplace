---
name: ai-running-coach
description: "AI Running Coach — personalized training via IM with automatic Strava-driven plan adjustments. Use when the user asks about running training, workout plans, marathon/half-marathon/10K/5K preparation, today's workout, weekly schedule, running stats/records (fastest, longest, weekly mileage), Strava analysis, or wants to chat with an AI running coach. Triggers on: running plan, training plan, today's workout, running stats, Strava data, marathon training, running coach."
---

# AI Running Coach

OpenClaw-powered running coach that delivers personalized training via IM. The core value: **Strava data flows in automatically, and the AI adjusts your plan in real-time**.

## Setup

The `arc` CLI handles all API calls. Token stored at `~/.config/airunningcoach/config.json`.

### First-Time Onboarding

If no token is configured (`arc config show` returns "not set"):

1. Send the user this welcome message:
```
🏃 Welcome to AI Running Coach!

To connect your account:
1. Register → https://airunningcoach.net/register
2. Choose Pro (3-day free trial, cancel anytime)
3. Connect Strava → Profile page
4. Generate API Token → Profile page
5. Paste your arc_xxx token here

Already have an account? Just paste your token!
```

2. When user pastes a token: `arc config set-token <token>` then `arc config test`
3. After successful connection, suggest: "Want me to check your Strava data and create a plan?"

## Core Workflows

### 1. Daily Check-In
```bash
arc today    # Today's workout
arc week     # Full week view
```
Format the output in a friendly IM message. Add encouragement.

### 2. AI Coach Chat (THE MAIN INTERFACE)
```bash
arc coach "user's message"
```
The coach endpoint has **full context**: active plan, Strava history, body feedback, personal records. Use this for ALL conversational interactions — it handles:
- Training questions ("How should I pace today's tempo?")
- Data queries ("What's my fastest 5K?" "How many km did I run this month?")
- Plan adjustments ("I'm injured, what should I do?")
- Motivation and encouragement

### 3. Creating a Plan via IM (CONVERSATIONAL FLOW)

**Do NOT ask for all parameters at once.** Guide the user through a conversation:

**Step 1** — Ask: "What distance are you training for? (5K / 10K / Half Marathon / Marathon)"

**Step 2** — Ask: "How many weeks do you have? (4-16 weeks)"

**Step 3** — Ask: "What's your goal? (Race a specific time / General fitness / Weight loss)"
- If race: "Do you have a target finish time?" (can suggest based on Strava data)

**Step 4** — Ask: "Any days you can't run? (e.g., Monday, Sunday)"

**Step 5** — Confirm and generate:
```bash
arc plan create --race <type> --weeks <n> [--target <time>] [--goal <goal>] [--mileage <level>]
```

If user has Strava data, check their current mileage first:
```bash
arc strava summary
```
Then auto-fill `--mileage` based on their actual weekly average.

### 4. Strava Data & Records
```bash
arc strava recent     # Last 5 activities
arc strava summary    # Full stats: records, PBs, weekly avg, monthly breakdown
```
Use `strava summary` when user asks about:
- "What's my fastest pace?"
- "How far have I run this month?"
- "What's my longest run?"
- "Am I running more than last month?"

### 5. Adaptive Coaching (AUTO-ADJUSTMENT)

When user reports fatigue/injury:
```bash
arc feedback --type <fatigue|injury|soreness|illness> --severity <1-5> --message "description"
```
Then use `arc coach` to get adjusted recommendations. The coach considers all feedback.

When Strava data shows:
- Declining pace → Coach suggests recovery
- Missed workouts → Coach adjusts plan
- Faster than expected → Coach may increase intensity

### 6. Stats & Progress
```bash
arc stats    # Completion rate, streaks, totals
```

## Command Reference

| Command | Purpose |
|---------|---------|
| `arc config set-token <t>` | Save API token |
| `arc config test` | Verify connection |
| `arc today` | Today's workout |
| `arc week` | This week's plan |
| `arc stats` | Running statistics |
| `arc coach "msg"` | Chat with AI coach |
| `arc plan create --race X --weeks N` | Generate plan |
| `arc strava recent` | Recent activities |
| `arc strava summary` | Full Strava analytics |
| `arc feedback --type T --message "M"` | Report body status |

## Error Handling

- **401**: Token expired → `arc config set-token <new_token>` (regenerate at profile page)
- **403**: Subscription needed → https://airunningcoach.net/choose-plan (3-day free trial!)
- **404**: No plan → Start conversational plan creation flow

## External Endpoints

| Endpoint | Data Sent |
|----------|-----------|
| `airunningcoach.net/api/v1/*` | API token, training queries, plan parameters |

## Security & Privacy

- Token stored locally at `~/.config/airunningcoach/config.json`
- All data sent to airunningcoach.net via HTTPS
- Strava data accessed through user's own OAuth connection

## Trust Statement

This skill sends running data and queries to airunningcoach.net. Install only if you trust this service. Privacy policy: https://airunningcoach.net/privacy
