# API Contract (Distilled for openclaw-popup-application)

Use this file as the canonical contract for this skill's runtime behavior.
Source: `https://portaldev.simplefi.tech/openapi.json`.

## Auth flow

### 1) Request OTP
- **POST** `/citizens/authenticate-edgeclaw`
- Body: `{ "email": "user@example.com" }`
- Expected success: 200, message like `Mail sent successfully`

### 2) Exchange OTP for JWT
- **POST** `/citizens/login?email=<urlencoded>&code=<6digit>`
- Expected success: `{"access_token":"...","token_type":"Bearer"}`

### 3) Profile
- **GET** `/citizens/profile`
- Header: `Authorization: Bearer <JWT>`
- Key fields used by this skill:
  - `id` (citizen_id)
  - `first_name`, `last_name`
  - `email/primary_email`

## Popup resolution

### 4) List popups
- **GET** `/popups`
- Header: `Authorization: Bearer <JWT>`
- Key fields:
  - `id`, `name`, `slug`
  - `start_date`, `end_date`
  - `requires_approval`

Selection policy for this skill:
1. Match intent by name/slug similarity.
2. Prefer not-finished popups (`end_date >= now`).
3. Then prefer nearest upcoming `start_date`.
4. Only suggest finished popup if no active/upcoming candidate matches.

## Applications

### 5) Create application
- **POST** `/applications`
- Header: `Authorization: Bearer <JWT>`
- Body schema: `ApplicationCreate`
- User-settable status: `draft | in review`
- Skill default: `status = "in review"`

Minimum fields used by this skill:
- `first_name`, `last_name`
- `citizen_id`, `popup_city_id`
- required conversational fields (`telegram`, `gender`, `age`, `local_resident`, `organization`)
- optional fields only when provided

### 6) Get applications / dedupe lookup
- **GET** `/applications?citizen_id=<id>&popup_city_id=<id>`
- Header: `Authorization: Bearer <JWT>`
- Used for duplicate handling and resolve-by-citizen+popup.

### 7) Get application by id
- **GET** `/applications/{application_id}`
- Header: `Authorization: Bearer <JWT>`

Application statuses (from API):
- `draft`, `in review`, `accepted`, `rejected`, `withdrawn`

## Products and payments

### 8) List products
- **GET** `/products?popup_city_id=<id>&is_active=true&limit=100&sort_by=name&sort_order=asc`
- Header: `Authorization: Bearer <JWT>`
- Key fields:
  - `id`, `name`, `description`, `price`
  - `min_price`, `max_price` (variable-price support)
  - `attendee_category`, `is_active`

### 9) Payment preview
- **POST** `/payments/preview`
- Header: `Authorization: Bearer <JWT>`
- Body schema: `PaymentCreate`
- Key output fields:
  - `amount`, `currency`, optional `discount_value`

### 10) Create payment
- **POST** `/payments`
- Header: `Authorization: Bearer <JWT>`
- Body schema: `PaymentCreate`
- Key output fields:
  - `id`, `status`, `checkout_url`, `amount`, `external_id`

### 11) Payment status
- **GET** `/payments/{payment_id}`
- Header: `Authorization: Bearer <JWT>`
- Key fields:
  - `status`, `checkout_url`

## Guardrails derived from contract

- Never create payment before application status is `accepted`.
- Keep product IDs internal; show user-facing labels/prices only.
- On duplicate application create conflict, lookup existing application and return current status.
- Never expose full OTP/JWT in chat output.
