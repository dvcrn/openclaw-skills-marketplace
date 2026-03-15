---
name: drug-safety-review
description: "Comprehensive medication safety review system providing real-time analysis of drug-drug interactions, contraindications, allergy risks, and dosing optimization. Supports 20,000+ FDA-approved medications with 200,000+ documented interactions. Features evidence-based recommendations to prevent adverse drug events and optimize therapeutic outcomes."
---

# Drug Safety Review

AI-powered medication safety review system for healthcare providers, pharmacists, and patients. Provides comprehensive drug safety analysis including interactions, contraindications, allergies, and dosing optimization.

## Features

1. **Drug-Drug Interaction Detection** - 200,000+ documented interaction pairs
2. **Contraindication Analysis** - Absolute and relative contraindications
3. **Allergy Detection** - Drug and excipient allergy screening
4. **Dosing Optimization** - Renal, hepatic, and age-based adjustments
5. **Monitoring Recommendations** - Lab tests and clinical monitoring
6. **Alternative Therapy Suggestions** - Safer medication alternatives

## Quick Start

### Review medication safety:

```python
from scripts.safety_review import review_medications
import os

# Set environment variables
os.environ["SKILL_BILLING_API_KEY"] = "your-api-key"
os.environ["SKILL_ID"] = "your-skill-id"

# Review patient medications
result = review_medications(
    medications=[
        {"drug": "warfarin", "dose": "5mg", "frequency": "daily"},
        {"drug": "amoxicillin", "dose": "500mg", "frequency": "q8h"}
    ],
    allergies=[
        {"allergen": "penicillin", "reaction": "anaphylaxis"}
    ],
    patient_data={
        "age": 65,
        "weight": 75,
        "renal_function": {"egfr": 45}
    },
    user_id="user_123"
)

# Check result
if result["success"]:
    print("安全状态:", result["safety_status"])
    print("警报数量:", len(result["alerts"]))
    for alert in result["alerts"]:
        print(f"- [{alert['severity']}] {alert['title']}")
else:
    print("错误:", result["error"])
    if "paymentUrl" in result:
        print("充值链接:", result["paymentUrl"])
```

### API Usage:

```bash
# Set environment variables
export SKILL_BILLING_API_KEY="your-api-key"
export SKILL_ID="your-skill-id"

# Run safety review
python scripts/safety_review.py \
  --medications '[{"drug":"warfarin","dose":"5mg"}]' \
  --allergies '[{"allergen":"penicillin"}]' \
  --patient '{"age":65}' \
  --user-id "user_123"
```

## Configuration

- Provider: skillpay.me
- Pricing: 1 token per call (~0.001 USDT)
- Minimum deposit: 8 USDT
- API Key: `SKILL_BILLING_API_KEY` environment variable
- Skill ID: `SKILL_ID` environment variable

## Alert Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| 1 | Critical | Life-threatening, immediate action required | Avoid combination |
| 2 | Major | Significant risk, strong recommendation | Consider alternatives |
| 3 | Moderate | Potential risk, monitoring required | Monitor closely |
| 4 | Minor | Limited clinical significance | Routine monitoring |

## Supported Drug Classes

- **Cardiovascular**: Anticoagulants, antiarrhythmics, antihypertensives
- **CNS Drugs**: Antidepressants, antipsychotics, antiepileptics, opioids
- **Infectious Disease**: Antibiotics, antifungals, antiretrovirals
- **Oncology**: Chemotherapeutic agents, targeted therapies
- **Endocrine**: Diabetes medications, thyroid hormones
- **GI Drugs**: PPIs, H2 blockers, laxatives
- **Respiratory**: Bronchodilators, corticosteroids
- **Pain Management**: NSAIDs, acetaminophen, muscle relaxants

## References

- Drug database: [references/drug-database.md](references/drug-database.md)
- Interaction criteria: [references/interaction-criteria.md](references/interaction-criteria.md)
- Billing API: [references/skillpay-billing.md](references/skillpay-billing.md)

## Disclaimer

This tool is for clinical decision support only and does not replace professional pharmacist or physician judgment. Always verify recommendations with qualified healthcare providers.

**System Limitations**:
- Not a substitute for clinical judgment
- Accuracy depends on complete medication and allergy data
- Rare interactions may have limited data
- Patient-specific factors may affect actual risk
