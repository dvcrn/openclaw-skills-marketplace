# Agora Credentials & Authentication

Cross-product knowledge shared by all Agora products.

## Credentials

| Credential | Where to find | Used for |
|------------|--------------|---------|
| `AGORA_APP_ID` | Console → Project Overview | All API calls and SDK init |
| `AGORA_CUSTOMER_KEY` | Console → Settings → RESTful API | REST API Basic Auth username |
| `AGORA_CUSTOMER_SECRET` | Console → Settings → RESTful API | REST API Basic Auth password |
| `AGORA_APP_CERTIFICATE` | Console → Project Overview | Token generation (only if enabled) |

Console: https://console.shengwang.cn/

### Environment Variables

```bash
AGORA_APP_ID=your_app_id
AGORA_CUSTOMER_KEY=your_customer_key
AGORA_CUSTOMER_SECRET=your_customer_secret
AGORA_APP_CERTIFICATE=your_app_certificate   # only if App Certificate enabled
```

- ALWAYS read from env vars — never hardcode
- NEVER put secrets in client-side code
- NEVER commit `.env` with real values

### Service Activation

Some products require extra activation in Console beyond having credentials:

| Product | Extra requirement |
|---------|------------------|
| ConvoAI | Enable ConvoAI service (403 if not done) |
| Cloud Recording | Enable Cloud Recording service |
| RTC / RTM | No extra activation needed |

## REST API Authentication

Agora REST APIs support two authentication methods (choose one):

### Option 1: RTC Token (supported by ConvoAI and other products)

Use an RTC Token from your Agora project for authentication:

```
Authorization: agora token="007abcxxxxxxx123"
```

**curl example:**
```bash
curl -H "Authorization: agora token=\"$RTC_TOKEN\"" \
     -H "Content-Type: application/json" \
     https://api.agora.io/...
```

How to obtain a token:
- Testing: Generate a temporary token (valid for 24 hours) from [Shengwang Console](https://console.shengwang.cn/)
- Production: Deploy a [token-server](../token-server/README.md) to generate tokens

### Option 2: Basic Auth

```
Authorization: Basic base64("{AGORA_CUSTOMER_KEY}:{AGORA_CUSTOMER_SECRET}")
```

**curl example:**
```bash
AUTH=$(echo -n "$AGORA_CUSTOMER_KEY:$AGORA_CUSTOMER_SECRET" | base64)
curl -H "Authorization: Basic $AUTH" \
     -H "Content-Type: application/json" \
     https://api.agora.io/...
```

> **Note:** Not all products support Token authentication. Cloud Recording and some other products only support Basic Auth. Refer to each product module's documentation for details.

For language-specific auth patterns (Go, Java, Python, Node.js), fetch the quick start docs for each product (see URLs in product module READMEs).

## RTC / RTM Token

Token generation is separate from REST auth. See [token-server](../token-server/README.md).

## Docs

Fetch docs using the doc fetching script (see [doc-fetching.md](../doc-fetching.md)):

| Topic | Command |
|-------|---------|
| Token authentication overview | `bash skills/voice-ai-integration/scripts/fetch-doc-content.sh "docs://default/rtc/android/basic-features/token-authentication"` |

## Docs Fallback

If fetch fails: https://doc.shengwang.cn/doc/rtc/android/basic-features/token-authentication
