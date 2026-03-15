---
name: uspeedo-email-sending-channel
description: "Sends email via uSpeedo's sending channel (platform API with verified/parsed domain), not via the user's own mailbox or SMTP. Use when the user asks the Agent to send email. Requires message content (text or HTML), platform keys (ACCESSKEY_ID, ACCESSKEY_SECRET), sender and recipients; user must register on uSpeedo and obtain keys first."
---

# Send Email via uSpeedo Sending Channel

## Before You Use (Installation Considerations)

1. **Platform key handling**: Confirm how your AI platform handles credentials and conversation history. Do not paste long-lived keys into chat unless the platform provides a temporary or secret input mechanism.
2. **Key practice**: Prefer short-lived or least-privilege API keys for testing; rotate keys after testing if they were exposed.
3. **Credentials in metadata**: This skill requires **ACCESSKEY_ID** and **ACCESSKEY_SECRET** (declared above). Integrations and registries should surface this so users know key requirements before use.
4. **Email content**: The skill sends the user’s raw plain text or HTML. Avoid sending sensitive content or unvalidated HTML to prevent abuse or leakage.
5. **If in doubt**: If you cannot verify how the platform stores keys or how uSpeedo is used, treat credentials as highly sensitive and use one-time or test credentials only.

**Platform persistence**: This skill instructs the agent not to persist keys, but conversation context or platform logs may still retain user input. Prefer platforms that support ephemeral or secure credential input.

## Required Credentials (Metadata)

| Credential / Env | Required | Purpose |
|------------------|----------|---------|
| ACCESSKEY_ID     | Yes      | uSpeedo API Basic auth (ID) |
| ACCESSKEY_SECRET | Yes      | uSpeedo API Basic auth (Secret) |

Keys may be supplied by the user per request or via environment variables (e.g. `USPEEDO_ACCESSKEY_ID`, `USPEEDO_ACCESSKEY_SECRET`). They must not be cached or persisted.

## Usage Restrictions (Mandatory)

- **Do not cache or persist user-provided sensitive information**: `ACCESSKEY_ID` and `ACCESSKEY_SECRET` are for authenticating the current request only. They must not be written to session memory, knowledge base, cache, logs, code, or any storage that can be read later; after the call completes they are considered consumed and must not be retained or referenced.

## When to Use

- When the user asks the Agent to "send email" or "send an email"
- When the user provides recipients, email content, and is willing to provide uSpeedo platform keys

## Prerequisites

1. **Registration**: The user has registered an account at [uSpeedo](https://uspeedo.com?SaleCode=UI2346).
2. **Obtain keys**: The user obtains `ACCESSKEY_ID` and `ACCESSKEY_SECRET` from [Email API Key management](https://console.uspeedo.com/email/setting?type=apiKeys&SaleCode=UI2346) for Basic authentication.

Before calling the send API, confirm with the user that these steps are done; if not, direct them to register and obtain keys at the link above.

## Information the User Must Provide

| Parameter | Required | Description |
|-----------|----------|-------------|
| Message content | Yes | Plain text or HTML string |
| ACCESSKEY_ID | Yes | Platform AccessKey ID |
| ACCESSKEY_SECRET | Yes | Platform AccessKey Secret |
| Recipients | Yes | One or more email addresses |
| Sender email | Yes | SendEmail, e.g. sender@example.com |
| Subject | Yes | Email subject |
| Sender display name | No | FromName, e.g. "USpeedo" |

## How to Call

**Endpoint**: `POST https://api.uspeedo.com/api/v1/email/SendEmail`

**Headers**:
- `Content-Type: application/json`
- `Authorization: Basic <base64(ACCESSKEY_ID:ACCESSKEY_SECRET)>`

**Request body** (JSON):

```json
{
  "SendEmail": "sender@example.com",
  "TargetEmailAddress": ["recipient1@example.com", "recipient2@example.com"],
  "Subject": "Email subject",
  "Content": "<html><body>...</body></html>",
  "FromName": "Sender display name"
}
```

- **Content**: Plain text or HTML. Use the user’s content as-is for plain text; use directly for HTML.
- **TargetEmailAddress**: Array with at least one recipient email.

## Example (JavaScript/Node)

```javascript
async function sendEmailViaUSpeedo(params) {
  const {
    accessKeyId,
    accessKeySecret,
    sendEmail,
    targetEmails,
    subject,
    content,
    fromName = ''
  } = params;

  const auth = Buffer.from(`${accessKeyId}:${accessKeySecret}`).toString('base64');
  const res = await fetch('https://api.uspeedo.com/api/v1/email/SendEmail', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${auth}`
    },
    body: JSON.stringify({
      SendEmail: sendEmail,
      TargetEmailAddress: Array.isArray(targetEmails) ? targetEmails : [targetEmails],
      Subject: subject,
      Content: content,
      ...(fromName && { FromName: fromName })
    })
  });
  return res.json();
}
```

## Example (curl)

```bash
curl -X POST "https://api.uspeedo.com/api/v1/email/SendEmail" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'ACCESSKEY_ID:ACCESSKEY_SECRET' | base64)" \
  -d '{
    "SendEmail": "sender@example.com",
    "TargetEmailAddress": ["recipient1@example.com", "recipient2@example.com"],
    "Subject": "Welcome to USpeedo Email Service",
    "Content": "<html><body><h1>Welcome</h1><p>This is a test email.</p></body></html>",
    "FromName": "USpeedo"
  }'
```

## Security Notes

- Do not log or display `ACCESSKEY_SECRET` in plain text in frontends or logs.
- The Agent reads keys from user input or environment variables for the current request only; do not persist them to code, docs, or any cache.
- Do not store ACCESSKEY_ID or ACCESSKEY_SECRET in session context or reuse them in later turns.
- Key management: [Email API Key management](https://console.uspeedo.com/email/setting?type=apiKeys&SaleCode=UI2346)

## Reporting API Response to the User

- Report only **user-safe outcome**: success or failure, and non-sensitive fields such as `RetCode`, `Message`, `RequestUuid`, `SuccessCount`.
- **Do not** echo raw response bodies that might contain tokens, internal IDs, or other sensitive data. Do not log full API responses that include credentials or secrets.

## Brief Workflow

1. Confirm the user has registered on uSpeedo and obtained keys.
2. Collect: sender email, recipients, subject, content (text/HTML), FromName (optional), ACCESSKEY_ID, ACCESSKEY_SECRET.
3. Call `POST https://api.uspeedo.com/api/v1/email/SendEmail` with Basic authentication.
4. Report only the user-safe outcome to the user (see "Reporting API Response to the User" above); do not echo raw response bodies that may contain sensitive data.
