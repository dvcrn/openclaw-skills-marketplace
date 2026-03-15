# Family Health Profiles

## Overview

Manage separate health records for multiple family members within one skill.

## Profile Structure

```json
{
  "family_profiles": {
    "active_profile": "self",
    "profiles": {
      "self": {
        "name": "John Doe",
        "relationship": "self",
        "date_of_birth": "1985-06-15",
        "data_path": "health/"
      },
      "child_1": {
        "name": "Emma Doe",
        "relationship": "daughter",
        "date_of_birth": "2015-03-20",
        "data_path": "health/family/emma/"
      },
      "parent_1": {
        "name": "Robert Doe",
        "relationship": "father",
        "date_of_birth": "1955-11-08",
        "data_path": "health/family/robert/"
      }
    }
  }
}
```

## Profile Management

### Create New Profile
```bash
python scripts/manage_family_profile.py \
  --action create \
  --name "Emma Doe" \
  --relationship daughter \
  --dob "2015-03-20"
```

### Switch Active Profile
```bash
python scripts/manage_family_profile.py \
  --action switch \
  --profile "emma"

# Output: "Now managing health records for: Emma Doe"
```

### List Profiles
```bash
python scripts/manage_family_profile.py --action list

# Output:
# Active: Emma Doe (daughter, age 8)
# All profiles:
#   • John Doe (self) - you
#   • Emma Doe (daughter) - active
#   • Robert Doe (father)
```

### Delete Profile
```bash
python scripts/manage_family_profile.py \
  --action delete \
  --profile "emma"
```

## Use Cases

### Parents Managing Children's Health
```
"Add Emma's vaccination record"
→ System checks active profile
→ If not Emma: "Switch to Emma's profile?"
→ Store in health/family/emma/immunizations.json
```

### Adult Children Managing Elderly Parents
```
"Track my dad's medications"
→ Create/switch to father's profile
→ All medication operations apply to father's record
→ Separate from your own medications
```

### Multi-Profile Queries
```
"What medications does my family take?"
→ Aggregate across all profiles
→ Present: "You: [meds], Emma: [meds], Dad: [meds]"
```

## Data Isolation

Each profile has completely separate:
- Medication lists
- Symptom records
- Medical history
- Vital signs
- Lab results
- Appointment schedules

No data is shared between profiles unless explicitly requested.

## Quick Switch Commands

User can say:
- "Switch to my daughter's profile"
- "Manage health for Emma"
- "Switch back to my records"
- "Show all family profiles"

## Privacy Note

When managing another adult's records (elderly parent):
- Ensure you have their consent
- Consider their privacy preferences
- Emergency information should be accessible
