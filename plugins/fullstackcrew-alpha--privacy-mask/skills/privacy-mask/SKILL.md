---
name: privacy-mask
description: "Mask and redact sensitive information (PII) in screenshots and images before analysis — phone numbers, emails, IDs, API keys, crypto wallets, credit cards, passwords, and more. Uses OCR (Tesseract / EasyOCR) to detect private data and applies redaction overlays. All processing is 100% local and offline — no data leaves your machine. Use when receiving screenshots that may contain private data, or when the user mentions privacy / masking / redacting / PII removal / sensitive data protection."
---

# Privacy Mask

Detect and mask sensitive information in images locally before they leave your machine.

## When to use

- User sends a screenshot that may contain private data
- User mentions privacy, masking, or redacting
- You need to analyze an image but want to redact sensitive info first

## Quick start

```bash
pip install privacy-mask
privacy-mask install   # one-time: sets up global Claude Code hook
```

After install, all images are automatically masked before upload. No further action needed.

## Manual usage

Mask an image:
```bash
privacy-mask mask <image_path>
privacy-mask mask <image_path> --in-place
privacy-mask mask <image_path> --dry-run   # detect only
```

Output is JSON:
```json
{
  "status": "success",
  "detections": [{"label": "PHONE_CN", "text": "***", "bbox": [10, 20, 100, 30]}],
  "summary": "Masked 1 regions: 1 PHONE_CN"
}
```

## What it detects (47 rules)

- **IDs**: Chinese ID card, passport, HK/TW ID, US SSN, UK NINO, Canadian SIN, Indian Aadhaar/PAN, Korean RRN, Singapore NRIC, Malaysian IC
- **Phone**: Chinese mobile/landline, US phone, international (+prefix)
- **Financial**: Bank card, Amex, IBAN, SWIFT/BIC
- **Developer keys**: AWS, GitHub, Slack, Google, Stripe tokens, JWT, connection strings, API keys, SSH/PEM keys
- **Crypto**: Bitcoin, Ethereum wallet addresses
- **Other**: Email, birthday, IP/IPv6, MAC, UUID, license plate, MRZ, URL auth tokens

## Important

- All processing is **local and offline** — no data leaves the machine
- The hook intercepts images **before** upload to cloud API
- Configure rules in the bundled `config.json` or pass `--config` for custom rules
