# Pet-Me-Master: How It Actually Works

## The Smart Way (Not Polling!)

Instead of checking every 30 minutes (wasteful), we schedule EXACTLY when we need to check.

## Flow

```
┌─────────────────────────────────────────┐
│ YOU (or auto-pet): "pet all my gotchis" │
│ → Runs pet-all-53.sh                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ After pet succeeds:                      │
│ → Calls after-pet-hook.sh               │
│ → Resets reminder state                 │
│ → Schedules next check                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ schedule-next-check.sh:                  │
│ 1. Reads last pet time from blockchain  │
│ 2. Calculates: last_pet + 12h 5m        │
│ 3. Schedules send-reminder.sh at that   │
│    exact time (via background sleep)    │
└─────────────────────────────────────────┘
              ↓
         [12h 5m wait]
              ↓
┌─────────────────────────────────────────┐
│ send-reminder.sh fires:                  │
│ → Sends "fren, pet your gotchi(s)!"     │
│ → Schedules auto-pet-simple.sh in 1h   │
└─────────────────────────────────────────┘
              ↓
          [1h wait]
              ↓
     ┌──────────┴──────────┐
     ↓                      ↓
  You petted          auto-pet-simple.sh
  manually            checks blockchain
     ↓                      ↓
  Success!          Still need petting?
                           ↓
                   ┌───────┴────────┐
                   ↓                ↓
                  YES              NO
                   ↓                ↓
           Runs pet-all-53.sh    Already done!
                   ↓                ↓
            Auto-pet success!   Good job!
```

## Key Files

### Core Scripts
- **pet-all-53.sh** - Pets all 53 gotchis via Bankr CLI
- **after-pet-hook.sh** - Runs after successful pet, schedules next reminder
- **schedule-next-check.sh** - Calculates and schedules reminder at 12h 5m
- **send-reminder.sh** - Sends reminder, schedules auto-pet fallback
- **auto-pet-simple.sh** - Auto-pets if user didn't respond after 1h

### State
- **reminder-state.json** - Tracks reminder/fallback status

## No Polling!

We don't check every X minutes. We schedule jobs at EXACT times:
- **Reminder time** = last_pet_timestamp + 43500 seconds (12h 5m)
- **Auto-pet time** = reminder_time + 3600 seconds (1h)

## Safety Net

One cron job runs daily at 6am UTC to catch any failed background jobs:
```cron
0 6 * * * schedule-next-check.sh
```

This ensures that if the background process dies, it gets rescheduled within 24h max.

## Current Status

Run this to see timing:
```bash
bash ~/.openclaw/workspace/skills/pet-me-master/scripts/schedule-next-check.sh
```

## The 3 Rules

1. **Pet all gotchis** - wallet + delegated (53 total)
2. **Reminder at 12h 5m** - after last onchain pet
3. **Auto-pet after 1h** - if no response to reminder

Simple. Efficient. Exact timing. No wasteful polling.

LFGOTCHi! 🦞👻
