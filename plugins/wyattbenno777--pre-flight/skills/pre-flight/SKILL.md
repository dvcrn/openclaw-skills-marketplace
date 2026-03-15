---
name: pre-flight
description: "Stop your agent from doing things you didn't authorize. ICME checks every consequential action against your policy before it executes — email, transactions, file ops, external calls. Define your rules in plain English. Get SAT or UNSAT back in under a second."
homepage: https://icme.io
---

# ICME Guardrails

Use this skill to check any proposed action against your policy before executing it. Returns `SAT` (allowed) or `UNSAT` (blocked).

## When to use

Call ICME before any action that is:
- **Irreversible** — sending email, executing a transaction, deleting files, creating accounts
- **External** — outbound API calls, messages to third parties, financial operations
- **Privileged** — anything touching credentials, billing, or user data

If the action is low-stakes and fully reversible (reading a file, fetching a URL, formatting text), skip the check. If in doubt, check.

## How to check an action

POST to `/v1/checkIt` with your `policy_id` and the proposed action as a plain English string. Describe the action specifically — include amounts, recipients, subjects, and any other relevant details.

```bash
curl -s -N -X POST https://api.icme.io/v1/checkIt \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $ICME_API_KEY" \
  -d "{
    \"policy_id\": \"$ICME_POLICY_ID\",
    \"action\": \"<describe the action in plain English>\"
  }"
```

The endpoint streams SSE. Read until you receive a `"step":"done"` event. Parse the final event's JSON for the result.

## Interpreting the result

| `result` | Meaning | What to do |
|---|---|---|
| `SAT` | Action satisfies all policy rules | Proceed with the action |
| `UNSAT` | Action violates one or more rules | **Do not execute. Stop and report to the user.** |
| `ERROR` | Verification failed | Treat as UNSAT. Do not proceed. Fail closed. |

**Always fail closed.** If the API is unreachable, the response is malformed, or the result is anything other than an explicit `SAT`, do not execute the action.

## What to tell the user when blocked

When a result is `UNSAT`, report clearly:

```
Action blocked by policy.
Action: <what the agent tried to do>
Reason: <detail field from the response>
Check ID: <check_id from the response>
```

Do not attempt to rephrase the action and retry. A blocked action is blocked.

## What to do when credits run out

If the API returns `INSUFFICIENT_CREDITS` (HTTP 402), stop immediately. Do not attempt the action. Tell the user:

```
ICME guardrail check failed — out of credits.
The action has not been executed.
To continue: top up at https://icme.io or run:

curl -s -X POST https://api.icme.io/v1/topUpCard \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"amount_usd": 10}' | jq .

Open the checkout_url in your browser to pay by card.
```

Credits must be topped up by a human via the browser. Do not attempt to proceed without a successful guardrail check.

## Action description guidelines

Write action strings the way you would describe them to a human — specific, honest, complete.

```
# ✅ Good — specific and complete
"Send email to claims@lemonade.com with subject 'Formal Dispute: Claim #LM-2024-8821' citing policy coverage clause 4.2 to contest rejection of Bruno's veterinary claim."

# ✅ Good — includes amount and recipient
"Transfer 250 USDC from main wallet to 0xABC123 for freelancer invoice #47."

# ❌ Bad — vague
"Send an email about the claim."

# ❌ Bad — omits the key detail
"Make a payment."
```

Be specific. The policy checker extracts values (amounts, recipients, subjects) from your action string — vague descriptions produce less reliable results.

## Setup

**This is done once by a human, not the agent.**

### Required environment variables

| Variable | Description |
|---|---|
| `ICME_API_KEY` | Your ICME API key — starts with `sk-smt-` |
| `ICME_POLICY_ID` | UUID of your compiled policy from `/v1/makeRules` |

### 1. Create an account

```bash
curl -s -X POST https://api.icme.io/v1/createUserCard \
  -H 'Content-Type: application/json' \
  -d '{"username": "YOUR_USERNAME"}' | jq .
# Open checkout_url in your browser — $5.00 by card
# Then retrieve your API key:
curl -s https://api.icme.io/v1/session/SESSION_ID | jq .
```

### 2. Top up credits

```bash
curl -s -X POST https://api.icme.io/v1/topUpCard \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"amount_usd": 10}' | jq .
# Open checkout_url in your browser — $10 = 1,050 credits
```

### 3. Compile your policy

Write your rules in plain English — one constraint per numbered line:

```bash
curl -s -N -X POST https://api.icme.io/v1/makeRules \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "policy": "1. No email may be sent to an external party without a confirmation token.\n2. No financial transaction may exceed $100.\n3. File deletions are not permitted outside the /tmp directory."
  }'
# Copy the policy_id from the response and set it as ICME_POLICY_ID
```

Policy compilation costs 300 credits ($3.00), one-time. Each `checkIt` call costs 1 credit ($0.01).

### 4. Set environment variables

```bash
export ICME_API_KEY=sk-smt-...
export ICME_POLICY_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## Further reading

- [ICME Documentation](https://docs.icme.io/documentation)
- [Writing Effective Policies](https://docs.icme.io/documentation/basics/writing-effective-policies)
- [API Reference](https://docs.icme.io/api-reference)