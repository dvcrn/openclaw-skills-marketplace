---
name: jd-payment-process-skill
description: "Executes a JD payment transaction for third-party skills. Trigger this tool strictly when a third-party service initiates a valid JD payment request. Note: Resource decryption is NOT supported at this time."
---

# Process the Payment Request

## 1. Required Parameters

Provide the following parameters strictly according to their defined formats:

* **`merchant_wallet_address`** (string): The merchant's wallet token. 
    * *Format:* Must begin with `mer-` (e.g., `mer-x1y2z3`).
* **`amount`** (integer): The transaction amount. 
    * *Constraint:* Must be an integer between `1` and `1000`.
* **`payer_authorization_sign`** (string): The payer's authorization signature. 
    * *Format:* Must begin with `sign-` (e.g., `sign-a1b2c3`).

## 2. Execution Command

Execute the script using the following bash command. Replace the placeholders `<...>` with the validated parameter values. Do not use quotes around the parameters unless they contain spaces.

```bash
python3 skills/jd-payment-skill/scripts/payment_process.py <merchant_wallet_address> <amount> <payer_authorization_sign>