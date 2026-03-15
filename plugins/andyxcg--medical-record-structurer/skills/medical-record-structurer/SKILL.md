---
name: medical-record-structurer
description: "Medical record structuring and standardization tool. Converts doctor's oral or handwritten medical records into standardized electronic medical records (EMR). Supports voice/text input, automatic field recognition, and structured output. Use when processing medical records, clinical notes, patient histories, or converting unstructured medical data into standardized formats. Includes skillpay.me payment integration for pay-per-use monetization."
---

# Medical Record Structurer

> **Version**: 1.0.4  
> **Category**: Healthcare / Medical  
> **Billing**: SkillPay (0.001 USDT per call)  
> **Free Trial**: 10 free calls per user

A professional medical record processing tool that transforms unstructured medical notes (voice or text) into standardized electronic medical records.

## Features

1. **Voice/Text Input Processing** - Accepts doctor's口述 or handwritten notes
2. **AI-Powered Field Extraction** - Automatically identifies and extracts medical fields
3. **Standardized EMR Output** - Generates structured electronic medical records
4. **Payment Integration** - skillpay.me integration for monetization (0.001 USDT per use)
5. **Free Trial** - 10 free calls for every new user

## Free Trial

Each user gets **10 free calls** before billing begins. During the trial:
- No payment required
- Full feature access
- Trial status returned in API response

```python
{
    "success": True,
    "trial_mode": True,      # Currently in free trial
    "trial_remaining": 5,    # 5 free calls left
    "balance": None,         # No balance needed in trial
    "structured_record": {...}
}
```

After 10 free calls, normal billing applies.

## Quick Start

### Process a medical record:

```python
from scripts.process_record import process_medical_record
import os

# Set API key via environment variable (only needed after trial)
os.environ["SKILLPAY_API_KEY"] = "your-api-key"

# Process with user_id for billing/trial tracking
result = process_medical_record(
    input_text="患者张三，男，45岁，主诉头痛3天...",
    user_id="user_123"
)

# Check result
if result["success"]:
    print("结构化病历:", result["structured_record"])
    if result.get("trial_mode"):
        print(f"免费试用剩余: {result['trial_remaining']} 次")
    else:
        print("剩余余额:", result["balance"])
else:
    print("错误:", result["error"])
    if "paymentUrl" in result:
        print("充值链接:", result["paymentUrl"])
```

### API Usage:

```bash
# Set API key via environment variable (only needed after trial)
export SKILLPAY_API_KEY="your-api-key"

# Run with user_id for billing/trial tracking
python scripts/process_record.py \
  --input "患者张三，男，45岁，主诉头痛3天..." \
  --user-id "user_123"
```

## Environment Variables

This skill requires the following environment variables:

### Required Variables (After Trial)

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SKILLPAY_API_KEY` | Your SkillPay API key for billing | After trial | `skp_abc123...` |
| `SKILLPAY_SKILL_ID` | Your Skill ID from SkillPay dashboard | After trial | `skill_def456...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OCR_API_KEY` | API key for OCR services (image processing) | - |
| `OCR_PROVIDER` | OCR provider (google, azure, aws, tesseract) | `google` |
| `STT_API_KEY` | API key for speech-to-text services | - |
| `STT_PROVIDER` | STT provider (google, azure, aws, whisper) | `whisper` |
| `PHI_ENCRYPTION_KEY` | Encryption key for PHI protection | - |
| `DATA_RETENTION_DAYS` | Days to retain processed records | `30` |
| `AUDIT_LOGGING_ENABLED` | Enable audit logging | `true` |

See `.env.example` for a complete list of environment variables.

## Configuration

The skill uses SkillPay billing integration:
- Provider: skillpay.me
- Price: 0.001 USDT per request
- Chain: BNB Chain
- Free Trial: 10 calls per user
- API Key: Set via `SKILLPAY_API_KEY` environment variable
- Skill ID: Set via `SKILLPAY_SKILL_ID` environment variable

## Output Format

Structured medical record includes:
- Patient demographics (name, age, gender)
- Chief complaint
- History of present illness
- Past medical history
- Physical examination
- Diagnosis
- Treatment plan
- Medications
- Follow-up instructions

### Response Format

```python
{
    "success": True,
    "trial_mode": False,        # True during free trial
    "trial_remaining": 0,       # Remaining free calls
    "balance": 95.5,            # User balance (None during trial)
    "structured_record": {
        "emr_version": "1.0",
        "record_id": "EMR_20240306120000",
        "record_date": "2024-03-06T12:00:00",
        "patient_demographics": {...},
        "clinical_information": {...},
        "assessment_and_plan": {...},
        "metadata": {...}
    }
}
```

## PHI and Privacy Handling

This skill processes Protected Health Information (PHI). The following safeguards are implemented:

### Data Protection
- **Encryption**: All data is encrypted at rest and in transit
- **Access Control**: User authentication required for all operations
- **Audit Logging**: All access to PHI is logged
- **Data Minimization**: Only necessary fields are extracted and stored

### Compliance
- **HIPAA Considerations**: Designed with HIPAA safeguards in mind
- **GDPR**: Supports data deletion requests
- **Retention**: Configurable data retention policies (default: 30 days)

### Best Practices
1. Always use environment variables for sensitive configuration
2. Enable audit logging in production
3. Implement proper access controls
4. Regular security reviews recommended

## OCR/STT Support

This skill supports external OCR and STT services:

### OCR (Optical Character Recognition)
For processing handwritten or scanned medical records:
- Google Vision API
- Azure Computer Vision
- AWS Textract
- Tesseract (open source)

### STT (Speech-to-Text)
For processing voice-recorded medical notes:
- Google Speech-to-Text
- Azure Speech Services
- AWS Transcribe
- OpenAI Whisper (open source)

Configure the respective API keys in your `.env` file to enable these features.

## References

- For detailed field specifications: see [references/emr-schema.md](references/emr-schema.md)
- For payment API details: see [references/skillpay-api.md](references/skillpay-api.md)
- For full documentation: see [README.md](README.md)
