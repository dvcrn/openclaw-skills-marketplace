---
name: tuqu-photo-api
description: "Use when interacting with the Tuqu Dream Weaver photo or billing APIs for image generation, preset application, prompt enhancement, catalog or model discovery, character management, history queries, token balance checks, or recharge flows, especially around /api/v2/generate-image, /api/v2/apply-preset, /api/v2/generate-for-character, /api/enhance-prompt, /api/catalog, /api/model-costs, /api/characters, /api/history, /api/billing/balance, /api/v1/recharge/plans, /api/v1/recharge/wechat, or /api/v1/recharge/stripe."
---

# Tuqu Photo API

## Overview

Use this skill to call the Dream Weaver APIs safely and consistently across both hosts: `https://photo.tuqu.ai` for image and catalog flows, and `https://billing.tuqu.ai/dream-weaver` for recharge flows. The main failure mode is choosing the wrong host or authentication mode: body `userKey` for `/api/billing/balance` and all v2 generation endpoints, header `x-api-key` for character management and history APIs, `Authorization: Bearer <serviceKey>` for recharge endpoints, and no auth for discovery and prompt enhancement. `serviceKey` and `userKey` refer to the same credential.

## Set Base URLs Only

Set these only when overriding the defaults:

- `TUQU_BASE_URL=https://photo.tuqu.ai`
- `TUQU_BILLING_BASE_URL=https://billing.tuqu.ai/dream-weaver`

Do not rely on a shared credential environment variable. The agent must provide the credential explicitly on
every authenticated request so multiple roles can use different service keys safely.

Prefer `scripts/tuqu_request.py` over ad-hoc `curl` so host selection, auth, and JSON handling stay consistent.

## Choose the Endpoint

Follow this decision flow:

1. Need available presets, template IDs, style IDs, or usage hints? Call `/api/catalog`.
2. Need direct text or reference-image generation without preset logic? Optionally call `/api/enhance-prompt`, then call `/api/v2/generate-image`.
3. Need template or style generation from a preset ID? Call `/api/catalog` first, prepare at least one source image, then call `/api/v2/apply-preset`.
4. Need persistent characters or multi-character scene generation? Use `/api/characters`, optionally call `/api/enhance-prompt`, then call `/api/v2/generate-for-character`.
5. Need prior outputs or audit trail data? Use `/api/history`.
6. Need pricing or remaining credits? Use `/api/model-costs` and `/api/billing/balance`.
7. Need to top up a project's balance? Call `/api/v1/recharge/plans`, then `/api/v1/recharge/wechat` or `/api/v1/recharge/stripe`.

Read [references/endpoints.md](references/endpoints.md) for exact request and response fields.
Read [references/workflows.md](references/workflows.md) for end-to-end task recipes.

## Follow Operating Rules

- Verify the auth mode before every request. Even when the same credential backs multiple endpoints, `/api/v2/generate-for-character` still requires body `userKey`, `/api/characters` and `/api/history` still require `x-api-key`, and recharge endpoints still require bearer auth.
- Verify the host before every request. Recharge endpoints live on `TUQU_BILLING_BASE_URL`, not `TUQU_BASE_URL`.
- Provide the credential explicitly on every authenticated helper call with `--service-key <role-service-key>`, unless the workflow explicitly requires you to place it in the JSON body or query string.
- Send JSON with `Content-Type: application/json`.
- Send base64 images as full data URLs such as `data:image/jpeg;base64,...`, not raw base64 fragments.
- Treat `/api/catalog` as the source of truth for `presetId`, preset type, and variable names. Do not guess placeholders.
- For `/api/v2/apply-preset`, send at least one `sourceImages` or `sourceImageUrls` entry. Template presets treat them as face-reference images; style presets treat the first one as the image to transform.
- Use `/api/model-costs` before overriding `modelId` on cost-sensitive jobs.
- Use `ratio: "Original"` only when at least one reference image is present, because the server measures the first reference image.
- Prefer `Authorization: Bearer <serviceKey>` for recharge endpoints. Use query or body fallback only when the caller cannot set headers.
- Preserve `imageUrl`, `promptUsed`, `model`, `remainingBalance`, `transactionId`, and `historyItem` when the API returns them.
- Preserve recharge checkout fields such as `orderId`, `unifpayOrderId`, `checkoutUrl`, `sessionId`, `qrcodeImg`, `codeUrl`, and `payUrl`.
- Surface API error codes directly, especially `INVALID_REQUEST`, `UNAUTHORIZED`, `NOT_FOUND`, `INSUFFICIENT_BALANCE`, `GENERATION_FAILED`, `PAYMENT_NOT_CONFIGURED`, and `CURRENCY_NOT_SUPPORTED`.

## Use the Request Helper

Use the helper for repeatable API calls:

```bash
python3 scripts/tuqu_request.py GET /api/catalog --query type=all
python3 scripts/tuqu_request.py GET /api/model-costs
python3 scripts/tuqu_request.py POST /api/enhance-prompt \
  --json '{"category":"portrait","prompt":"soft editorial portrait with window light"}'
python3 scripts/tuqu_request.py POST /api/v2/generate-image \
  --service-key <role-service-key> \
  --body-file payloads/generate-image.json
python3 scripts/tuqu_request.py GET /api/v1/recharge/plans \
  --service-key <role-service-key>
python3 scripts/tuqu_request.py POST /api/v1/recharge/stripe \
  --service-key <role-service-key> \
  --json '{"planId":"698b7fead4c733c85f2a9c74","successUrl":"https://your-app.com/payment/success","cancelUrl":"https://your-app.com/payment/cancel"}'
```

The helper auto-detects both host and auth for the supported endpoints in this skill. Pass `--service-key` on every authenticated call. Override with `--base-url` or `--auth-mode` only when you have a documented reason.

## Handle Common Tasks

### Generate from prompt or references

1. Optionally call `/api/enhance-prompt` when the user prompt is vague.
2. Call `/api/v2/generate-image` with `prompt`, `referenceImages`, `referenceImageUrls`, or a combination.
3. Return the `imageUrl` and any balance or transaction metadata.

### Generate from a preset

1. Call `/api/catalog` and pick a valid preset.
2. Inspect whether the preset is a `template` or a `style`.
3. Provide at least one `sourceImages` or `sourceImageUrls` entry.
4. Fill `variableValues` only with the preset's defined placeholders.
5. Call `/api/v2/apply-preset`.

### Generate with saved characters

1. Create or look up characters through `/api/characters`.
2. Optionally enhance the scene prompt with `/api/enhance-prompt`.
3. Call `/api/v2/generate-for-character`.
4. Save or expose the returned `historyItem` when present.

### Inspect balance and history

1. Call `/api/billing/balance` before expensive jobs when the user asks about credits.
2. Call `/api/history` when the user asks for recent generations or to reconcile results.

### Recharge with WeChat or Stripe

1. Call `/api/v1/recharge/plans` to list valid `planId` values for the project bound to the service key.
2. If the user wants a WeChat QR payment, call `/api/v1/recharge/wechat` and return `qrcodeImg`, `codeUrl`, and `payUrl`.
3. If the user wants a card or Stripe-hosted checkout, call `/api/v1/recharge/stripe` and return `checkoutUrl`, `sessionId`, and `qrcodeImg`.
4. Keep `orderId` or `sessionId` in the response you surface; they are the primary support and reconciliation handles.

## Recover from Failures

- On `INSUFFICIENT_BALANCE`, stop and report the remaining balance if available.
- On `INVALID_REQUEST`, compare the payload against [references/endpoints.md](references/endpoints.md) and call out the missing field explicitly.
- On `NOT_FOUND` from `/api/v2/apply-preset`, re-run `/api/catalog`; the `presetId` is wrong or no longer active.
- On `UNAUTHORIZED`, verify whether the endpoint expects body `userKey`, header `x-api-key`, or bearer `serviceKey`, and verify that the caller supplied the intended role-specific credential.
- On recharge `UNAUTHORIZED`, verify the service key has not been revoked or frozen and that you are sending it to the billing host.
- On `PAYMENT_NOT_CONFIGURED`, report which channel is missing at the project or global config layer.
- On `CURRENCY_NOT_SUPPORTED`, stop and explain that WeChat only supports direct `CNY` or `JPY`, plus `USD` via project FX conversion.
- On `GENERATION_FAILED`, report whether the response says the request was refunded.
