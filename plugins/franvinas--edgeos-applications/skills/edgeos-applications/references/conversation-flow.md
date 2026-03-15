# Conversation Flow (v1)

## Contract
- Keep messages short.
- Ask one question at a time.
- Confirm critical choices before submit.
- Pre-fill fields already known.
- Ask only for missing required fields.
- Never ask for first/last name if it can be inferred reliably from known identity/context.
- Do not ask for fields already known.
- Do not show internal IDs unless the user asks.

## Step 1 — Authenticate
1. If a valid JWT is already present in current session state, skip OTP and continue.
2. Otherwise ask for email.
3. Trigger OTP via `scripts/auth_request_otp.sh <email>`.
4. Ask for 6-digit code.
5. Exchange code via `scripts/auth_login.sh <email> <code>`.
6. JWT is persisted to script state keyed by email and reused by subsequent scripts.
7. Persist the authenticated email as session auth identity and pass it as `SESSION_EMAIL` in subsequent script runs.
8. Fetch profile: `GET /citizens/profile`.

Re-auth rule:
- Ask for OTP again only after a 401/unauthorized response or if no JWT is available in script state.
- Before asking for re-auth, reload JWT from script state and retry one authenticated call (e.g., profile/status) once.
- Never claim token expiry unless a real API response indicates unauthorized after that retry.

## Step 2 — Popup discovery
1. `GET /popups` with bearer token.
2. Match user intent by name/slug similarity.
3. Prioritize popups that are not finished (`end_date >= now`) over historical ones.
4. If multiple not-finished matches exist, prefer the nearest upcoming one by start date.
5. Never continue with a finished popup (`end_date < now`).
6. If the user's requested popup is finished, explain it ended and ask which active/upcoming popup they want instead.
7. Confirm selected popup with user.

## Step 3 — Build field map (required first, optional when possible)
Required for v1:
- `first_name`
- `last_name`
- `telegram`
- `gender`
- `age`
- `local_resident`
- `organization`
- `duration`
- `citizen_id`
- `popup_city_id`
- `status` (`in review`)

Optional candidates to prefill aggressively whenever plausible:
- `residence`, `role`, `social_media`, `preferred_dates`, `referral`, `eth_address`, `video_url`, etc.
- Infer booleans from context when possible:
  - `builder_boolean` from technical/builder profile
  - `investor` from investor/VC intent signals
- If inference is unclear, ask the optional question explicitly (do not silently invent or default).
- Privacy exclusions (`info_not_shared`): ask optional preference if unknown.
- `personal_goals`: never auto-invent text. Ask as optional if unknown.

Fill this map in order:
1. `USER.md` known user context (primary source for all mappable fields).
2. API/profile values.
3. Known user identity/context from the current chat/session and prior turns.
4. Sender metadata inference (for names).
5. Ask user only for still-missing required fields.

Never ask for fields that are already resolved.
If a value exists in `USER.md`, reuse it and do not ask again unless the user asks to change it.
Infer `gender` from pronouns/context by default; ask only if unknown.
Infer `local_resident` from known location context by default (e.g., Buenos Aires => not local for Edge Esmeralda).

Question ordering for unresolved required fields:
1) `local_resident` 2) `duration` 3) remaining unresolved fields.

Do not ask `telegram` or `age` if they can be resolved from known user context (`USER.md`, prior turns, sender identity) and normalization rules.

## Step 4 — Full review + gap resolution
Show a full review using the exact frontend question wording from the form (required + optional), excluding internal workflow fields like `status`.

Use these canonical labels in review/questions:
- First name (required)
- Last name (required)
- Telegram username (required)
- Usual location of residence (optional)
- Gender (required)
- Age (required)
- Did anyone refer you? (optional)
- ETH address (optional)
- Are you a Sonoma resident? (required)
- Info I'm NOT willing to share with other attendees (optional)
- Organization you represent (required)
- Role in the organization (optional)
- Your active social media accounts (optional)
- Duration (required)
- Are you a builder/developer interested in creating open-source software at Edge Esmeralda 2026? (optional)
- Are you a venture capitalist / investor coming to source deals? (optional)
- Video URL (optional)
- What are your goals in attending Edge Esmeralda 2026? (optional)
- I am bringing a spouse/partner (optional)
- I'm bringing kids (optional)
- Are you interested in applying for a scholarship? (optional)

For unresolved fields:
- Ask each unresolved field explicitly using the same canonical label.
- Include `(required)` or `(optional)` in the question.

Only when no required fields remain unresolved, ask:
"Do you want to change anything, or should I submit it as-is?"
Submit only after explicit approval.

Age normalization:
- If user gives numeric age, convert to API ranges:
  - 18-24, 25-34, 35-44, 45-54, 55+
- Example: `27` -> `25-34`.

Field normalization:
- `telegram`: accept with/without `@`, store normalized as `@username`.
- `local_resident`: normalize to boolean (`yes`->true, `no`->false).
- `duration`: only allowed values:
  - `1 week`
  - `1 weekend`
  - `2 weeks`
  - `a few days`
  - `full length`
- `preferred_dates`: if missing, derive from `duration` when possible (`full length` -> `full length`; otherwise mirror selected duration label).

## Step 5 — Submit
Use `scripts/submit_application.sh` only after user approval.

After success, return:
- application id
- status

## Step 6 — Status checks
If user asks for status, use `scripts/check_application_status.sh`.

## Step 7 — Product selection and payment (only after acceptance)
1. Verify application status is `accepted`.
2. List active products in friendly language (name + price), no IDs shown.
3. Ask user choice.
4. Run `payment_preview.sh`, show total, ask confirmation.
5. Run `payment_create.sh`, return checkout link.
6. If user asks later, run `payment_status.sh`.

## User-friendly errors
- Citizen not found → "That email is not registered. Try another one?"
- Validation error → ask only the invalid field again.
- Duplicate application → automatically fetch existing application and return current status.
