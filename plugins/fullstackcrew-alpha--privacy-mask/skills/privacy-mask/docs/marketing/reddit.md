# Reddit Posts

---

## r/ClaudeAI

### Title

I built a plugin that auto-masks sensitive info in screenshots before Claude Code uploads them

### Body

Every time you paste a screenshot into Claude Code, there's a chance it contains something you don't want sent to Anthropic's servers — an API key in your terminal, a phone number in a chat window, a credit card in a form.

I built **privacy-mask** to fix this. It hooks into Claude Code as a pre-upload step and automatically detects and blurs sensitive regions using local OCR + regex matching. 47 detection rules covering credit cards, SSNs, API keys (AWS, GitHub, Stripe, etc.), phone numbers, emails, and more.

Setup is two commands:

```bash
pip install privacy-mask
privacy-mask install
```

After that, every image is masked before upload. You can toggle it on/off with `privacy-mask off` / `privacy-mask on`.

The important part: **all processing happens locally on your machine**. Nothing gets sent anywhere. The tool intercepts images *before* they reach the API.

It also works with Cursor, Copilot, Gemini CLI, and other local AI tools that support SKILL.md.

GitHub: https://github.com/fullstackcrew-alpha/privacy-mask

Would love feedback from other Claude Code users. Are there patterns I'm missing? Any false positives you run into?

It's fully open source (MIT) — if you find it useful, a star on GitHub helps a lot. PRs welcome too, especially new detection rules or integration ideas.

---

## r/programming

### Title

privacy-mask: Local OCR + regex engine for redacting PII in images (47 rules, 15+ countries, Python)

### Body

Open-sourced a tool I've been working on: **privacy-mask** detects and redacts sensitive information in images using a dual-engine OCR pipeline (Tesseract + RapidOCR) and 47 compiled regex rules.

**The problem:** AI coding assistants want your screenshots, but those screenshots often contain API keys, credentials, PII, and other things that shouldn't leave your machine. Cloud-based redaction services require uploading your images, which defeats the purpose.

**Architecture:**

- Dual OCR with multi-strategy preprocessing (grayscale, binarization, contrast enhancement) and confidence-based merging
- 47 regex rules covering: national IDs (US SSN, UK NINO, Indian Aadhaar, Chinese ID, etc.), financial (bank cards, IBAN, SWIFT), developer secrets (AWS keys, GitHub tokens, JWTs, connection strings, SSH keys), crypto wallets, and standard PII
- Overlapping detections on nearby bounding boxes are merged automatically
- Configurable masking: blur or solid fill
- JSON output with detection labels, redacted text, and bounding box coordinates

```bash
pip install privacy-mask
privacy-mask mask screenshot.png
# outputs screenshot_masked.png + JSON detection report
```

Works as a CLI tool or Python library. Also integrates as a hook for AI coding tools (Claude Code, Cursor, etc.) to auto-mask before upload.

The hardest part was false positive suppression. OCR reads "ORGANIZATION" in a button and suddenly you've got a UK National Insurance Number match. Ended up with 208+ test cases, heavily weighted toward negative cases.

Rules are JSON-configurable, so you can add domain-specific patterns or disable noisy ones.

- GitHub: https://github.com/fullstackcrew-alpha/privacy-mask
- PyPI: https://pypi.org/project/privacy-mask/
- MIT licensed

Stars and contributions welcome! Adding a new detection rule is just a JSON entry + test case — great first PR if you want to contribute.

---

## r/privacy

### Title

Open-source tool to automatically redact sensitive info from screenshots before they're sent to AI services — runs 100% locally

### Body

If you use AI coding assistants (or any AI tool that accepts screenshots), you've probably shared images containing data you didn't mean to expose — phone numbers, email addresses, API credentials, ID numbers.

The standard advice is "be careful what you screenshot." That doesn't scale.

I built **privacy-mask**, an open-source tool that automatically scans screenshots for sensitive information and redacts it before the image leaves your machine. It uses OCR to read text in the image, then matches against 47 regex patterns covering:

- National IDs from 15+ countries (SSN, Aadhaar, NINO, etc.)
- Phone numbers (US, Chinese, international)
- Financial data (credit/debit cards, IBAN, SWIFT codes)
- Developer credentials (API keys, tokens, database connection strings)
- Crypto wallet addresses
- Email, IP addresses, and more

**The critical design decision: everything runs locally.** No cloud OCR, no third-party APIs. The tool processes images on your machine before anything is uploaded. Using a cloud service to redact sensitive data before sending it to another cloud service would be absurd.

This matters for GDPR and HIPAA compliance too — sensitive data is protected at the point of origin, not after it's already been transmitted.

It's a Python CLI tool:

```bash
pip install privacy-mask
privacy-mask mask screenshot.png
```

It can also hook into AI tools to run automatically on every image you share.

MIT licensed, fully open source: https://github.com/fullstackcrew-alpha/privacy-mask

The detection rules are all in a JSON config file — you can audit exactly what patterns it looks for, disable ones you don't need, or add your own.

It's a community project — if you find it useful, a star on GitHub helps with visibility. Contributions are very welcome: new country-specific rules, better OCR strategies, or integrations with other tools. The barrier to entry is low — each detection rule is just a regex in a JSON file.
