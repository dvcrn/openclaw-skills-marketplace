# EdgeOS API Flow (v1)

Base settings (v1 fixed PROD):
- source `{baseDir}/scripts/env.sh`
- `BASE_URL` comes from that file
- Auth header: `Authorization: Bearer $JWT`

## 1) Request OTP
Use script: `scripts/auth_request_otp.sh <email>`
(under the hood: `POST /citizens/authenticate-edgeclaw`)

## 2) Exchange OTP for JWT
Use script: `scripts/auth_login.sh <email> <6digit>`
(under the hood: `POST /citizens/login?email=<urlencoded>&code=<6digit>`)

`auth_login.sh` persists `access_token` into script state under `scripts/.state/` keyed by email.
Other scripts auto-load token for `SESSION_EMAIL` when `JWT` env is not provided.
Do not request a new OTP unless API returns 401/unauthorized or JWT is missing.

## 3) Profile
`GET /citizens/profile`
Extract `id`, `first_name`, `last_name`.

## 4) Popups
`GET /popups`
Resolve popup `id` by exact or close name/slug match, with date-aware ranking:
- Prefer `end_date >= now` (not finished).
- Then prefer nearest upcoming `start_date`.
- Reject finished popups (`end_date < now`) for new applications.
- If all matches are finished, ask user to choose a currently active/upcoming popup.

## 5) Submit application
`POST /applications/`
If using temp payload files, include email reference in filename (example: `.tmp_application_payload_francisco_openclaw_muvinai_com_249_7.json`).
Minimum fields:
- `first_name`
- `last_name`
- `citizen_id`
- `popup_city_id`
- `status` = `in review`
- required conversation fields for v1 (`telegram`, `gender`, `age`, `local_resident`, `organization`, `duration`)

Optional fill strategy:
- Include optional fields aggressively when values are known/inferred.
- Default unknown optional booleans to `false`.
- Leave uncertain free-text optional fields omitted.

Store:
- `id` => application_id
- `status`

## 6) Check status
Preferred script behavior:
- If `application_id` is known: `GET /applications/{id}`
- If not: resolve with `GET /applications?citizen_id=<id>&popup_city_id=<id>`, then fetch by id.

Return current status to user.

## 7) Product retrieval (accepted only)
`GET /products?popup_city_id=<id>&is_active=true&limit=100&sort_by=name&sort_order=asc`

Only proceed if application status is `accepted`.

## 8) Payment preview
Use script: `scripts/payment_preview.sh`

Required inputs:
- application_id
- product_id (internal mapping from user's product choice)
- attendee_id (main attendee)

## 9) Payment create
Use script: `scripts/payment_create.sh`

Return `checkout_url` to user.

## 10) Payment status
Use script: `scripts/payment_status.sh --payment-id <id>`

Terminal states:
- success: `approved`
- failure: `expired`, `cancelled`
- pending: keep waiting / check later
