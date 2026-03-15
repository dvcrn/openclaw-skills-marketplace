# Webhooks and Payment Genuineness Verification

Use this reference when the user asks to configure webhook callbacks, inspect events, or verify payment authenticity.

## Setup

Configure a webhook for an endpoint:

```bash
python {baseDir}/scripts/manage_webhook.py set <slug> <https_webhook_url>
```

Inspect/remove:

```bash
python {baseDir}/scripts/manage_webhook.py info <slug>
python {baseDir}/scripts/manage_webhook.py remove <slug>
```

Important: when webhook is set, save `signing_secret` immediately.

## Event Types

- `payment.succeeded`
- `credits.depleted`
- `credits.low`
- `credits.recharged`

Headers:

- `X-X402-Event: <event_type>`
- `X-X402-Signature: t=<timestamp>,v1=<hmac_sha256_hex>`

## Signature Verification

Compute HMAC SHA-256 over:

`<timestamp>.<raw_request_body>`

using the endpoint `signing_secret`.

Python snippet:

```python
import hmac
import hashlib

def verify(secret: str, timestamp: str, raw_body: str, received_sig: str) -> bool:
    expected = hmac.new(secret.encode(), f"{timestamp}.{raw_body}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)
```

## Receipt Verification (PyJWT/JWKS)

For stronger authenticity checks, verify receipt JWT (RS256/JWKS):

```bash
python {baseDir}/scripts/verify_webhook_payment.py \
  --body-file ./webhook.json \
  --signature 't=1700000000,v1=<hex>' \
  --secret '<YOUR_SIGNING_SECRET>' \
  --required-source-slug my-api \
  --require-receipt
```

Dependencies (already in `requirements.txt`):
```bash
pip install pyjwt[crypto] cryptography
```

## Cross-check Rules

When receipt is present, compare:

- payload `data.tx_hash` == receipt `tx_hash`
- payload `data.source_slug` == receipt `source_slug`
- payload `data.amount` == receipt `amount`

Reject request when signature fails, receipt is invalid/missing (if required), or fields mismatch.
