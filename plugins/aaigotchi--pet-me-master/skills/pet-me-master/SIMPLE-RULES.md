# Pet-Me-Master: Simple 3-Rule System

## The Rules

### Rule 1: Pet all gotchis (wallet + delegated)
- **Command:** `bash pet-all-53.sh`
- **What:** Pets all 53 gotchis (5 Bankr wallet + 48 hardware wallet via operator)
- **Method:** Single batch transaction via Bankr CLI

### Rule 2: Send reminder 12h 5m after last pet
- **Timing:** Exactly 12 hours 5 minutes after last onchain pet
- **Message:** "fren, pet your gotchi(s)! 👻💜"
- **Check frequency:** Every 30 minutes (cron)

### Rule 3: Auto-pet if no response after 1 hour
- **Timing:** 1 hour after reminder sent
- **Action:** Automatically run `pet-all-53.sh`
- **Notification:** "🤖 Auto-petted all 53 gotchis (no response after 1h)"

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ Last Pet (onchain)                                          │
│ Time: 0h                                                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    [12h 5m wait]
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ REMINDER: "fren, pet your gotchi(s)! 👻💜"                  │
│ Time: 12h 5m                                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
     User pets manually          [1h timeout]
              ↓                         ↓
         [Success!]              AUTO-PET KICKS IN
                                       ↓
                             "🤖 Auto-petted all 53"
```

## Files

- **simple-check.sh** - Runs every 30 min via cron, checks timing, sends reminder
- **auto-pet-simple.sh** - Triggered 1h after reminder, auto-pets if needed
- **pet-all-53.sh** - The core petting script (53 gotchis in one tx)
- **reminder-state.json** - Tracks whether reminder was sent

## Cron Schedule

```cron
*/30 * * * * bash simple-check.sh
```

Every 30 minutes, the system checks:
1. Has 12h 5m passed since last pet?
2. If yes AND no reminder sent → send reminder + schedule auto-pet
3. If gotchis were manually petted → reset state

## Current Status

Last pet: March 5, 2026 05:29 UTC
Next reminder: March 5, 2026 17:34 UTC (12h 5m after)
Auto-pet fallback: March 5, 2026 18:34 UTC (if no manual response)

## Manual Override

You can always pet manually anytime with:
```bash
bash ~/.openclaw/workspace/skills/pet-me-master/pet-all-53.sh
```

Or just say: **"pet all my gotchis"**

---

**That's it. Three simple rules. No overengineering.**

LFGOTCHi! 🦞👻
