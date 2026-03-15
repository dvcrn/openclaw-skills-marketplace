# Security Policy

## Overview

The uSpeedo Email Skill allows AI agents to send email through the uSpeedo Email API.

The skill requires API credentials provided by the user and follows strict security practices to prevent misuse.

---

# Credential Handling

The following credentials are required:

- ACCESSKEY_ID
- ACCESSKEY_SECRET

Security requirements:

- Credentials must be supplied via **secure platform storage**
- Credentials must **never be logged**
- Credentials must **never be persisted**
- Credentials must **never be exposed in responses**

The skill only uses credentials **for the duration of the API request**.

---

# Data Handling

The skill processes the following user-provided data:

- sender email
- recipient email
- email subject
- email content (plain text or HTML)

The skill does **not**:

- access local files
- access system prompts
- access external APIs beyond the uSpeedo API

---

# Allowed Network Access

The skill communicates only with: https://api.uspeedo.com


No other outbound network connections are allowed.

---

# Abuse Prevention

The agent must not use this skill to:

- send phishing emails
- impersonate organizations
- distribute malware
- send illegal or abusive content

If such requests are detected, the agent should refuse the request.

---

# HTML Content Safety

HTML email content must follow these rules:

The agent must not allow:

- JavaScript
- malicious tracking scripts
- embedded credential harvesting forms
- hidden phishing links

The content should be treated as **user-supplied content** and transmitted without modification unless formatting is necessary.

---

# Responsible Use

The skill is intended for legitimate email sending use cases such as:

- transactional emails
- notification emails
- marketing emails (with proper consent)
- application notifications

---

# Reporting Security Issues

If you discover a security vulnerability related to this skill, please contact:

support@uspeedo.com
