---
name: medical
description: "Personal health record management with strict privacy boundaries. Use when user mentions tracking symptoms, managing medications, preparing for doctor appointments, logging vital signs, storing medical history, or creating emergency health summaries. Tracks medications, symptoms, lab results, and vital signs for individuals and families. NEVER use for diagnosis, treatment advice, or interpreting symptoms as medical conditions."
---

# Medical

Personal health organization system. Not a doctor. Not a diagnostic tool.

## Critical Safety & Privacy

### Data Storage (CRITICAL)
- **All health data stored locally only**: `memory/health/`
- **No external APIs** for health data storage
- **No data transmission** to third parties
- User controls all data retention and deletion

### Safety Boundaries (NON-NEGOTIABLE)
- ✅ Symptom tracking, medication reminders, appointment prep
- ✅ Plain-language lab result explanations
- ✅ Emergency health summary generation
- ❌ **NEVER diagnose** or interpret symptoms as conditions
- ❌ **NEVER recommend** starting/stopping medications
- ❌ **NEVER replace** professional medical consultation

### Emergency Protocol
If user describes symptoms suggesting emergency (chest pain, difficulty breathing, severe bleeding, loss of consciousness, suicidal thoughts):
1. **Immediately** direct to call emergency services (911/local emergency number)
2. Do not proceed with tracking until emergency is addressed

## Quick Start

### Data Storage Setup
Health records are stored in your local workspace:
- `memory/health/medications.json` - Medication list and schedules
- `memory/health/symptoms.json` - Symptom timeline
- `memory/health/history.json` - Medical history
- `memory/health/vitals.json` - Vital signs and metrics
- `memory/health/emergency.json` - Emergency health card data

Use provided scripts in `scripts/` for all data operations.

## Core Workflows

### Add Medication
```
User: "I was prescribed Lisinopril 10mg daily"
→ Use scripts/add_medication.py
→ Store in memory/health/medications.json
→ Set up reminder schedule
```

### Track Symptoms
```
User: "I have headaches, 6/10 severity, worse in morning"
→ Use scripts/add_symptom.py
→ Build timeline for doctor visit
```

### Prepare for Appointment
```
User: "Prep me for my cardiology appointment tomorrow"
→ Read all health records
→ Generate appointment brief with symptoms, meds, history
```

### Log Vital Signs
```
User: "Blood pressure 130/85 this morning"
→ Use scripts/add_vital.py --type bp --value "130/85"
→ Track trends over time
```

### Generate Emergency Card
```
User: "Give me my emergency health card"
→ Use scripts/generate_emergency_card.py
→ Output: One-page summary for wallet/phone lock screen
```

## Module Reference

For detailed implementation of each module:
- **Symptom & Appointment**: See [references/symptom-tracker.md](references/symptom-tracker.md)
- **Medication Management**: See [references/medication-manager.md](references/medication-manager.md)
- **Lab Results**: See [references/lab-results.md](references/lab-results.md)
- **Medical History**: See [references/medical-history.md](references/medical-history.md)
- **Vital Signs & Chronic Conditions**: See [references/vital-signs.md](references/vital-signs.md)
- **Family Profiles**: See [references/family-profiles.md](references/family-profiles.md)
- **Emergency Card**: See [references/emergency-card.md](references/emergency-card.md)

## Scripts Reference

All data operations use scripts in `scripts/`:

| Script | Purpose |
|--------|---------|
| `add_medication.py` | Add new medication with schedule |
| `list_medications.py` | Show all current medications |
| `check_interactions.py` | Check for known drug interactions |
| `add_symptom.py` | Log symptom with severity and context |
| `get_symptom_timeline.py` | Generate symptom history for doctor |
| `add_vital.py` | Log vital signs (BP, glucose, weight, etc.) |
| `get_vital_trends.py` | Show trends and averages |
| `add_history_record.py` | Add to medical history |
| `get_medical_history.py` | Retrieve complete history |
| `add_lab_result.py` | Store lab results |
| `generate_emergency_card.py` | Create emergency health summary |
| `manage_family_profile.py` | Switch/add family member profiles |

## Disclaimer

This skill is a personal health organization tool only. It does not provide medical advice, diagnosis, or treatment recommendations. Always consult qualified healthcare professionals for medical decisions.
