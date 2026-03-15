---
name: KYC & Identity
description: "Know-Your-Customer verification via MasterPay Global. Submit personal data, upload identity documents, and track approval status."
---

# KYC & Identity

Use this skill when the user needs to complete identity verification, upload KYC documents, or check verification status.

## Available Tools

- `create_masterpay_user` — Create a MasterPay user account (prerequisite for all MasterPay operations) | `POST /api/v1/masterpay/users` | Requires auth
- `get_kyc_status` — Check current KYC verification status and document upload progress | `GET /api/v1/masterpay/kyc/status` | Requires auth
- `get_kyc_metadata` — Get valid document types, occupations, nationalities, and countries for KYC forms | `GET /api/v1/masterpay/kyc/metadata` | Requires auth
- `submit_kyc` — Submit KYC personal data for review (uses profile data) | `POST /api/v1/masterpay/kyc/submit` | Requires auth
- `upload_kyc_document` — Upload a KYC document (passport, ID, proof of address) via multipart or base64 JSON | `POST /api/v1/masterpay/kyc/documents` | Requires auth
- `submit_wallet_kyc` — Submit wallet-level KYC for a card wallet (requires profile phone number and identity document ID number) | `POST /api/v1/masterpay/wallets/kyc` | Requires auth
- `get_profile` — Get user profile data used for KYC submission | `GET /api/v1/profile` | Requires auth
- `update_profile` — Update user profile data (name, DOB, nationality, etc.) | `PUT /api/v1/profile` | Requires auth
- `get_document` — Get stored identity document info | `GET /api/v1/profile/document` | Requires auth
- `update_document` — Update identity document details (passport number, NRIC, etc.) | `PUT /api/v1/profile/document` | Requires auth
- `get_residential_address` — Get residential address on file | `GET /api/v1/profile/res-address` | Requires auth
- `update_residential_address` — Update residential address | `PUT /api/v1/profile/res-address` | Requires auth

## Recommended Flows

### Complete KYC Verification

Full flow from profile setup to KYC approval

0. Create MasterPay user: POST /api/v1/masterpay/users — required once before any MasterPay operation
1. Get metadata: GET /api/v1/masterpay/kyc/metadata — learn valid nationalities, occupations, document types
2. Update profile: PUT /api/v1/profile with name, DOB, gender, phone_number, phone_country_code (with '+' prefix, e.g. '+65'), nationality, occupation, source_of_fund
3. Update residential address: PUT /api/v1/profile/res-address with country_code (ISO alpha-2, e.g. 'SG'), province, city, zip_code, english_address_line_1/2/3
4. Upload documents: POST /api/v1/masterpay/kyc/documents — upload passport/ID front, back, selfie, proof of address
5. Submit KYC: POST /api/v1/masterpay/kyc/submit — merges profile + residential address, resolves country codes to names, and sends to MasterPay
6. Poll status: GET /api/v1/masterpay/kyc/status — wait for 'approved' (can take minutes to days)


## Rules

- MasterPay user must be created (POST /masterpay/users) before any KYC, wallet, or card operation — this is a one-time setup step
- Profile AND residential address must both be complete before submitting KYC — submit reads from both
- Use ISO alpha-2 country codes (e.g. 'SG', 'HK', 'MY') in residential address — the backend resolves them to full country names for MasterPay
- Phone country code in profile must include the '+' prefix (e.g. '+65') — MasterPay requires it
- Documents should be uploaded before submission — MasterPay requires passport/ID and proof of address, but our backend does not block submission without them
- KYC review can take minutes to several days — poll status periodically
- Once approved, KYC does not need to be repeated
- Document uploads support both multipart/form-data and JSON with base64 — max 15MB per file

## Agent Guidance

Follow these instructions when executing this skill:

- Always follow the documented flow order. Do not skip steps.
- If a tool requires authentication, verify the session has a valid bearer token before calling it.
- If a tool requires a transaction PIN, ask the user for it fresh each time. Never cache or log PINs.
- Never expose, log, or persist secrets (passwords, tokens, full card numbers, CVVs).
- If the user requests an operation outside this skill's scope, decline and suggest the appropriate skill.
- If a step fails, check the error and follow the recovery guidance below before retrying.

- Before any KYC operation, ensure a MasterPay user exists by calling `create_masterpay_user`. This is a one-time setup. Other MasterPay handlers also auto-create the user, but calling it explicitly is good practice.
- Complete both profile (`update_profile`) and residential address (`update_residential_address`) before calling `submit_kyc`. The backend validates both are present and returns 404 if either is missing.
- Upload documents (`upload_kyc_document`) before submitting KYC. MasterPay requires them, but our backend does not block submission without them — submit will succeed, but MasterPay may reject the application.
- `submit_wallet_kyc` requires the user's profile (phone number + phone country code) and identity document (ID number) to be set first. It will fail with INCOMPLETE_PROFILE if the ID number is missing.
- KYC review takes minutes to days. Poll `get_kyc_status` periodically — there are no push notifications.
- Use ISO alpha-2 country codes (e.g., "SG", "MY") for addresses. Include the "+" prefix for phone country codes (e.g., "+65").
