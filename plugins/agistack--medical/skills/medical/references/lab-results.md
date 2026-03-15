# Lab Results in Plain Language

## Processing Lab Results

### Trigger Phrases
- "Here are my lab results"
- "What does this blood test mean?"
- "Interpret my cholesterol panel"
- User forwards lab report document

### Data Structure
```json
{
  "lab_results": [
    {
      "id": "uuid",
      "test_date": "2024-03-01",
      "lab_name": "Quest Diagnostics",
      "test_type": "Comprehensive Metabolic Panel",
      "results": [
        {
          "marker": "Glucose",
          "value": 95,
          "unit": "mg/dL",
          "reference_range": "70-100",
          "status": "normal",
          "notes": "Fasting"
        }
      ],
      "abnormal_flags": [],
      "follow_up_questions": []
    }
  ]
}
```

### Script Usage
```bash
# Add lab result
python scripts/add_lab_result.py \
  --file "lab_report.pdf" \
  --date "2024-03-01" \
  --lab "Quest Diagnostics"

# Or manual entry
python scripts/add_lab_result.py \
  --test "Lipid Panel" \
  --marker "LDL" --value 145 --unit "mg/dL" \
  --range "<100" \
  --date "2024-03-01"
```

## Explanation Guidelines

### What TO Do
1. **Explain what each marker measures**
   - Simple, non-technical language
   - Why doctors order this test

2. **Compare to reference ranges**
   - State if value is normal, high, or low
   - How far from normal (if significantly outside range)

3. **Provide general context**
   - "High cholesterol can increase heart disease risk"
   - "Low vitamin D is common and often supplementable"

4. **Generate questions for doctor**
   - Specific to abnormal values
   - Focus on "what does this mean for me"

### What NEVER To Do
- ❌ Diagnose a condition based on results
- ❌ Say "you have [disease]" based on one value
- ❌ Recommend starting/stopping medications
- ❌ Interpret results as "nothing to worry about" without doctor review
- ❌ Compare to population averages without context

## Common Lab Markers Reference

### Complete Blood Count (CBC)
| Marker | Measures | Normal Range* |
|--------|----------|---------------|
| WBC | Immune system | 4.5-11.0 K/μL |
| RBC | Oxygen carrying | 4.5-5.5 M/μL |
| Hemoglobin | Oxygen capacity | 12-16 g/dL |
| Hematocrit | Blood thickness | 36-46% |
| Platelets | Clotting | 150-400 K/μL |

### Metabolic Panel
| Marker | Measures | Normal Range* |
|--------|----------|---------------|
| Glucose | Blood sugar | 70-100 mg/dL |
| BUN | Kidney function | 7-20 mg/dL |
| Creatinine | Kidney function | 0.6-1.2 mg/dL |
| eGFR | Kidney filtration | >60 mL/min |
| Sodium | Electrolyte | 135-145 mEq/L |
| Potassium | Electrolyte | 3.5-5.0 mEq/L |

### Lipid Panel
| Marker | Measures | Normal Range* |
|--------|----------|---------------|
| Total Cholesterol | Overall | <200 mg/dL |
| LDL | "Bad" cholesterol | <100 mg/dL |
| HDL | "Good" cholesterol | >40 mg/dL |
| Triglycerides | Blood fats | <150 mg/dL |

*Ranges vary by lab and individual factors. Always use reference ranges from your specific lab report.

## Example Explanation

### Input
User: "My LDL is 145, what does that mean?"

### Output
```
Lab Result: LDL Cholesterol

What it measures:
LDL (low-density lipoprotein) is often called "bad cholesterol." 
It carries cholesterol to your arteries. Higher levels are associated 
with increased risk of plaque buildup in blood vessels.

Your result: 145 mg/dL
Reference range: <100 mg/dL (optimal for most adults)

What this means:
Your LDL is above the optimal range. This falls into the "borderline 
high" category (130-159 mg/dL).

Important context:
- Cholesterol is just one factor in heart disease risk
- Your doctor considers your overall risk profile (age, family history, 
  other conditions, smoking status, etc.)
- One reading doesn't tell the whole story

Questions to ask your doctor:
1. Given my overall health, how concerned should I be about this LDL level?
2. Should we recheck this in a few months or make changes now?
3. Would lifestyle changes help, or is medication something to consider?
4. What is my HDL and total cholesterol? (The ratio matters too)

⚠️  This explanation is for information only. Discuss these results 
    with your doctor before making any decisions.
```

## Abnormal Result Protocol

When encountering significantly abnormal results:

1. **Explain the marker** in plain language
2. **Note the abnormality** without alarm
3. **Emphasize doctor consultation** - "Your doctor will interpret this in context"
4. **Generate specific questions** for the appointment
5. **Never suggest urgency level** - let doctor determine if urgent

### Red Flag Values
If user reports critically abnormal values (e.g., glucose >400, potassium >6.0, WBC <2.0 or >30.0):
- Recommend contacting doctor same day
- Do NOT suggest waiting for next appointment
- Still do not diagnose, but emphasize prompt medical contact
