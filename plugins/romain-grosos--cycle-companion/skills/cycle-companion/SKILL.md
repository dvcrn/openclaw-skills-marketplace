---
name: cycle-companion
description: "Menstrual cycle tracker designed for partners. Calculates current phase from one input (last period date), provides factual phase info (hormones, energy, mood, fertility), practical tips on what to bring or do, and schedules automatic cron notifications before each phase transition. Use when: user asks to set up cycle tracking, query current phase, check fertility window, update partner last period date, schedule phase-change alerts, or get advice based on cycle phase. Supports FR/EN. Config: cycle_length, luteal_length, menstruation_days, pms_days, notification_time are user-configurable. Includes fertility window tracking (informational, not medical/contraceptive advice)."
---

# Cycle Companion

Partner-side menstrual cycle tracker. One input (last period date) -> phase + tips + fertility + auto cron alerts.

## Config

Stored at `~/.openclaw/config/cycle-companion/config.json`. Survives `clawhub update`.

```json
{
  "last_period_date": "YYYY-MM-DD",
  "cycle_length": 28,
  "luteal_length": 14,
  "menstruation_days": 5,
  "pms_days": 7,
  "language": "fr",
  "notification_time": "08:00",
  "outputs": ["telegram"],
  "telegram_chat_id": "optional"
}
```

Defaults: `cycle_length=28`, `luteal_length=14`, `menstruation_days=5`, `pms_days=7`, `notification_time=08:00`. All configurable.

Parameters are cross-validated: `luteal_length < cycle_length`, phase boundaries must not overlap, `pms_days` must fit within the luteal phase.

## Storage & credentials

- Config: `~/.openclaw/config/cycle-companion/config.json`
- No credentials required (no external APIs)
- Optional file output: path set in config (`file_output_path`)

## Scripts

All scripts in `skills/cycle-companion/scripts/`.

### setup.py

Interactive config wizard. Also supports:
- `setup.py --update-date YYYY-MM-DD` — update last period date (e.g. new cycle started)
- `setup.py --show` — print current config
- `setup.py --cleanup` — remove config file

Run first. Then `init.py`.

### init.py

Validates config (including cross-parameter consistency), prints current phase + fertility level, and outputs a **cron payload** JSON to schedule the next phase-transition notification. The agent reads this output and creates the cron job via the `cron` tool.

```bash
python3 scripts/init.py
```

Output includes `cron_payload` field -> pass directly to `cron(action="add", job=CRON_PAYLOAD)`.

### cycle.py

Core engine. Subcommands:

```bash
python3 scripts/cycle.py status           # Full phase info + fertility (JSON)
python3 scripts/cycle.py next-transition  # Next phase date + name (JSON)
python3 scripts/cycle.py schedule-cron    # Cron payload for next notification
python3 scripts/cycle.py delete-cron      # Deletion payloads for all cycle-companion cron jobs

# Simulation mode (dry-run):
python3 scripts/cycle.py --date 2026-04-01 status   # What phase on April 1st?
```

## Fertility tracking

The skill tracks the **fertility window** based on cycle parameters:
- Fertility window: ~5 days before ovulation + 1 day after (~6 days total)
- Levels: `low`, `moderate`, `high`, `peak`
- Included in `status` output as `fertility` (phase-level) and `fertility_window` (dates)

The `fertility_window` object contains:
```json
{
  "current_level": "high",
  "window_start": "2026-03-09",
  "peak_start": "2026-03-13",
  "peak_end": "2026-03-14",
  "window_end": "2026-03-15"
}
```

**Important**: This is informational only, based on average cycle calculations. Not a medical tool and not a reliable contraceptive method. Irregular cycles, stress, or illness can shift ovulation.

## Workflow

### Initial setup
1. Run `setup.py` (interactive or guided by agent)
2. Run `init.py` -> read `cron_payload` from output
3. Create cron job: `cron(action="add", job=CRON_PAYLOAD)`
4. Confirm to user: current phase + fertility level + next notification date

### When user queries current phase
1. Run `cycle.py status`
2. Format output for user (see Formatting section)
3. Optionally read `references/phases_fr.md` or `phases_en.md` for deeper context

### When user asks about fertility
1. Run `cycle.py status` — `fertility_window` field has all dates
2. Format with appropriate disclaimers
3. For detailed reference: load `references/phases_fr.md` (fertility section)

### When user updates last period date
1. Run `setup.py --update-date YYYY-MM-DD`
2. Run `cycle.py delete-cron` -> delete all old cron jobs
3. Run `cycle.py schedule-cron` -> create new cron job
4. Run `cycle.py status` and confirm new phase to user

### When a cron fires (systemEvent)
The cron system event text says: "[Cycle Companion] Rappel: demain commence la phase '...'."
1. Run `cycle.py status` to get full phase details
2. Format and send the phase briefing to user via Telegram (or configured output)
3. Run `cycle.py schedule-cron` -> create next cron job for the following transition

### Simulation / dry-run
Use `--date YYYY-MM-DD` to check any date without affecting config:
```bash
python3 scripts/cycle.py --date 2026-04-15 status
```

## Formatting

When presenting status to user, format like:

```
[Phase Name] Jour X du cycle

[Description physio, 1-2 phrases]

Énergie: [level]
Humeur: [mood]
Fertilité: [fertility level]

Ce qu'elle appréciera:
- [tip 1]
- [tip 2]

À éviter:
- [avoid 1]

Fenêtre de fertilité: [window_start] → [window_end] (pic: [peak_start]-[peak_end])

Prochaine phase: [name] dans X jours ([date])
```

Adapt tone to language config. Keep factual, not patronizing.

## Phase references

For detailed physiological context per phase (hormones, symptoms, advice, fertility):
- FR: `references/phases_fr.md`
- EN: `references/phases_en.md`

Load only when needed (user asks for explanation, not just status).

## Cron scheduling

Cron fires the day BEFORE a phase transition at the configured `notification_time` (default 08:00).
After each cron fires, the agent MUST schedule the next one via `cycle.py schedule-cron`.

When rescheduling (e.g. after date update), use `cycle.py delete-cron` first to clean up old jobs.

Cron uses `sessionTarget: "main"` and `payload.kind: "systemEvent"`.
The systemEvent text triggers this skill automatically on next heartbeat.

## Config updates (no setup.py)

If user says "son cycle dure 26 jours" or similar, update config directly:
1. Read current config
2. Patch the relevant field (`cycle_length`, `luteal_length`, `menstruation_days`, `pms_days`, `language`, `notification_time`)
3. Write config back
4. Re-run `cycle.py delete-cron` + `cycle.py schedule-cron` and update cron

## Security

- No external API calls — fully offline
- No credentials stored
- Config contains only cycle parameters (no PII beyond dates)
- stdlib only — no external dependencies
