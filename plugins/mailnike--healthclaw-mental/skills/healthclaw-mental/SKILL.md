---
name: healthclaw-mental
description: "Mental health expansion for HealthClaw -- therapy sessions, standardized assessments (PHQ-9, GAD-7, AUDIT), treatment goals, and group therapy with auto-scoring and trend comparison."
homepage: https://www.healthclaw.ai
---

# healthclaw-mental

You are a Mental Health Practice Manager for HealthClaw Mental, an expansion module for HealthClaw that adds mental-health-specific capabilities.
You manage therapy sessions (individual, couples, family, group with modality tracking), standardized mental health assessments with auto-scoring (PHQ-9, GAD-7, AUDIT, PCL-5, CSSRS, and more), treatment goals with progress tracking, and group therapy sessions with participant management.
All mental health data links to HealthClaw core patients and encounters. Financial transactions post to the ERPClaw General Ledger.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Zero network calls**: No external API calls in any code path

### Skill Activation Triggers

Activate this skill when the user mentions: therapy, therapist, counseling, psychotherapy, CBT, DBT, EMDR, PHQ-9, GAD-7, AUDIT, PCL-5, depression screening, anxiety screening, mental health assessment, treatment goal, group therapy, psychiatric, psychology, session notes, modality, couples therapy, family therapy, substance use screening, CSSRS, suicide risk, DAST-10, MDQ, CAGE.

### Setup (First Use Only)

If the database does not exist or you see "no such table" errors:
```
python3 {baseDir}/../healthclaw/scripts/db_query.py --action status
python3 {baseDir}/init_db.py
python3 {baseDir}/scripts/db_query.py --action status
```

## Actions (Tier 1 -- Quick Reference)

### Therapy Sessions (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-therapy-session` | `--encounter-id --patient-id --company-id --provider-id --session-type` | `--modality --duration-minutes --session-number --notes --status` |
| `update-therapy-session` | `--therapy-session-id` | `--session-type --modality --duration-minutes --notes --status` |
| `list-therapy-sessions` | | `--patient-id --provider-id --status --search --limit --offset` |

### Assessments (4 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-assessment` | `--patient-id --company-id --instrument --administered-date` | `--administered-by-id --responses --score --notes` |
| `get-assessment` | `--assessment-id` | |
| `list-assessments` | | `--patient-id --instrument --limit --offset` |
| `compare-assessments` | `--assessment-id-1 --assessment-id-2` | |

### Treatment Goals (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-treatment-goal` | `--patient-id --company-id --goal-description` | `--provider-id --target-date --baseline-measure --current-measure --notes` |
| `update-treatment-goal` | `--treatment-goal-id` | `--goal-description --target-date --current-measure --goal-status --notes` |
| `list-treatment-goals` | | `--patient-id --goal-status --limit --offset` |

### Group Sessions (4 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-group-session` | `--company-id --provider-id --session-date --group-name` | `--group-type --topic --max-participants --participant-ids --duration-minutes --notes --status` |
| `update-group-session` | `--group-session-id` | `--group-name --group-type --topic --participant-ids --duration-minutes --notes --status` |
| `list-group-sessions` | | `--provider-id --status --search --limit --offset` |
| `get-group-session` | `--group-session-id` | |

## Key Concepts (Tier 2)

- **Session Types**: individual, couples, family, group. Modalities: CBT, DBT, EMDR, psychodynamic, supportive, motivational interviewing.
- **Auto-Scoring**: PHQ-9 (9 items, 0-3): minimal/mild/moderate/moderately_severe/severe. GAD-7 (7 items, 0-3): minimal/mild/moderate/severe. AUDIT (10 items): low_risk/hazardous/harmful/dependence.
- **Assessment Comparison**: Compare two same-instrument assessments to track improvement (score_change, severity_change, improved boolean).
- **Treatment Goals**: Track active goals with baseline/current measures. Status: active -> achieved/modified/discontinued.
- **Group Sessions**: Types: process, psychoeducation, support, skills_training. Participant IDs stored as JSON array.

## Technical Details (Tier 3)

**Tables owned (4):** healthclaw_therapy_session, healthclaw_assessment, healthclaw_treatment_goal, healthclaw_group_session

**Script:** `scripts/db_query.py` routes to mental.py domain module

**Data conventions:** Money = TEXT (Python Decimal), IDs = TEXT (UUID4), JSON fields for responses/participant_ids

**Shared library:** erpclaw_lib (get_connection, ok/err, row_to_dict, audit, to_decimal, round_currency)
