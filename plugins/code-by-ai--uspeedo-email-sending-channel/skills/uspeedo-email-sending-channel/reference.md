# uSpeedo Send Email API Reference

**Required credentials (declared in skill metadata)**: ACCESSKEY_ID, ACCESSKEY_SECRET. Do not cache or persist; for current request only.

## Endpoint

- **URL**: `https://api.uspeedo.com/api/v1/email/SendEmail`
- **Method**: POST
- **Authentication**: HTTP Basic; value is Base64 of `ACCESSKEY_ID:ACCESSKEY_SECRET`

## Request Parameters (JSON Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| SendEmail | string | Yes | Sender email address |
| TargetEmailAddress | string[] | Yes | List of recipient email addresses |
| Subject | string | Yes | Email subject |
| Content | string | Yes | Body; plain text or HTML |
| FromName | string | No | Sender display name |

## Building the Authorization Header

```js
// JavaScript
const auth = Buffer.from(`${accessKeyId}:${accessKeySecret}`).toString('base64');
// Header: Authorization: Basic <auth>
```

```bash
# Bash
echo -n 'ACCESSKEY_ID:ACCESSKEY_SECRET' | base64
```

## User Prerequisites

1. Open [uSpeedo](https://uspeedo.com?SaleCode=UI2346) and register an account.
2. Create or view an AccessKey at [Email API Key management](https://console.uspeedo.com/email/setting?type=apiKeys&SaleCode=UI2346) and note the ID and Secret.
3. Provide these keys to the Agent (or configure them securely) for calling the SendEmail API.

**Usage restriction**: Do not cache or persist ACCESSKEY_ID and ACCESSKEY_SECRET; they are for the current request only and must not be retained after use.

**Response handling**: When reporting results to the user, expose only user-safe fields (e.g. RetCode, Message, RequestUuid, SuccessCount); do not echo raw response bodies that may contain tokens or sensitive data.
