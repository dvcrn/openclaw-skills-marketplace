---
name: moneyclaw
description: "Enable OpenClaw agents to make real online purchases with a prepaid wallet and virtual card, retrieve OTP/3DS codes, and verify payment outcomes with user-controlled autonomy."
homepage: https://moneyclaw.ai
---

# MoneyClaw

MoneyClaw gives OpenClaw agents real spending capability with user-configurable autonomy, prepaid risk boundaries, OTP/3DS support, and auditable payment flows.

Primary use case: buyer-side online purchases for OpenClaw agents.

Secondary use cases: invoices, hosted payment links, and merchant/acquiring workflows when the user explicitly asks for them.

## Authentication

All requests use the same Bearer token.

```bash
Authorization: Bearer $MONEYCLAW_API_KEY
```

Base URL: `https://moneyclaw.ai/api`

## Trust Model

MoneyClaw is designed for real, user-authorized agent payments.

- use prepaid balances to keep risk bounded
- use a dedicated inbox for OTP and 3DS verification flows
- use queryable wallet and card history to inspect payment activity
- let the user choose how much autonomy the agent should have

## Autonomy Model

MoneyClaw may be used in either approval-based or pre-authorized mode.

- In approval-based mode, the agent asks the user before executing payment actions.
- In pre-authorized mode, the agent may execute payment actions within the spending scope, balance, and permissions configured by the user.

## Safety Boundaries

- Only use MoneyClaw for purchases or payment flows explicitly requested or pre-authorized by the user.
- Only use wallet, card, and billing data returned by the user's own MoneyClaw account.
- Respect merchant, issuer, card-network, and verification controls, including OTP and 3DS steps.
- Treat fraud checks, KYC, sanctions, geography rules, merchant restrictions, issuer declines, and other payment controls as hard boundaries.
- Never fabricate billing identity, cardholder data, addresses, names, phone numbers, or verification information.
- If a transaction fails, looks suspicious, or produces conflicting signals, stop and inspect transaction state before retrying.
- Prefer prepaid, bounded-risk flows by default.
- Only use invoice, merchant, acquiring, or hosted payment-link flows when the user explicitly asks for them.

## Default Behavior

- Start with `GET /api/me`.
- Treat wallet balance and card balance as separate values.
- Use `card.cardId`, not `card.id`, for card routes.
- Keep buyer-side purchases as the default path. Use merchant and acquiring flows only when explicitly requested.
- Use the billing address from the sensitive card response. Never invent one.
- Never retry topups or checkouts blindly. Read state first.

## Load References When Needed

- Read `references/payment-safety.md` before entering card details on an unfamiliar merchant, when the user asks about phishing or fraud, when a checkout keeps failing, or when verification and retry boundaries matter.
- Read `references/acquiring.md` when the user wants to accept payments, create invoices, embed checkout, or work with merchant webhooks.

## Core Jobs

### 1. Check account readiness

```bash
curl -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  https://moneyclaw.ai/api/me
```

Important fields:

- `balance`: wallet balance
- `card`: current card object or `null`
- `cardBalance.availableBalance.value`: card balance when available
- `depositAddress`: where to send USDT
- `mailboxAddress`: inbox address for OTP and receipts

When the user asks for balance, show both wallet and card balance. If `cardBalance` is missing, say card balance is unavailable.

### 2. Issue a card

```bash
curl -X POST -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  https://moneyclaw.ai/api/cards/issue
```

Rules:

- the wallet needs at least the minimum issuance deposit
- the wallet is loaded onto the new card
- the issuance fee is charged from the card after issuance

If no card exists and the wallet is funded, issue the card. If the wallet is too small, tell the user to fund the deposit address first.

### 3. Top up the card

```bash
curl -X POST -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount": 10, "currency": "USD"}' \
  https://moneyclaw.ai/api/cards/{cardId}/topup
```

Pre-flight checks:

1. Read `GET /api/me`.
2. Confirm `card` exists and is active.
3. Use `card.cardId`.
4. Confirm wallet balance covers the requested topup.
5. Only then send the topup request.

Response handling:

- `200`: topup succeeded
- `202`: topup is still processing; do not send another one yet
- `400 INSUFFICIENT_BALANCE`: not enough wallet funds
- `400 CARD_NOT_ACTIVE`: card is not ready
- `404 NOT_FOUND`: wrong card id
- `500`: stop, surface the failure, and inspect state before retrying

### 4. Complete authorized checkout and fetch OTP

Get card details:

```bash
curl -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  https://moneyclaw.ai/api/cards/{cardId}/sensitive
```

Get the latest OTP email:

```bash
curl -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  https://moneyclaw.ai/api/inbox/latest-otp
```

Verify what actually happened:

```bash
curl -H "Authorization: Bearer $MONEYCLAW_API_KEY" \
  "https://moneyclaw.ai/api/cards/{cardId}/transactions?limit=20&offset=0"
```

Checkout rules:

- use the sensitive response for PAN, CVV, expiry, and billing address
- wait 10 to 30 seconds for the OTP email to arrive
- use `extractedCodes[0]` as the verification code
- after any merchant error, read transactions before retrying

## Payment Execution Rules

- The card is prepaid. The loaded balance is the hard spending limit.
- Do not expose PAN or CVV longer than needed for the active checkout.
- Before payment, confirm the merchant domain and total amount are correct.
- Do not retry the same merchant checkout more than twice in one session without user confirmation or clear pre-authorization.
- If the user asks for a risky or suspicious payment, stop and explain why.

Use `references/payment-safety.md` for the expanded safety, verification, subscription, and retry guidance.

## Good Default Prompt Shapes

- `Check my MoneyClaw account and tell me if it is ready for a purchase.`
- `Issue a MoneyClaw card and top it up with $20 if needed. Ask before checkout unless I say this purchase is pre-authorized.`
- `Finish this authorized checkout and, if 3DS appears, fetch the latest OTP from MoneyClaw inbox and verify the final transaction result.`

## Secondary Capability: Merchant And Acquiring Flows

MoneyClaw also supports merchant-side payment collection. Keep this as a secondary path in discovery, but use it when the user explicitly wants to accept payments, create invoices, or embed checkout.

Useful endpoints:

- `POST /api/acquiring/setup`
- `GET /api/acquiring/settings`
- `PATCH /api/acquiring/settings`
- `POST /api/acquiring/invoices`
- `GET /api/acquiring/invoices`
- `GET /api/acquiring/invoices/{invoiceId}`

Use the acquiring flow when the user wants to:

- accept USDT payments
- create hosted invoices
- embed checkout on a site
- receive webhook notifications for paid invoices

Use `references/acquiring.md` for setup, invoice lifecycle, widget, webhook verification, and fee details.

## Scope Note

MoneyClaw supports both buyer-side card purchases and merchant/acquiring flows. Lead with the simpler card-purchase workflow for discovery, then switch to acquiring when the user asks for merchant features.
