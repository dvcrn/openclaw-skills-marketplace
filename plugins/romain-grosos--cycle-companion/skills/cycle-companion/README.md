# 🩸 openclaw-skill-cycle-companion

> OpenClaw skill - Partner-side menstrual cycle tracker with phase tips & fertility window

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-cycle--companion-green)](https://clawhub.com/skills/cycle-companion)

Menstrual cycle tracker designed for partners. One input (last period date) gives you the current phase, energy level, mood, practical tips, fertility window, and automatic cron notifications before each phase transition. Bilingual FR/EN. Stdlib only (no external dependencies).

## Install

```bash
clawhub install cycle-companion
```

Or manually:

```bash
git clone https://github.com/Rwx-G/openclaw-skill-cycle-companion \
  ~/.openclaw/workspace/skills/cycle-companion
```

## Setup

```bash
python3 scripts/setup.py    # interactive config wizard
```

Quick update (new cycle started):

```bash
python3 scripts/setup.py --update-date 2026-03-10
```

## What it does

From a single date input, the skill calculates the current cycle phase and provides:

| Feature | Description |
|---------|-------------|
| Phase detection | 5 phases: menstruation, follicular, ovulation, luteal, PMS |
| Tips & advice | What to do/bring, what to avoid — partner-oriented |
| Fertility window | 4 levels (low/moderate/high/peak) with exact dates |
| Cron alerts | Automatic notification 1 day before each phase transition |
| Simulation | `--date YYYY-MM-DD` to check any date without changing config |
| Bilingual | French and English |

### Phase overview (default 28-day cycle)

| Phase | Days | Energy | Fertility |
|-------|------|--------|-----------|
| Menstruation | J1-5 | Basse | Très faible |
| Folliculaire | J6-12 | Croissante | Croissante |
| Ovulation | J13-15 | Maximale | **MAXIMALE** |
| Lutéale | J16-21 | Décroissante | Faible |
| SPM | J22-28 | Très basse | Nulle |

## Configuration

Config is stored at `~/.openclaw/config/cycle-companion/config.json` and survives `clawhub update`.

```json
{
  "last_period_date": "2026-02-25",
  "cycle_length": 28,
  "luteal_length": 14,
  "menstruation_days": 5,
  "pms_days": 7,
  "language": "fr",
  "notification_time": "08:00",
  "outputs": ["telegram"],
  "telegram_chat_id": "123456789"
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `last_period_date` | — | Date of last period start (YYYY-MM-DD) |
| `cycle_length` | `28` | Total cycle length in days (18-45) |
| `luteal_length` | `14` | Luteal phase length in days (10-16) |
| `menstruation_days` | `5` | Menstruation duration in days (2-8) |
| `pms_days` | `7` | PMS duration in days (0-14, 0 to disable) |
| `language` | `fr` | Language: `fr` or `en` |
| `notification_time` | `08:00` | Cron notification time (HH:MM) |
| `outputs` | `[]` | Output channels: `telegram`, `file` |

Parameters are cross-validated: `luteal_length < cycle_length`, phase boundaries must not overlap, `pms_days` must fit within the luteal phase.

A `config.example.json` with safe defaults is included as reference.

## Storage

- Config: `~/.openclaw/config/cycle-companion/config.json`
- No database — all state derived from `last_period_date` + today's date
- No credentials required (no external APIs)

## Requirements

- Python 3.9+ (stdlib only — no pip install needed)

## Documentation

- [SKILL.md](SKILL.md) — full skill instructions, workflows, formatting guidelines
- [references/phases_fr.md](references/phases_fr.md) — detailed phase reference (French)
- [references/phases_en.md](references/phases_en.md) — detailed phase reference (English)

## License

[MIT](LICENSE)
