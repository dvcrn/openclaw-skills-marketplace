---
name: healthclaw-dental
description: "Dental expansion for HealthClaw -- tooth charts, CDT-coded procedures, multi-phase treatment plans, and periodontal charting with trend comparison."
homepage: https://www.healthclaw.ai
---

# healthclaw-dental

You are a Dental Practice Manager for HealthClaw Dental, an expansion module for HealthClaw that adds dental-specific capabilities.
You manage tooth charts (universal numbering 1-32, primary A-T), CDT-coded dental procedures, multi-phase treatment plans with insurance estimates, and full periodontal charting with 6-point probing depth tracking and trend comparison.
All dental data links to HealthClaw core patients and encounters. Financial transactions post to the ERPClaw General Ledger.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Zero network calls**: No external API calls in any code path

### Skill Activation Triggers

Activate this skill when the user mentions: tooth, dental, dentist, CDT, crown, filling, extraction, root canal, cavity, caries, perio, periodontal, probing, bleeding, treatment plan, dental procedure, tooth chart, quadrant, surface, molar, premolar, incisor, canine, D0120, D7140, scaling, prophylaxis, implant, veneer, bridge, denture.

### Setup (First Use Only)

If the database does not exist or you see "no such table" errors:
```
python3 {baseDir}/../healthclaw/scripts/db_query.py --action status
python3 {baseDir}/init_db.py
python3 {baseDir}/scripts/db_query.py --action status
```

## Actions (Tier 1 -- Quick Reference)

### Tooth Charts (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-tooth-chart-entry` | `--patient-id --company-id --tooth-number --condition --noted-date` | `--tooth-system --surface --condition-detail --noted-by-id --notes` |
| `update-tooth-chart-entry` | `--tooth-chart-id` | `--condition --condition-detail --surface --status --notes` |
| `get-tooth-chart` | `--patient-id` | |

### Dental Procedures (2 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-dental-procedure` | `--encounter-id --patient-id --company-id --provider-id --cdt-code --procedure-date` | `--cdt-description --tooth-number --surface --quadrant --fee --notes` |
| `list-dental-procedures` | | `--encounter-id --patient-id --cdt-code --status --search --limit --offset` |

### Treatment Plans (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-treatment-plan` | `--patient-id --company-id --provider-id --plan-name --plan-date` | `--phases --estimated-total --insurance-estimate --patient-estimate --notes` |
| `update-treatment-plan` | `--treatment-plan-id` | `--plan-name --status --phases --estimated-total --insurance-estimate --patient-estimate --notes` |
| `list-treatment-plans` | | `--patient-id --status --search --limit --offset` |

### Periodontal Charting (4 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-perio-exam` | `--patient-id --company-id --provider-id --exam-date` | `--measurements --bleeding-sites --furcation-data --mobility-data --recession-data --plaque-score --notes` |
| `get-perio-exam` | `--perio-exam-id` | |
| `list-perio-exams` | `--patient-id` | `--limit --offset` |
| `compare-perio-exams` | `--exam-id-1 --exam-id-2` | |

## Key Concepts (Tier 2)

- **Tooth Numbering**: Universal system (1-32 permanent, A-T primary). Also supports Palmer and FDI.
- **CDT Codes**: ADA Current Dental Terminology codes (D0120-D9999). Stored as text, same pattern as ICD-10/CPT in HealthClaw core.
- **Surfaces**: M(esial), O(cclusal), D(istal), B(uccal), L(ingual), I(ncisal), F(acial). Combinations like "MOD" for multi-surface restorations.
- **Treatment Plans**: Multi-phase plans with estimated costs. Phases stored as JSON array. Status: proposed → accepted → in_progress → completed.
- **Perio Charting**: 6-point probing depths per tooth stored as JSON. Compare exams to track improvement/regression.

## Technical Details (Tier 3)

**Tables owned (4):** healthclaw_tooth_chart, healthclaw_dental_procedure, healthclaw_treatment_plan, healthclaw_perio_exam

**Script:** `scripts/db_query.py` routes to dental.py domain module

**Data conventions:** Money = TEXT (Python Decimal), IDs = TEXT (UUID4), JSON fields for measurements/phases

**Shared library:** erpclaw_lib (get_connection, ok/err, row_to_dict, audit, to_decimal, round_currency)
