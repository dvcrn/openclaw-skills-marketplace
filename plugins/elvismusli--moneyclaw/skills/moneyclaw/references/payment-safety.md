# Authorized Payment Safety Reference

Use this reference when:

- you are about to enter card details on an unfamiliar site
- the user asks about phishing, fraud, or safe checkout behavior
- a merchant declines payment and you need retry guidance
- you need to confirm whether a checkout is within the user's authorized scope

## Table of Contents

1. Authorization Boundaries
2. Pre-Payment Checklist
3. Verification And Retry Rules
4. Subscription And Currency Traps
5. When To Stop And Ask The User

## 1. Authorization Boundaries

Follow these rules for every MoneyClaw payment flow:

- only use MoneyClaw for purchases or payment flows explicitly requested or pre-authorized by the user
- only use wallet, card, and billing data returned by the user's own MoneyClaw account
- respect merchant, issuer, card-network, and verification controls, including OTP and 3DS steps
- treat fraud checks, KYC, sanctions, geography rules, merchant restrictions, issuer declines, and other payment controls as hard boundaries
- never fabricate billing identity, cardholder data, addresses, names, phone numbers, or verification information
- prefer prepaid, bounded-risk flows by default

## 2. Pre-Payment Checklist

Run this checklist before entering card details:

1. Verify the exact domain. In `paypal.com.secure-verify.net`, the real domain is `secure-verify.net`.
2. Confirm HTTPS is present, but do not treat HTTPS alone as proof of legitimacy.
3. Confirm the total amount and currency.
4. Confirm card balance covers the amount plus a small buffer.
5. Use the billing address from the card credentials. Do not invent one.
6. Confirm the purchase matches the user's request or the user's pre-authorized scope.
7. If the merchant asks for information that is not present in the account data, stop and ask the user.
8. If the flow shows obvious scam signals, do not continue.

## 3. Verification And Retry Rules

- never retry immediately after a merchant error; read transaction history first
- maximum two retries per merchant session unless the user explicitly confirms further attempts
- if topup returns `202`, wait and re-check state instead of sending another topup
- do not keep retrying after repeated CVV or verification failures
- if the merchant, inbox, and transaction history give conflicting signals, stop and inspect state before doing anything else

Common guidance:

- `INSUFFICIENT_BALANCE`: top up or reduce purchase amount
- `CARD_NOT_ACTIVE`: card is not ready yet
- merchant-side error with no clear payment result: read `/api/cards/{cardId}/transactions` before trying again

## 4. Subscription And Currency Traps

Watch for these patterns:

- free trials that auto-convert to paid subscriptions
- hidden fees that appear only at final checkout
- pre-checked upsells
- cancellation flows designed to be difficult

For foreign-currency checkouts:

- decline Dynamic Currency Conversion if offered
- pay in the merchant's local currency when possible
- let the card network handle conversion instead of the merchant

## 5. When To Stop And Ask The User

Stop and ask the user if any of these are true:

- the merchant requests identity documents, social security numbers, bank account data, or unusual verification details
- the amount, currency, or merchant domain no longer matches the expected purchase
- the merchant or issuer decline appears related to compliance, sanctions, geography, or merchant policy
- the checkout asks for contact or identity information that is not already present in the user's account data
- you are no longer sure the flow is within the user's requested or pre-authorized scope
