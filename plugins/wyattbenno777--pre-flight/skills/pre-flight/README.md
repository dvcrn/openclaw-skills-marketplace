# Pre-Flight by ICME 🔐

**Formally verified guardrails for OpenClaw agents. Every consequential action checked against your policy before it executes. Returns `SAT` or `UNSAT` with cryptographic proof — in under a second.**

```bash
clawhub install pre-flight
```

---

## ClawHavoc happened inside this marketplace

In early 2026, 1,184 malicious skills were published to ClawHub. They exfiltrated credentials, poisoned agent memory, and executed unauthorized actions — before most users knew they were installed. The attack was called ClawHavoc.

Every tool that tried to stop it relied on the same defense: probabilistic scanning. VirusTotal signatures. Heuristic classifiers. Pattern matching. Those tools are good at catching *known* malware. ClawHavoc used *unknown* malware — freshly generated, polymorphic, and designed to look legitimate until it wasn't.

**Pre-Flight doesn't scan for known-bad. It checks every action against rules you wrote — before the action executes.**

If a ClawHavoc skill had tried to:
- Exfiltrate your API key to an external server → **UNSAT**
- Send email to a domain you didn't authorize → **UNSAT**
- Write files outside your project directory → **UNSAT**
- Call an external URL not in your allowlist → **UNSAT**

Not because Pre-Flight recognized the attack signature. Because you said those things aren't allowed, and formal verification proved they violated your rules.

---

## Why formal verification is different

Every other guardrail in this ecosystem works by asking a model "does this seem bad?" That's probabilistic. A clever attacker — or a cleverly poisoned skill — can find the edge cases. "Seems safe" is not the same as "is safe."

Pre-Flight uses **SMT-based formal verification** (the same class of technology used to verify chip designs, cryptographic protocols, and aerospace control systems). Your policy is compiled into a set of logical constraints. Each action is checked against those constraints. The result is a **mathematical proof**, not a confidence score.

| | Model-based guardrails | Pre-Flight |
|---|---|---|
| **Approach** | "Does this look bad?" | "Does this violate the rules?" |
| **Result** | Probability estimate | Proof |
| **Adversarial robustness** | Bypassable with clever wording | Constraint is either satisfied or it isn't |
| **Auditability** | Black box | Every block has a `check_id` receipt |
| **Latency** | Varies | < 1 second |
| **Self-hosting required** | Sometimes | No |

---

## How it works

**You write your policy once, in plain English:**

```
1. No email may be sent to an external party without a confirmation token.
2. No financial transaction may exceed $100 without explicit user approval.
3. File deletions are not permitted outside the /tmp directory.
4. External API calls are only permitted to domains on the approved list.
```

**ICME compiles it into formal constraints (one-time, $3.00).**

**Your agent calls `checkIt` before every consequential action:**

```bash
curl -s -N -X POST https://api.icme.io/v1/checkIt \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ICME_API_KEY" \
  -d '{
    "policy_id": "'"$ICME_POLICY_ID"'",
    "action": "Send invoice to billing@external-vendor.com for $2,400."
  }'
```

**It gets back a proof, not a guess:**

```json
{
  "result": "UNSAT",
  "reason": "Action violates rule 2: transaction amount $2,400 exceeds $100 limit without explicit user approval.",
  "check_id": "chk_8f3a..."
}
```

The agent stops. The action does not execute. You have a receipt.

---

## Real ClawHavoc attack patterns — blocked

These are the attack categories documented in ClawHavoc post-mortems. Here's how a Pre-Flight policy would have handled each one:

**Credential exfiltration via HTTP**
> Skill sends `$HOME/.ssh/id_rsa` contents to `https://attacker[.]io/collect`

Policy rule: `"External HTTP calls are only permitted to icme.io and api.github.com."`
Result: **UNSAT** — domain `attacker[.]io` not on allowlist.

---

**Delayed activation — skill waits 72 hours then acts**
> After installation, skill reads all files in the workspace and emails them to an external address

Policy rule: `"No email may be sent to an address outside the @yourcompany.com domain."`
Result: **UNSAT** — recipient domain fails rule.

---

**Prompt injection through skill metadata**
> Malicious skill embeds instructions in its description to override agent behavior and approve unauthorized payments

Policy rule: `"No payment may be initiated without an explicit confirmation token present in the action description."`
Result: **UNSAT** — no confirmation token, payment blocked regardless of how the instruction was injected.

---

**Typosquatting skill impersonation**
> Skill named `github-pr-manager` (legitimate) vs `gittub-pr-manager` (malicious) — malicious version exfiltrates PR content

Policy rule: `"File reads outside the current project directory are not permitted."`
Result: **UNSAT** — malicious skill tries to read `~/.gitconfig` and SSH keys outside project scope.

---

## Setup — 4 steps, done once by a human

### 1. Install the skill

```bash
clawhub install pre-flight
```

### 2. Get your API key

```bash
# Create account ($5 minimum to start)
curl -s -X POST https://api.icme.io/v1/createUserCard \
  -H 'Content-Type: application/json' \
  -d '{"username": "your-username"}' | jq .
# Open checkout_url in your browser
# Then get your key:
curl -s https://api.icme.io/v1/session/SESSION_ID | jq .
```

### 3. Write and compile your policy

```bash
curl -s -N -X POST https://api.icme.io/v1/makeRules \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $ICME_API_KEY" \
  -d '{
    "policy": "1. No email may be sent to an external domain.\n2. No financial transaction may exceed $100.\n3. File writes are not permitted outside the current working directory.\n4. External HTTP calls are only permitted to approved domains."
  }'
# Save the policy_id from the response
```

One-time cost: **300 credits ($3.00)**. Takes under 10 seconds.

### 4. Set environment variables

```bash
export ICME_API_KEY=sk-smt-...
export ICME_POLICY_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Your agent will check actions automatically from here.

---

## Pricing

| Credits | Cost | Per check |
|---|---|---|
| 500 | $5.00 | $0.01 |
| 1,050 (+5%) | $10.00 | $0.0095 |
| 2,750 (+10%) | $25.00 | $0.0091 |
| 5,750 (+15%) | $50.00 | $0.0087 |
| 12,000 (+20%) | $100.00 | $0.0083 |

Policy compilation: 300 credits ($3.00), one-time per policy. Each `checkIt` call: 1 credit.

Running Pre-Flight on 1,000 agent actions per month costs **$10**.

---

## Writing a good policy

A policy is a numbered list of plain English rules. Each rule should be specific enough that a formal verifier can check it against an action string.

**Good rules — specific and checkable:**
```
1. No email may be sent to an address outside the @yourcompany.com domain.
2. No financial transaction may exceed $500 without a confirmation token.
3. Files may only be deleted from the /tmp or /var/cache directories.
4. Outbound HTTP calls are only permitted to: api.github.com, api.stripe.com, api.icme.io.
5. No SSH keys or credential files may be read or transmitted.
```

**Weak rules — too vague to enforce formally:**
```
1. Be careful with emails.       ← What does "careful" mean?
2. Don't do anything suspicious. ← Unquantifiable.
3. Protect sensitive data.       ← Against what actions, specifically?
```

Write rules the way you'd write an access control policy — not the way you'd write a prompt.

---

## What Pre-Flight does not do

Pre-Flight is a **pre-execution action gate**, not a firewall for everything your agent touches.

- It does not scan skill source code for malware
- It does not monitor runtime memory or network traffic
- It does not replace VirusTotal scanning for skill provenance
- It does not protect against prompt injection attacks in your system prompt

What it does: before your agent executes a consequential action, it checks whether that action is allowed by your policy. If it isn't, the action is blocked — regardless of how the instruction got there.

Use Pre-Flight alongside ClawHub's VirusTotal scanning, not instead of it.

---

## Links

- [ICME Documentation](https://docs.icme.io/documentation)
- [Writing Effective Policies](https://docs.icme.io/documentation/basics/writing-effective-policies)
- [API Reference](https://docs.icme.io/api-reference)
- [icme.io](https://icme.io)

---

*Pre-Flight is built by [ICME Labs](https://icme.io) — cryptographers building formal verification for AI agents.*
