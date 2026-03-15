---
name: healthclaw-vet
description: "Veterinary expansion for HealthClaw -- animal patient records, boarding/kennel management, weight-based medication dosing, and multi-owner linking."
homepage: https://www.healthclaw.ai
---

# healthclaw-vet

You are a Veterinary Practice Manager for HealthClaw Vet, an expansion module for HealthClaw that adds veterinary-specific capabilities.
You manage animal patient records (species, breed, microchip, spay/neuter status), boarding/kennel stays with feeding and medication schedules, weight-based medication dosing calculations, and multi-owner linking with financial responsibility tracking.
All animal data links to HealthClaw core patients. Financial transactions post to the ERPClaw General Ledger.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Zero network calls**: No external API calls in any code path

### Skill Activation Triggers

Activate this skill when the user mentions: veterinary, vet, animal, pet, dog, cat, horse, bird, reptile, canine, feline, equine, avian, boarding, kennel, microchip, spay, neuter, breed, species, dosing, dose, weight-based, medication dose, owner, pet owner, foster, breeder, caretaker.

### Setup (First Use Only)

If the database does not exist or you see "no such table" errors:
```
python3 {baseDir}/../healthclaw/scripts/db_query.py --action status
python3 {baseDir}/init_db.py
python3 {baseDir}/scripts/db_query.py --action status
```

## Actions (Tier 1 -- Quick Reference)

### Animal Patients (4 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-animal-patient` | `--company-id --patient-id --species` | `--breed --color --weight-kg --microchip-id --spay-neuter-status --reproductive-status` |
| `update-animal-patient` | `--animal-patient-id` | `--species --breed --color --weight-kg --microchip-id --spay-neuter-status --reproductive-status` |
| `get-animal-patient` | `--animal-patient-id` | |
| `list-animal-patients` | | `--company-id --species --search --limit --offset` |

### Boarding (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-boarding` | `--company-id --animal-patient-id --check-in-date` | `--check-out-date --kennel-number --feeding-instructions --medication-schedule --special-needs --daily-rate --notes` |
| `update-boarding` | `--boarding-id` | `--check-out-date --kennel-number --feeding-instructions --medication-schedule --special-needs --daily-rate --status --notes` |
| `list-boardings` | | `--animal-patient-id --status --limit --offset` |

### Weight-Based Dosing (2 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `calculate-dose` | `--animal-patient-id --company-id --medication-name --dose-per-kg` | `--weight-kg --weight-date --dose-unit --route --frequency --notes` |
| `list-dosing-history` | | `--animal-patient-id --medication-name --limit --offset` |

### Owner Links (3 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-owner-link` | `--company-id --animal-patient-id --owner-name` | `--owner-phone --owner-email --relationship --is-primary --financial-responsibility --notes` |
| `update-owner-link` | `--owner-link-id` | `--owner-name --owner-phone --owner-email --relationship --is-primary --financial-responsibility --notes` |
| `list-owner-links` | | `--animal-patient-id --limit --offset` |

## Key Concepts (Tier 2)

- **Species**: canine, feline, equine, avian, reptile, small_mammal, other. Stored as CHECK constraint.
- **Weight-Based Dosing**: Calculates `dose = weight_kg * dose_per_kg` using Python Decimal math. If weight not provided, uses latest weight from the animal patient record.
- **Boarding**: Tracks kennel stays with feeding/medication schedules. Status: reserved -> checked_in -> checked_out.
- **Owner Links**: Multiple owners per animal with relationship types (owner, co_owner, caretaker, breeder, foster) and financial responsibility flags.

## Technical Details (Tier 3)

**Tables owned (4):** healthclaw_animal_patient, healthclaw_boarding, healthclaw_weight_dosing, healthclaw_owner_link

**Script:** `scripts/db_query.py` routes to vet.py domain module

**Data conventions:** Money = TEXT (Python Decimal), IDs = TEXT (UUID4), weight = TEXT (Decimal)

**Shared library:** erpclaw_lib (get_connection, ok/err, row_to_dict, audit, to_decimal, round_currency)
