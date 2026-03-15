---
name: lap-stripe-api
description: "Stripe API skill. Use when working with Stripe for account, account_links, account_sessions. Covers 587 endpoints."
---

# Stripe API
API version: 2026-02-25.clover

## Auth
Bearer basic | Bearer bearer

## Base URL
https://api.stripe.com/

## Setup
1. Set Authorization header with your Bearer token
2. GET /v1/account -- verify access
3. POST /v1/account_links -- create first account_links

## Endpoints

587 endpoints across 76 groups. See references/api-spec.lap for full details.

### account
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/account | Retrieve account |

### account_links
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/account_links | Create an account link |

### account_sessions
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/account_sessions | Create an Account Session |

### accounts
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/accounts | List all connected accounts |
| POST | /v1/accounts | <p>With <a href="/docs/connect">Connect</a>, you can create Stripe accounts for your users. |
| DELETE | /v1/accounts/{account} | Delete an account |
| GET | /v1/accounts/{account} | Retrieve account |
| POST | /v1/accounts/{account} | Update an account |
| POST | /v1/accounts/{account}/bank_accounts | Create an external account |
| DELETE | /v1/accounts/{account}/bank_accounts/{id} | Delete an external account |
| GET | /v1/accounts/{account}/bank_accounts/{id} | Retrieve an external account |
| POST | /v1/accounts/{account}/bank_accounts/{id} | <p>Updates the metadata, account holder name, account holder type of a bank account belonging to |
| GET | /v1/accounts/{account}/capabilities | List all account capabilities |
| GET | /v1/accounts/{account}/capabilities/{capability} | Retrieve an Account Capability |
| POST | /v1/accounts/{account}/capabilities/{capability} | Update an Account Capability |
| GET | /v1/accounts/{account}/external_accounts | List all external accounts |
| POST | /v1/accounts/{account}/external_accounts | Create an external account |
| DELETE | /v1/accounts/{account}/external_accounts/{id} | Delete an external account |
| GET | /v1/accounts/{account}/external_accounts/{id} | Retrieve an external account |
| POST | /v1/accounts/{account}/external_accounts/{id} | <p>Updates the metadata, account holder name, account holder type of a bank account belonging to |
| POST | /v1/accounts/{account}/login_links | Create a login link |
| GET | /v1/accounts/{account}/people | List all persons |
| POST | /v1/accounts/{account}/people | Create a person |
| DELETE | /v1/accounts/{account}/people/{person} | Delete a person |
| GET | /v1/accounts/{account}/people/{person} | Retrieve a person |
| POST | /v1/accounts/{account}/people/{person} | Update a person |
| GET | /v1/accounts/{account}/persons | List all persons |
| POST | /v1/accounts/{account}/persons | Create a person |
| DELETE | /v1/accounts/{account}/persons/{person} | Delete a person |
| GET | /v1/accounts/{account}/persons/{person} | Retrieve a person |
| POST | /v1/accounts/{account}/persons/{person} | Update a person |
| POST | /v1/accounts/{account}/reject | Reject an account |

### apple_pay
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/apple_pay/domains | <p>List apple pay domains.</p> |
| POST | /v1/apple_pay/domains | <p>Create an apple pay domain.</p> |
| DELETE | /v1/apple_pay/domains/{domain} | <p>Delete an apple pay domain.</p> |
| GET | /v1/apple_pay/domains/{domain} | <p>Retrieve an apple pay domain.</p> |

### application_fees
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/application_fees | List all application fees |
| GET | /v1/application_fees/{fee}/refunds/{id} | Retrieve an application fee refund |
| POST | /v1/application_fees/{fee}/refunds/{id} | Update an application fee refund |
| GET | /v1/application_fees/{id} | Retrieve an application fee |
| POST | /v1/application_fees/{id}/refund |  |
| GET | /v1/application_fees/{id}/refunds | List all application fee refunds |
| POST | /v1/application_fees/{id}/refunds | Create an application fee refund |

### apps
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/apps/secrets | List secrets |
| POST | /v1/apps/secrets | Set a Secret |
| POST | /v1/apps/secrets/delete | Delete a Secret |
| GET | /v1/apps/secrets/find | Find a Secret |

### balance
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/balance | Retrieve balance |
| GET | /v1/balance/history | List all balance transactions |
| GET | /v1/balance/history/{id} | Retrieve a balance transaction |

### balance_settings
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/balance_settings | Retrieve balance settings |
| POST | /v1/balance_settings | Update balance settings |

### balance_transactions
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/balance_transactions | List all balance transactions |
| GET | /v1/balance_transactions/{id} | Retrieve a balance transaction |

### billing
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/billing/alerts | List billing alerts |
| POST | /v1/billing/alerts | Create a billing alert |
| GET | /v1/billing/alerts/{id} | Retrieve a billing alert |
| POST | /v1/billing/alerts/{id}/activate | Activate a billing alert |
| POST | /v1/billing/alerts/{id}/archive | Archive a billing alert |
| POST | /v1/billing/alerts/{id}/deactivate | Deactivate a billing alert |
| GET | /v1/billing/credit_balance_summary | Retrieve the credit balance summary for a customer |
| GET | /v1/billing/credit_balance_transactions | List credit balance transactions |
| GET | /v1/billing/credit_balance_transactions/{id} | Retrieve a credit balance transaction |
| GET | /v1/billing/credit_grants | List credit grants |
| POST | /v1/billing/credit_grants | Create a credit grant |
| GET | /v1/billing/credit_grants/{id} | Retrieve a credit grant |
| POST | /v1/billing/credit_grants/{id} | Update a credit grant |
| POST | /v1/billing/credit_grants/{id}/expire | Expire a credit grant |
| POST | /v1/billing/credit_grants/{id}/void | Void a credit grant |
| POST | /v1/billing/meter_event_adjustments | Create a billing meter event adjustment |
| POST | /v1/billing/meter_events | Create a billing meter event |
| GET | /v1/billing/meters | List billing meters |
| POST | /v1/billing/meters | Create a billing meter |
| GET | /v1/billing/meters/{id} | Retrieve a billing meter |
| POST | /v1/billing/meters/{id} | Update a billing meter |
| POST | /v1/billing/meters/{id}/deactivate | Deactivate a billing meter |
| GET | /v1/billing/meters/{id}/event_summaries | List billing meter event summaries |
| POST | /v1/billing/meters/{id}/reactivate | Reactivate a billing meter |

### billing_portal
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/billing_portal/configurations | List portal configurations |
| POST | /v1/billing_portal/configurations | Create a portal configuration |
| GET | /v1/billing_portal/configurations/{configuration} | Retrieve a portal configuration |
| POST | /v1/billing_portal/configurations/{configuration} | Update a portal configuration |
| POST | /v1/billing_portal/sessions | Create a portal session |

### charges
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/charges | List all charges |
| POST | /v1/charges | <p>This method is no longer recommended—use the <a href="/docs/api/payment_intents">Payment Intents API</a> |
| GET | /v1/charges/search | Search charges |
| GET | /v1/charges/{charge} | Retrieve a charge |
| POST | /v1/charges/{charge} | Update a charge |
| POST | /v1/charges/{charge}/capture | Capture a payment |
| GET | /v1/charges/{charge}/dispute | <p>Retrieve a dispute for a specified charge.</p> |
| POST | /v1/charges/{charge}/dispute |  |
| POST | /v1/charges/{charge}/dispute/close |  |
| POST | /v1/charges/{charge}/refund | Create a refund |
| GET | /v1/charges/{charge}/refunds | List all refunds |
| POST | /v1/charges/{charge}/refunds | Create customer balance refund |
| GET | /v1/charges/{charge}/refunds/{refund} | <p>Retrieves the details of an existing refund.</p> |
| POST | /v1/charges/{charge}/refunds/{refund} | <p>Update a specified refund.</p> |

### checkout
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/checkout/sessions | List all Checkout Sessions |
| POST | /v1/checkout/sessions | Create a Checkout Session |
| GET | /v1/checkout/sessions/{session} | Retrieve a Checkout Session |
| POST | /v1/checkout/sessions/{session} | Update a Checkout Session |
| POST | /v1/checkout/sessions/{session}/expire | Expire a Checkout Session |
| GET | /v1/checkout/sessions/{session}/line_items | Retrieve a Checkout Session's line items |

### climate
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/climate/orders | List orders |
| POST | /v1/climate/orders | Create an order |
| GET | /v1/climate/orders/{order} | Retrieve an order |
| POST | /v1/climate/orders/{order} | Update an order |
| POST | /v1/climate/orders/{order}/cancel | Cancel an order |
| GET | /v1/climate/products | List products |
| GET | /v1/climate/products/{product} | Retrieve a product |
| GET | /v1/climate/suppliers | List suppliers |
| GET | /v1/climate/suppliers/{supplier} | Retrieve a supplier |

### confirmation_tokens
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/confirmation_tokens/{confirmation_token} | Retrieve a ConfirmationToken |

### country_specs
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/country_specs | List Country Specs |
| GET | /v1/country_specs/{country} | Retrieve a Country Spec |

### coupons
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/coupons | List all coupons |
| POST | /v1/coupons | Create a coupon |
| DELETE | /v1/coupons/{coupon} | Delete a coupon |
| GET | /v1/coupons/{coupon} | Retrieve a coupon |
| POST | /v1/coupons/{coupon} | Update a coupon |

### credit_notes
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/credit_notes | List all credit notes |
| POST | /v1/credit_notes | Create a credit note |
| GET | /v1/credit_notes/preview | Preview a credit note |
| GET | /v1/credit_notes/preview/lines | Retrieve a credit note preview's line items |
| GET | /v1/credit_notes/{credit_note}/lines | Retrieve a credit note's line items |
| GET | /v1/credit_notes/{id} | Retrieve a credit note |
| POST | /v1/credit_notes/{id} | Update a credit note |
| POST | /v1/credit_notes/{id}/void | Void a credit note |

### customer_sessions
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/customer_sessions | Create a Customer Session |

### customers
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/customers | List all customers |
| POST | /v1/customers | Create a customer |
| GET | /v1/customers/search | Search customers |
| DELETE | /v1/customers/{customer} | Delete a customer |
| GET | /v1/customers/{customer} | Retrieve a customer |
| POST | /v1/customers/{customer} | Update a customer |
| GET | /v1/customers/{customer}/balance_transactions | List customer balance transactions |
| POST | /v1/customers/{customer}/balance_transactions | Create a customer balance transaction |
| GET | /v1/customers/{customer}/balance_transactions/{transaction} | Retrieve a customer balance transaction |
| POST | /v1/customers/{customer}/balance_transactions/{transaction} | Update a customer credit balance transaction |
| GET | /v1/customers/{customer}/bank_accounts | List all bank accounts |
| POST | /v1/customers/{customer}/bank_accounts | Create a card |
| DELETE | /v1/customers/{customer}/bank_accounts/{id} | Delete a customer source |
| GET | /v1/customers/{customer}/bank_accounts/{id} | Retrieve a bank account |
| POST | /v1/customers/{customer}/bank_accounts/{id} | <p>Update a specified source for a given customer.</p> |
| POST | /v1/customers/{customer}/bank_accounts/{id}/verify | Verify a bank account |
| GET | /v1/customers/{customer}/cards | List all cards |
| POST | /v1/customers/{customer}/cards | Create a card |
| DELETE | /v1/customers/{customer}/cards/{id} | Delete a customer source |
| GET | /v1/customers/{customer}/cards/{id} | Retrieve a card |
| POST | /v1/customers/{customer}/cards/{id} | <p>Update a specified source for a given customer.</p> |
| GET | /v1/customers/{customer}/cash_balance | Retrieve a cash balance |
| POST | /v1/customers/{customer}/cash_balance | Update a cash balance's settings |
| GET | /v1/customers/{customer}/cash_balance_transactions | List cash balance transactions |
| GET | /v1/customers/{customer}/cash_balance_transactions/{transaction} | Retrieve a cash balance transaction |
| DELETE | /v1/customers/{customer}/discount | Delete a customer discount |
| GET | /v1/customers/{customer}/discount |  |
| POST | /v1/customers/{customer}/funding_instructions | Create or retrieve funding instructions for a customer cash balance |
| GET | /v1/customers/{customer}/payment_methods | List a Customer's PaymentMethods |
| GET | /v1/customers/{customer}/payment_methods/{payment_method} | Retrieve a Customer's PaymentMethod |
| GET | /v1/customers/{customer}/sources | <p>List sources for a specified customer.</p> |
| POST | /v1/customers/{customer}/sources | Create a card |
| DELETE | /v1/customers/{customer}/sources/{id} | Delete a customer source |
| GET | /v1/customers/{customer}/sources/{id} | <p>Retrieve a specified source for a given customer.</p> |
| POST | /v1/customers/{customer}/sources/{id} | <p>Update a specified source for a given customer.</p> |
| POST | /v1/customers/{customer}/sources/{id}/verify | Verify a bank account |
| GET | /v1/customers/{customer}/subscriptions | List active subscriptions |
| POST | /v1/customers/{customer}/subscriptions | Create a subscription |
| DELETE | /v1/customers/{customer}/subscriptions/{subscription_exposed_id} | Cancel a subscription |
| GET | /v1/customers/{customer}/subscriptions/{subscription_exposed_id} | Retrieve a subscription |
| POST | /v1/customers/{customer}/subscriptions/{subscription_exposed_id} | Update a subscription on a customer |
| DELETE | /v1/customers/{customer}/subscriptions/{subscription_exposed_id}/discount | Delete a customer discount |
| GET | /v1/customers/{customer}/subscriptions/{subscription_exposed_id}/discount |  |
| GET | /v1/customers/{customer}/tax_ids | List all Customer tax IDs |
| POST | /v1/customers/{customer}/tax_ids | Create a Customer tax ID |
| DELETE | /v1/customers/{customer}/tax_ids/{id} | Delete a Customer tax ID |
| GET | /v1/customers/{customer}/tax_ids/{id} | Retrieve a Customer tax ID |

### disputes
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/disputes | List all disputes |
| GET | /v1/disputes/{dispute} | Retrieve a dispute |
| POST | /v1/disputes/{dispute} | Update a dispute |
| POST | /v1/disputes/{dispute}/close | Close a dispute |

### entitlements
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/entitlements/active_entitlements | List all active entitlements |
| GET | /v1/entitlements/active_entitlements/{id} | Retrieve an active entitlement |
| GET | /v1/entitlements/features | List all features |
| POST | /v1/entitlements/features | Create a feature |
| GET | /v1/entitlements/features/{id} | Retrieve a feature |
| POST | /v1/entitlements/features/{id} | Updates a feature |

### ephemeral_keys
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/ephemeral_keys | Create an ephemeral key |
| DELETE | /v1/ephemeral_keys/{key} | Immediately invalidate an ephemeral key |

### events
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/events | List all events |
| GET | /v1/events/{id} | Retrieve an event |

### exchange_rates
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/exchange_rates | List all exchange rates |
| GET | /v1/exchange_rates/{rate_id} | Retrieve an exchange rate |

### external_accounts
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/external_accounts/{id} | <p>Updates the metadata, account holder name, account holder type of a bank account belonging to |

### file_links
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/file_links | List all file links |
| POST | /v1/file_links | Create a file link |
| GET | /v1/file_links/{link} | Retrieve a file link |
| POST | /v1/file_links/{link} | Update a file link |

### files
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/files | List all files |
| POST | /v1/files | Create a file |
| GET | /v1/files/{file} | Retrieve a file |

### financial_connections
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/financial_connections/accounts | List Accounts |
| GET | /v1/financial_connections/accounts/{account} | Retrieve an Account |
| POST | /v1/financial_connections/accounts/{account}/disconnect | Disconnect an Account |
| GET | /v1/financial_connections/accounts/{account}/owners | List Account Owners |
| POST | /v1/financial_connections/accounts/{account}/refresh | Refresh Account data |
| POST | /v1/financial_connections/accounts/{account}/subscribe | Subscribe to data refreshes for an Account |
| POST | /v1/financial_connections/accounts/{account}/unsubscribe | Unsubscribe from data refreshes for an Account |
| POST | /v1/financial_connections/sessions | Create a Session |
| GET | /v1/financial_connections/sessions/{session} | Retrieve a Session |
| GET | /v1/financial_connections/transactions | List Transactions |
| GET | /v1/financial_connections/transactions/{transaction} | Retrieve a Transaction |

### forwarding
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/forwarding/requests | List all ForwardingRequests |
| POST | /v1/forwarding/requests | Create a ForwardingRequest |
| GET | /v1/forwarding/requests/{id} | Retrieve a ForwardingRequest |

### identity
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/identity/verification_reports | List VerificationReports |
| GET | /v1/identity/verification_reports/{report} | Retrieve a VerificationReport |
| GET | /v1/identity/verification_sessions | List VerificationSessions |
| POST | /v1/identity/verification_sessions | Create a VerificationSession |
| GET | /v1/identity/verification_sessions/{session} | Retrieve a VerificationSession |
| POST | /v1/identity/verification_sessions/{session} | Update a VerificationSession |
| POST | /v1/identity/verification_sessions/{session}/cancel | Cancel a VerificationSession |
| POST | /v1/identity/verification_sessions/{session}/redact | Redact a VerificationSession |

### invoice_payments
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/invoice_payments | List all payments for an invoice |
| GET | /v1/invoice_payments/{invoice_payment} | Retrieve an InvoicePayment |

### invoice_rendering_templates
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/invoice_rendering_templates | List all invoice rendering templates |
| GET | /v1/invoice_rendering_templates/{template} | Retrieve an invoice rendering template |
| POST | /v1/invoice_rendering_templates/{template}/archive | Archive an invoice rendering template |
| POST | /v1/invoice_rendering_templates/{template}/unarchive | Unarchive an invoice rendering template |

### invoiceitems
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/invoiceitems | List all invoice items |
| POST | /v1/invoiceitems | Create an invoice item |
| DELETE | /v1/invoiceitems/{invoiceitem} | Delete an invoice item |
| GET | /v1/invoiceitems/{invoiceitem} | Retrieve an invoice item |
| POST | /v1/invoiceitems/{invoiceitem} | Update an invoice item |

### invoices
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/invoices | List all invoices |
| POST | /v1/invoices | Create an invoice |
| POST | /v1/invoices/create_preview | Create a preview invoice |
| GET | /v1/invoices/search | Search invoices |
| DELETE | /v1/invoices/{invoice} | Delete a draft invoice |
| GET | /v1/invoices/{invoice} | Retrieve an invoice |
| POST | /v1/invoices/{invoice} | Update an invoice |
| POST | /v1/invoices/{invoice}/add_lines | Bulk add invoice line items |
| POST | /v1/invoices/{invoice}/attach_payment | Attach a payment to an Invoice |
| POST | /v1/invoices/{invoice}/finalize | Finalize an invoice |
| GET | /v1/invoices/{invoice}/lines | Retrieve an invoice's line items |
| POST | /v1/invoices/{invoice}/lines/{line_item_id} | Update an invoice's line item |
| POST | /v1/invoices/{invoice}/mark_uncollectible | Mark an invoice as uncollectible |
| POST | /v1/invoices/{invoice}/pay | Pay an invoice |
| POST | /v1/invoices/{invoice}/remove_lines | Bulk remove invoice line items |
| POST | /v1/invoices/{invoice}/send | Send an invoice for manual payment |
| POST | /v1/invoices/{invoice}/update_lines | Bulk update invoice line items |
| POST | /v1/invoices/{invoice}/void | Void an invoice |

### issuing
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/issuing/authorizations | List all authorizations |
| GET | /v1/issuing/authorizations/{authorization} | Retrieve an authorization |
| POST | /v1/issuing/authorizations/{authorization} | Update an authorization |
| POST | /v1/issuing/authorizations/{authorization}/approve | Approve an authorization |
| POST | /v1/issuing/authorizations/{authorization}/decline | Decline an authorization |
| GET | /v1/issuing/cardholders | List all cardholders |
| POST | /v1/issuing/cardholders | Create a cardholder |
| GET | /v1/issuing/cardholders/{cardholder} | Retrieve a cardholder |
| POST | /v1/issuing/cardholders/{cardholder} | Update a cardholder |
| GET | /v1/issuing/cards | List all cards |
| POST | /v1/issuing/cards | Create a card |
| GET | /v1/issuing/cards/{card} | Retrieve a card |
| POST | /v1/issuing/cards/{card} | Update a card |
| GET | /v1/issuing/disputes | List all disputes |
| POST | /v1/issuing/disputes | Create a dispute |
| GET | /v1/issuing/disputes/{dispute} | Retrieve a dispute |
| POST | /v1/issuing/disputes/{dispute} | Update a dispute |
| POST | /v1/issuing/disputes/{dispute}/submit | Submit a dispute |
| GET | /v1/issuing/personalization_designs | List all personalization designs |
| POST | /v1/issuing/personalization_designs | Create a personalization design |
| GET | /v1/issuing/personalization_designs/{personalization_design} | Retrieve a personalization design |
| POST | /v1/issuing/personalization_designs/{personalization_design} | Update a personalization design |
| GET | /v1/issuing/physical_bundles | List all physical bundles |
| GET | /v1/issuing/physical_bundles/{physical_bundle} | Retrieve a physical bundle |
| GET | /v1/issuing/settlements/{settlement} | Retrieve a settlement |
| POST | /v1/issuing/settlements/{settlement} | Update a settlement |
| GET | /v1/issuing/tokens | List all issuing tokens for card |
| GET | /v1/issuing/tokens/{token} | Retrieve an issuing token |
| POST | /v1/issuing/tokens/{token} | Update a token status |
| GET | /v1/issuing/transactions | List all transactions |
| GET | /v1/issuing/transactions/{transaction} | Retrieve a transaction |
| POST | /v1/issuing/transactions/{transaction} | Update a transaction |

### link_account_sessions
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/link_account_sessions | Create a Session |
| GET | /v1/link_account_sessions/{session} | Retrieve a Session |

### linked_accounts
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/linked_accounts | List Accounts |
| GET | /v1/linked_accounts/{account} | Retrieve an Account |
| POST | /v1/linked_accounts/{account}/disconnect | Disconnect an Account |
| GET | /v1/linked_accounts/{account}/owners | List Account Owners |
| POST | /v1/linked_accounts/{account}/refresh | Refresh Account data |

### mandates
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/mandates/{mandate} | Retrieve a Mandate |

### payment_attempt_records
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_attempt_records | List Payment Attempt Records |
| GET | /v1/payment_attempt_records/{id} | Retrieve a Payment Attempt Record |

### payment_intents
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_intents | List all PaymentIntents |
| POST | /v1/payment_intents | Create a PaymentIntent |
| GET | /v1/payment_intents/search | Search PaymentIntents |
| GET | /v1/payment_intents/{intent} | Retrieve a PaymentIntent |
| POST | /v1/payment_intents/{intent} | Update a PaymentIntent |
| GET | /v1/payment_intents/{intent}/amount_details_line_items | List all PaymentIntent LineItems |
| POST | /v1/payment_intents/{intent}/apply_customer_balance | Reconcile a customer_balance PaymentIntent |
| POST | /v1/payment_intents/{intent}/cancel | Cancel a PaymentIntent |
| POST | /v1/payment_intents/{intent}/capture | Capture a PaymentIntent |
| POST | /v1/payment_intents/{intent}/confirm | Confirm a PaymentIntent |
| POST | /v1/payment_intents/{intent}/increment_authorization | Increment an authorization |
| POST | /v1/payment_intents/{intent}/verify_microdeposits | Verify microdeposits on a PaymentIntent |

### payment_links
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_links | List all payment links |
| POST | /v1/payment_links | Create a payment link |
| GET | /v1/payment_links/{payment_link} | Retrieve payment link |
| POST | /v1/payment_links/{payment_link} | Update a payment link |
| GET | /v1/payment_links/{payment_link}/line_items | Retrieve a payment link's line items |

### payment_method_configurations
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_method_configurations | List payment method configurations |
| POST | /v1/payment_method_configurations | Create a payment method configuration |
| GET | /v1/payment_method_configurations/{configuration} | Retrieve payment method configuration |
| POST | /v1/payment_method_configurations/{configuration} | Update payment method configuration |

### payment_method_domains
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_method_domains | List payment method domains |
| POST | /v1/payment_method_domains | Create a payment method domain |
| GET | /v1/payment_method_domains/{payment_method_domain} | Retrieve a payment method domain |
| POST | /v1/payment_method_domains/{payment_method_domain} | Update a payment method domain |
| POST | /v1/payment_method_domains/{payment_method_domain}/validate | Validate an existing payment method domain |

### payment_methods
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payment_methods | List PaymentMethods |
| POST | /v1/payment_methods | Shares a PaymentMethod |
| GET | /v1/payment_methods/{payment_method} | Retrieve a PaymentMethod |
| POST | /v1/payment_methods/{payment_method} | Update a PaymentMethod |
| POST | /v1/payment_methods/{payment_method}/attach | Attach a PaymentMethod to a Customer |
| POST | /v1/payment_methods/{payment_method}/detach | Detach a PaymentMethod from a Customer |

### payment_records
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/payment_records/report_payment | Report a payment |
| GET | /v1/payment_records/{id} | Retrieve a Payment Record |
| POST | /v1/payment_records/{id}/report_payment_attempt | Report a payment attempt |
| POST | /v1/payment_records/{id}/report_payment_attempt_canceled | Report payment attempt canceled |
| POST | /v1/payment_records/{id}/report_payment_attempt_failed | Report payment attempt failed |
| POST | /v1/payment_records/{id}/report_payment_attempt_guaranteed | Report payment attempt guaranteed |
| POST | /v1/payment_records/{id}/report_payment_attempt_informational | Report payment attempt informational |
| POST | /v1/payment_records/{id}/report_refund | Report a refund |

### payouts
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/payouts | List all payouts |
| POST | /v1/payouts | Create a payout |
| GET | /v1/payouts/{payout} | Retrieve a payout |
| POST | /v1/payouts/{payout} | Update a payout |
| POST | /v1/payouts/{payout}/cancel | Cancel a payout |
| POST | /v1/payouts/{payout}/reverse | Reverse a payout |

### plans
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/plans | List all plans |
| POST | /v1/plans | Create a plan |
| DELETE | /v1/plans/{plan} | Delete a plan |
| GET | /v1/plans/{plan} | Retrieve a plan |
| POST | /v1/plans/{plan} | Update a plan |

### prices
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/prices | List all prices |
| POST | /v1/prices | Create a price |
| GET | /v1/prices/search | Search prices |
| GET | /v1/prices/{price} | Retrieve a price |
| POST | /v1/prices/{price} | Update a price |

### products
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/products | List all products |
| POST | /v1/products | Create a product |
| GET | /v1/products/search | Search products |
| DELETE | /v1/products/{id} | Delete a product |
| GET | /v1/products/{id} | Retrieve a product |
| POST | /v1/products/{id} | Update a product |
| GET | /v1/products/{product}/features | List all features attached to a product |
| POST | /v1/products/{product}/features | Attach a feature to a product |
| DELETE | /v1/products/{product}/features/{id} | Remove a feature from a product |
| GET | /v1/products/{product}/features/{id} | Retrieve a product_feature |

### promotion_codes
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/promotion_codes | List all promotion codes |
| POST | /v1/promotion_codes | Create a promotion code |
| GET | /v1/promotion_codes/{promotion_code} | Retrieve a promotion code |
| POST | /v1/promotion_codes/{promotion_code} | Update a promotion code |

### quotes
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/quotes | List all quotes |
| POST | /v1/quotes | Create a quote |
| GET | /v1/quotes/{quote} | Retrieve a quote |
| POST | /v1/quotes/{quote} | Update a quote |
| POST | /v1/quotes/{quote}/accept | Accept a quote |
| POST | /v1/quotes/{quote}/cancel | Cancel a quote |
| GET | /v1/quotes/{quote}/computed_upfront_line_items | Retrieve a quote's upfront line items |
| POST | /v1/quotes/{quote}/finalize | Finalize a quote |
| GET | /v1/quotes/{quote}/line_items | Retrieve a quote's line items |
| GET | /v1/quotes/{quote}/pdf | Download quote PDF |

### radar
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/radar/early_fraud_warnings | List all early fraud warnings |
| GET | /v1/radar/early_fraud_warnings/{early_fraud_warning} | Retrieve an early fraud warning |
| POST | /v1/radar/payment_evaluations | Create a Payment Evaluation |
| GET | /v1/radar/value_list_items | List all value list items |
| POST | /v1/radar/value_list_items | Create a value list item |
| DELETE | /v1/radar/value_list_items/{item} | Delete a value list item |
| GET | /v1/radar/value_list_items/{item} | Retrieve a value list item |
| GET | /v1/radar/value_lists | List all value lists |
| POST | /v1/radar/value_lists | Create a value list |
| DELETE | /v1/radar/value_lists/{value_list} | Delete a value list |
| GET | /v1/radar/value_lists/{value_list} | Retrieve a value list |
| POST | /v1/radar/value_lists/{value_list} | Update a value list |

### refunds
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/refunds | List all refunds |
| POST | /v1/refunds | Create customer balance refund |
| GET | /v1/refunds/{refund} | Retrieve a refund |
| POST | /v1/refunds/{refund} | Update a refund |
| POST | /v1/refunds/{refund}/cancel | Cancel a refund |

### reporting
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/reporting/report_runs | List all Report Runs |
| POST | /v1/reporting/report_runs | Create a Report Run |
| GET | /v1/reporting/report_runs/{report_run} | Retrieve a Report Run |
| GET | /v1/reporting/report_types | List all Report Types |
| GET | /v1/reporting/report_types/{report_type} | Retrieve a Report Type |

### reviews
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/reviews | List all open reviews |
| GET | /v1/reviews/{review} | Retrieve a review |
| POST | /v1/reviews/{review}/approve | Approve a review |

### setup_attempts
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/setup_attempts | List all SetupAttempts |

### setup_intents
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/setup_intents | List all SetupIntents |
| POST | /v1/setup_intents | Create a SetupIntent |
| GET | /v1/setup_intents/{intent} | Retrieve a SetupIntent |
| POST | /v1/setup_intents/{intent} | Update a SetupIntent |
| POST | /v1/setup_intents/{intent}/cancel | Cancel a SetupIntent |
| POST | /v1/setup_intents/{intent}/confirm | Confirm a SetupIntent |
| POST | /v1/setup_intents/{intent}/verify_microdeposits | Verify microdeposits on a SetupIntent |

### shipping_rates
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/shipping_rates | List all shipping rates |
| POST | /v1/shipping_rates | Create a shipping rate |
| GET | /v1/shipping_rates/{shipping_rate_token} | Retrieve a shipping rate |
| POST | /v1/shipping_rates/{shipping_rate_token} | Update a shipping rate |

### sigma
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/sigma/saved_queries/{id} | Update an existing Sigma Query |
| GET | /v1/sigma/scheduled_query_runs | List all scheduled query runs |
| GET | /v1/sigma/scheduled_query_runs/{scheduled_query_run} | Retrieve a scheduled query run |

### sources
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/sources | Shares a source |
| GET | /v1/sources/{source} | Retrieve a source |
| POST | /v1/sources/{source} | Update a source |
| GET | /v1/sources/{source}/mandate_notifications/{mandate_notification} | Retrieve a Source MandateNotification |
| GET | /v1/sources/{source}/source_transactions | <p>List source transactions for a given source.</p> |
| GET | /v1/sources/{source}/source_transactions/{source_transaction} | Retrieve a source transaction |
| POST | /v1/sources/{source}/verify | <p>Verify a given source.</p> |

### subscription_items
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/subscription_items | List all subscription items |
| POST | /v1/subscription_items | Create a subscription item |
| DELETE | /v1/subscription_items/{item} | Delete a subscription item |
| GET | /v1/subscription_items/{item} | Retrieve a subscription item |
| POST | /v1/subscription_items/{item} | Update a subscription item |

### subscription_schedules
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/subscription_schedules | List all schedules |
| POST | /v1/subscription_schedules | Create a schedule |
| GET | /v1/subscription_schedules/{schedule} | Retrieve a schedule |
| POST | /v1/subscription_schedules/{schedule} | Update a schedule |
| POST | /v1/subscription_schedules/{schedule}/cancel | Cancel a schedule |
| POST | /v1/subscription_schedules/{schedule}/release | Release a schedule |

### subscriptions
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/subscriptions | List subscriptions |
| POST | /v1/subscriptions | Create a subscription |
| GET | /v1/subscriptions/search | Search subscriptions |
| DELETE | /v1/subscriptions/{subscription_exposed_id} | Cancel a subscription |
| GET | /v1/subscriptions/{subscription_exposed_id} | Retrieve a subscription |
| POST | /v1/subscriptions/{subscription_exposed_id} | Update a subscription |
| DELETE | /v1/subscriptions/{subscription_exposed_id}/discount | Delete a subscription discount |
| POST | /v1/subscriptions/{subscription}/migrate | Migrate a subscription |
| POST | /v1/subscriptions/{subscription}/resume | Resume a subscription |

### tax
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/tax/associations/find | Find a Tax Association |
| POST | /v1/tax/calculations | Create a Tax Calculation |
| GET | /v1/tax/calculations/{calculation} | Retrieve a Tax Calculation |
| GET | /v1/tax/calculations/{calculation}/line_items | Retrieve a calculation's line items |
| GET | /v1/tax/registrations | List registrations |
| POST | /v1/tax/registrations | Create a registration |
| GET | /v1/tax/registrations/{id} | Retrieve a registration |
| POST | /v1/tax/registrations/{id} | Update a registration |
| GET | /v1/tax/settings | Retrieve settings |
| POST | /v1/tax/settings | Update settings |
| POST | /v1/tax/transactions/create_from_calculation | Create a transaction from a calculation |
| POST | /v1/tax/transactions/create_reversal | Create a reversal transaction |
| GET | /v1/tax/transactions/{transaction} | Retrieve a transaction |
| GET | /v1/tax/transactions/{transaction}/line_items | Retrieve a transaction's line items |

### tax_codes
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/tax_codes | List all tax codes |
| GET | /v1/tax_codes/{id} | Retrieve a tax code |

### tax_ids
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/tax_ids | List all tax IDs |
| POST | /v1/tax_ids | Create a tax ID |
| DELETE | /v1/tax_ids/{id} | Delete a tax ID |
| GET | /v1/tax_ids/{id} | Retrieve a tax ID |

### tax_rates
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/tax_rates | List all tax rates |
| POST | /v1/tax_rates | Create a tax rate |
| GET | /v1/tax_rates/{tax_rate} | Retrieve a tax rate |
| POST | /v1/tax_rates/{tax_rate} | Update a tax rate |

### terminal
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/terminal/configurations | List all Configurations |
| POST | /v1/terminal/configurations | Create a Configuration |
| DELETE | /v1/terminal/configurations/{configuration} | Delete a Configuration |
| GET | /v1/terminal/configurations/{configuration} | Retrieve a Configuration |
| POST | /v1/terminal/configurations/{configuration} | Update a Configuration |
| POST | /v1/terminal/connection_tokens | Create a Connection Token |
| GET | /v1/terminal/locations | List all Locations |
| POST | /v1/terminal/locations | Create a Location |
| DELETE | /v1/terminal/locations/{location} | Delete a Location |
| GET | /v1/terminal/locations/{location} | Retrieve a Location |
| POST | /v1/terminal/locations/{location} | Update a Location |
| POST | /v1/terminal/onboarding_links | Create an Onboarding Link |
| GET | /v1/terminal/readers | List all Readers |
| POST | /v1/terminal/readers | Create a Reader |
| DELETE | /v1/terminal/readers/{reader} | Delete a Reader |
| GET | /v1/terminal/readers/{reader} | Retrieve a Reader |
| POST | /v1/terminal/readers/{reader} | Update a Reader |
| POST | /v1/terminal/readers/{reader}/cancel_action | Cancel the current reader action |
| POST | /v1/terminal/readers/{reader}/collect_inputs | Collect inputs using a Reader |
| POST | /v1/terminal/readers/{reader}/collect_payment_method | Hand off a PaymentIntent to a Reader and collect card details |
| POST | /v1/terminal/readers/{reader}/confirm_payment_intent | Confirm a PaymentIntent on the Reader |
| POST | /v1/terminal/readers/{reader}/process_payment_intent | Hand-off a PaymentIntent to a Reader |
| POST | /v1/terminal/readers/{reader}/process_setup_intent | Hand-off a SetupIntent to a Reader |
| POST | /v1/terminal/readers/{reader}/refund_payment | Refund a Charge or a PaymentIntent in-person |
| POST | /v1/terminal/readers/{reader}/set_reader_display | Set reader display |
| POST | /v1/terminal/refunds | Create a refund using a Terminal-supported device. |

### test_helpers
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/test_helpers/confirmation_tokens | Create a test Confirmation Token |
| POST | /v1/test_helpers/customers/{customer}/fund_cash_balance | Fund a test mode cash balance |
| POST | /v1/test_helpers/issuing/authorizations | Create a test-mode authorization |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/capture | Capture a test-mode authorization |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/expire | Expire a test-mode authorization |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/finalize_amount | Finalize a test-mode authorization's amount |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/fraud_challenges/respond | Respond to fraud challenge |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/increment | Increment a test-mode authorization |
| POST | /v1/test_helpers/issuing/authorizations/{authorization}/reverse | Reverse a test-mode authorization |
| POST | /v1/test_helpers/issuing/cards/{card}/shipping/deliver | Deliver a testmode card |
| POST | /v1/test_helpers/issuing/cards/{card}/shipping/fail | Fail a testmode card |
| POST | /v1/test_helpers/issuing/cards/{card}/shipping/return | Return a testmode card |
| POST | /v1/test_helpers/issuing/cards/{card}/shipping/ship | Ship a testmode card |
| POST | /v1/test_helpers/issuing/cards/{card}/shipping/submit | Submit a testmode card |
| POST | /v1/test_helpers/issuing/personalization_designs/{personalization_design}/activate | Activate a testmode personalization design |
| POST | /v1/test_helpers/issuing/personalization_designs/{personalization_design}/deactivate | Deactivate a testmode personalization design |
| POST | /v1/test_helpers/issuing/personalization_designs/{personalization_design}/reject | Reject a testmode personalization design |
| POST | /v1/test_helpers/issuing/settlements | Create a test-mode settlement |
| POST | /v1/test_helpers/issuing/settlements/{settlement}/complete | Complete a test-mode settlement |
| POST | /v1/test_helpers/issuing/transactions/create_force_capture | Create a test-mode force capture |
| POST | /v1/test_helpers/issuing/transactions/create_unlinked_refund | Create a test-mode unlinked refund |
| POST | /v1/test_helpers/issuing/transactions/{transaction}/refund | Refund a test-mode transaction |
| POST | /v1/test_helpers/refunds/{refund}/expire | Expire a pending refund. |
| POST | /v1/test_helpers/terminal/readers/{reader}/present_payment_method | Simulate presenting a payment method |
| POST | /v1/test_helpers/terminal/readers/{reader}/succeed_input_collection | Simulate a successful input collection |
| POST | /v1/test_helpers/terminal/readers/{reader}/timeout_input_collection | Simulate an input collection timeout |
| GET | /v1/test_helpers/test_clocks | List all test clocks |
| POST | /v1/test_helpers/test_clocks | Create a test clock |
| DELETE | /v1/test_helpers/test_clocks/{test_clock} | Delete a test clock |
| GET | /v1/test_helpers/test_clocks/{test_clock} | Retrieve a test clock |
| POST | /v1/test_helpers/test_clocks/{test_clock}/advance | Advance a test clock |
| POST | /v1/test_helpers/treasury/inbound_transfers/{id}/fail | Test mode: Fail an InboundTransfer |
| POST | /v1/test_helpers/treasury/inbound_transfers/{id}/return | Test mode: Return an InboundTransfer |
| POST | /v1/test_helpers/treasury/inbound_transfers/{id}/succeed | Test mode: Succeed an InboundTransfer |
| POST | /v1/test_helpers/treasury/outbound_payments/{id} | Test mode: Update an OutboundPayment |
| POST | /v1/test_helpers/treasury/outbound_payments/{id}/fail | Test mode: Fail an OutboundPayment |
| POST | /v1/test_helpers/treasury/outbound_payments/{id}/post | Test mode: Post an OutboundPayment |
| POST | /v1/test_helpers/treasury/outbound_payments/{id}/return | Test mode: Return an OutboundPayment |
| POST | /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer} | Test mode: Update an OutboundTransfer |
| POST | /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/fail | Test mode: Fail an OutboundTransfer |
| POST | /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/post | Test mode: Post an OutboundTransfer |
| POST | /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/return | Test mode: Return an OutboundTransfer |
| POST | /v1/test_helpers/treasury/received_credits | Test mode: Create a ReceivedCredit |
| POST | /v1/test_helpers/treasury/received_debits | Test mode: Create a ReceivedDebit |

### tokens
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/tokens | Create a CVC update token |
| GET | /v1/tokens/{token} | Retrieve a token |

### topups
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/topups | List all top-ups |
| POST | /v1/topups | Create a top-up |
| GET | /v1/topups/{topup} | Retrieve a top-up |
| POST | /v1/topups/{topup} | Update a top-up |
| POST | /v1/topups/{topup}/cancel | Cancel a top-up |

### transfers
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/transfers | List all transfers |
| POST | /v1/transfers | Create a transfer |
| GET | /v1/transfers/{id}/reversals | List all reversals |
| POST | /v1/transfers/{id}/reversals | Create a transfer reversal |
| GET | /v1/transfers/{transfer} | Retrieve a transfer |
| POST | /v1/transfers/{transfer} | Update a transfer |
| GET | /v1/transfers/{transfer}/reversals/{id} | Retrieve a reversal |
| POST | /v1/transfers/{transfer}/reversals/{id} | Update a reversal |

### treasury
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/treasury/credit_reversals | List all CreditReversals |
| POST | /v1/treasury/credit_reversals | Create a CreditReversal |
| GET | /v1/treasury/credit_reversals/{credit_reversal} | Retrieve a CreditReversal |
| GET | /v1/treasury/debit_reversals | List all DebitReversals |
| POST | /v1/treasury/debit_reversals | Create a DebitReversal |
| GET | /v1/treasury/debit_reversals/{debit_reversal} | Retrieve a DebitReversal |
| GET | /v1/treasury/financial_accounts | List all FinancialAccounts |
| POST | /v1/treasury/financial_accounts | Create a FinancialAccount |
| GET | /v1/treasury/financial_accounts/{financial_account} | Retrieve a FinancialAccount |
| POST | /v1/treasury/financial_accounts/{financial_account} | Update a FinancialAccount |
| POST | /v1/treasury/financial_accounts/{financial_account}/close | Close a FinancialAccount |
| GET | /v1/treasury/financial_accounts/{financial_account}/features | Retrieve FinancialAccount Features |
| POST | /v1/treasury/financial_accounts/{financial_account}/features | Update FinancialAccount Features |
| GET | /v1/treasury/inbound_transfers | List all InboundTransfers |
| POST | /v1/treasury/inbound_transfers | Create an InboundTransfer |
| GET | /v1/treasury/inbound_transfers/{id} | Retrieve an InboundTransfer |
| POST | /v1/treasury/inbound_transfers/{inbound_transfer}/cancel | Cancel an InboundTransfer |
| GET | /v1/treasury/outbound_payments | List all OutboundPayments |
| POST | /v1/treasury/outbound_payments | Create an OutboundPayment |
| GET | /v1/treasury/outbound_payments/{id} | Retrieve an OutboundPayment |
| POST | /v1/treasury/outbound_payments/{id}/cancel | Cancel an OutboundPayment |
| GET | /v1/treasury/outbound_transfers | List all OutboundTransfers |
| POST | /v1/treasury/outbound_transfers | Create an OutboundTransfer |
| GET | /v1/treasury/outbound_transfers/{outbound_transfer} | Retrieve an OutboundTransfer |
| POST | /v1/treasury/outbound_transfers/{outbound_transfer}/cancel | Cancel an OutboundTransfer |
| GET | /v1/treasury/received_credits | List all ReceivedCredits |
| GET | /v1/treasury/received_credits/{id} | Retrieve a ReceivedCredit |
| GET | /v1/treasury/received_debits | List all ReceivedDebits |
| GET | /v1/treasury/received_debits/{id} | Retrieve a ReceivedDebit |
| GET | /v1/treasury/transaction_entries | List all TransactionEntries |
| GET | /v1/treasury/transaction_entries/{id} | Retrieve a TransactionEntry |
| GET | /v1/treasury/transactions | List all Transactions |
| GET | /v1/treasury/transactions/{id} | Retrieve a Transaction |

### webhook_endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/webhook_endpoints | List all webhook endpoints |
| POST | /v1/webhook_endpoints | Create a webhook endpoint |
| DELETE | /v1/webhook_endpoints/{webhook_endpoint} | Delete a webhook endpoint |
| GET | /v1/webhook_endpoints/{webhook_endpoint} | Retrieve a webhook endpoint |
| POST | /v1/webhook_endpoints/{webhook_endpoint} | Update a webhook endpoint |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "List all account?" -> GET /v1/account
- "Create a account_link?" -> POST /v1/account_links
- "Create a account_session?" -> POST /v1/account_sessions
- "List all accounts?" -> GET /v1/accounts
- "Create a account?" -> POST /v1/accounts
- "Delete a account?" -> DELETE /v1/accounts/{account}
- "Get account details?" -> GET /v1/accounts/{account}
- "Create a bank_account?" -> POST /v1/accounts/{account}/bank_accounts
- "Delete a bank_account?" -> DELETE /v1/accounts/{account}/bank_accounts/{id}
- "Get bank_account details?" -> GET /v1/accounts/{account}/bank_accounts/{id}
- "List all capabilities?" -> GET /v1/accounts/{account}/capabilities
- "Get capability details?" -> GET /v1/accounts/{account}/capabilities/{capability}
- "List all external_accounts?" -> GET /v1/accounts/{account}/external_accounts
- "Create a external_account?" -> POST /v1/accounts/{account}/external_accounts
- "Delete a external_account?" -> DELETE /v1/accounts/{account}/external_accounts/{id}
- "Get external_account details?" -> GET /v1/accounts/{account}/external_accounts/{id}
- "Create a login_link?" -> POST /v1/accounts/{account}/login_links
- "List all people?" -> GET /v1/accounts/{account}/people
- "Create a people?" -> POST /v1/accounts/{account}/people
- "Delete a people?" -> DELETE /v1/accounts/{account}/people/{person}
- "Get people details?" -> GET /v1/accounts/{account}/people/{person}
- "List all persons?" -> GET /v1/accounts/{account}/persons
- "Create a person?" -> POST /v1/accounts/{account}/persons
- "Delete a person?" -> DELETE /v1/accounts/{account}/persons/{person}
- "Get person details?" -> GET /v1/accounts/{account}/persons/{person}
- "Create a reject?" -> POST /v1/accounts/{account}/reject
- "List all domains?" -> GET /v1/apple_pay/domains
- "Create a domain?" -> POST /v1/apple_pay/domains
- "Delete a domain?" -> DELETE /v1/apple_pay/domains/{domain}
- "Get domain details?" -> GET /v1/apple_pay/domains/{domain}
- "List all application_fees?" -> GET /v1/application_fees
- "Get refund details?" -> GET /v1/application_fees/{fee}/refunds/{id}
- "Get application_fee details?" -> GET /v1/application_fees/{id}
- "Create a refund?" -> POST /v1/application_fees/{id}/refund
- "List all refunds?" -> GET /v1/application_fees/{id}/refunds
- "Create a refund?" -> POST /v1/application_fees/{id}/refunds
- "List all secrets?" -> GET /v1/apps/secrets
- "Create a secret?" -> POST /v1/apps/secrets
- "Create a delete?" -> POST /v1/apps/secrets/delete
- "List all find?" -> GET /v1/apps/secrets/find
- "List all balance?" -> GET /v1/balance
- "List all history?" -> GET /v1/balance/history
- "Get history details?" -> GET /v1/balance/history/{id}
- "List all balance_settings?" -> GET /v1/balance_settings
- "Create a balance_setting?" -> POST /v1/balance_settings
- "List all balance_transactions?" -> GET /v1/balance_transactions
- "Get balance_transaction details?" -> GET /v1/balance_transactions/{id}
- "List all alerts?" -> GET /v1/billing/alerts
- "Create a alert?" -> POST /v1/billing/alerts
- "Get alert details?" -> GET /v1/billing/alerts/{id}
- "Create a activate?" -> POST /v1/billing/alerts/{id}/activate
- "Create a archive?" -> POST /v1/billing/alerts/{id}/archive
- "Create a deactivate?" -> POST /v1/billing/alerts/{id}/deactivate
- "List all credit_balance_summary?" -> GET /v1/billing/credit_balance_summary
- "List all credit_balance_transactions?" -> GET /v1/billing/credit_balance_transactions
- "Get credit_balance_transaction details?" -> GET /v1/billing/credit_balance_transactions/{id}
- "List all credit_grants?" -> GET /v1/billing/credit_grants
- "Create a credit_grant?" -> POST /v1/billing/credit_grants
- "Get credit_grant details?" -> GET /v1/billing/credit_grants/{id}
- "Create a expire?" -> POST /v1/billing/credit_grants/{id}/expire
- "Create a void?" -> POST /v1/billing/credit_grants/{id}/void
- "Create a meter_event_adjustment?" -> POST /v1/billing/meter_event_adjustments
- "Create a meter_event?" -> POST /v1/billing/meter_events
- "List all meters?" -> GET /v1/billing/meters
- "Create a meter?" -> POST /v1/billing/meters
- "Get meter details?" -> GET /v1/billing/meters/{id}
- "Create a deactivate?" -> POST /v1/billing/meters/{id}/deactivate
- "List all event_summaries?" -> GET /v1/billing/meters/{id}/event_summaries
- "Create a reactivate?" -> POST /v1/billing/meters/{id}/reactivate
- "List all configurations?" -> GET /v1/billing_portal/configurations
- "Create a configuration?" -> POST /v1/billing_portal/configurations
- "Get configuration details?" -> GET /v1/billing_portal/configurations/{configuration}
- "Create a session?" -> POST /v1/billing_portal/sessions
- "List all charges?" -> GET /v1/charges
- "Create a charge?" -> POST /v1/charges
- "Search search?" -> GET /v1/charges/search
- "Get charge details?" -> GET /v1/charges/{charge}
- "Create a capture?" -> POST /v1/charges/{charge}/capture
- "List all dispute?" -> GET /v1/charges/{charge}/dispute
- "Create a dispute?" -> POST /v1/charges/{charge}/dispute
- "Create a close?" -> POST /v1/charges/{charge}/dispute/close
- "Create a refund?" -> POST /v1/charges/{charge}/refund
- "List all refunds?" -> GET /v1/charges/{charge}/refunds
- "Create a refund?" -> POST /v1/charges/{charge}/refunds
- "Get refund details?" -> GET /v1/charges/{charge}/refunds/{refund}
- "List all sessions?" -> GET /v1/checkout/sessions
- "Create a session?" -> POST /v1/checkout/sessions
- "Get session details?" -> GET /v1/checkout/sessions/{session}
- "Create a expire?" -> POST /v1/checkout/sessions/{session}/expire
- "List all line_items?" -> GET /v1/checkout/sessions/{session}/line_items
- "List all orders?" -> GET /v1/climate/orders
- "Create a order?" -> POST /v1/climate/orders
- "Get order details?" -> GET /v1/climate/orders/{order}
- "Create a cancel?" -> POST /v1/climate/orders/{order}/cancel
- "List all products?" -> GET /v1/climate/products
- "Get product details?" -> GET /v1/climate/products/{product}
- "List all suppliers?" -> GET /v1/climate/suppliers
- "Get supplier details?" -> GET /v1/climate/suppliers/{supplier}
- "Get confirmation_token details?" -> GET /v1/confirmation_tokens/{confirmation_token}
- "List all country_specs?" -> GET /v1/country_specs
- "Get country_spec details?" -> GET /v1/country_specs/{country}
- "List all coupons?" -> GET /v1/coupons
- "Create a coupon?" -> POST /v1/coupons
- "Delete a coupon?" -> DELETE /v1/coupons/{coupon}
- "Get coupon details?" -> GET /v1/coupons/{coupon}
- "List all credit_notes?" -> GET /v1/credit_notes
- "Create a credit_note?" -> POST /v1/credit_notes
- "List all preview?" -> GET /v1/credit_notes/preview
- "List all lines?" -> GET /v1/credit_notes/preview/lines
- "List all lines?" -> GET /v1/credit_notes/{credit_note}/lines
- "Get credit_note details?" -> GET /v1/credit_notes/{id}
- "Create a void?" -> POST /v1/credit_notes/{id}/void
- "Create a customer_session?" -> POST /v1/customer_sessions
- "List all customers?" -> GET /v1/customers
- "Create a customer?" -> POST /v1/customers
- "Search search?" -> GET /v1/customers/search
- "Delete a customer?" -> DELETE /v1/customers/{customer}
- "Get customer details?" -> GET /v1/customers/{customer}
- "List all balance_transactions?" -> GET /v1/customers/{customer}/balance_transactions
- "Create a balance_transaction?" -> POST /v1/customers/{customer}/balance_transactions
- "Get balance_transaction details?" -> GET /v1/customers/{customer}/balance_transactions/{transaction}
- "List all bank_accounts?" -> GET /v1/customers/{customer}/bank_accounts
- "Create a bank_account?" -> POST /v1/customers/{customer}/bank_accounts
- "Delete a bank_account?" -> DELETE /v1/customers/{customer}/bank_accounts/{id}
- "Get bank_account details?" -> GET /v1/customers/{customer}/bank_accounts/{id}
- "Create a verify?" -> POST /v1/customers/{customer}/bank_accounts/{id}/verify
- "List all cards?" -> GET /v1/customers/{customer}/cards
- "Create a card?" -> POST /v1/customers/{customer}/cards
- "Delete a card?" -> DELETE /v1/customers/{customer}/cards/{id}
- "Get card details?" -> GET /v1/customers/{customer}/cards/{id}
- "List all cash_balance?" -> GET /v1/customers/{customer}/cash_balance
- "Create a cash_balance?" -> POST /v1/customers/{customer}/cash_balance
- "List all cash_balance_transactions?" -> GET /v1/customers/{customer}/cash_balance_transactions
- "Get cash_balance_transaction details?" -> GET /v1/customers/{customer}/cash_balance_transactions/{transaction}
- "List all discount?" -> GET /v1/customers/{customer}/discount
- "Create a funding_instruction?" -> POST /v1/customers/{customer}/funding_instructions
- "List all payment_methods?" -> GET /v1/customers/{customer}/payment_methods
- "Get payment_method details?" -> GET /v1/customers/{customer}/payment_methods/{payment_method}
- "List all sources?" -> GET /v1/customers/{customer}/sources
- "Create a source?" -> POST /v1/customers/{customer}/sources
- "Delete a source?" -> DELETE /v1/customers/{customer}/sources/{id}
- "Get source details?" -> GET /v1/customers/{customer}/sources/{id}
- "Create a verify?" -> POST /v1/customers/{customer}/sources/{id}/verify
- "List all subscriptions?" -> GET /v1/customers/{customer}/subscriptions
- "Create a subscription?" -> POST /v1/customers/{customer}/subscriptions
- "Delete a subscription?" -> DELETE /v1/customers/{customer}/subscriptions/{subscription_exposed_id}
- "Get subscription details?" -> GET /v1/customers/{customer}/subscriptions/{subscription_exposed_id}
- "List all discount?" -> GET /v1/customers/{customer}/subscriptions/{subscription_exposed_id}/discount
- "List all tax_ids?" -> GET /v1/customers/{customer}/tax_ids
- "Create a tax_id?" -> POST /v1/customers/{customer}/tax_ids
- "Delete a tax_id?" -> DELETE /v1/customers/{customer}/tax_ids/{id}
- "Get tax_id details?" -> GET /v1/customers/{customer}/tax_ids/{id}
- "List all disputes?" -> GET /v1/disputes
- "Get dispute details?" -> GET /v1/disputes/{dispute}
- "Create a close?" -> POST /v1/disputes/{dispute}/close
- "List all active_entitlements?" -> GET /v1/entitlements/active_entitlements
- "Get active_entitlement details?" -> GET /v1/entitlements/active_entitlements/{id}
- "List all features?" -> GET /v1/entitlements/features
- "Create a feature?" -> POST /v1/entitlements/features
- "Get feature details?" -> GET /v1/entitlements/features/{id}
- "Create a ephemeral_key?" -> POST /v1/ephemeral_keys
- "Delete a ephemeral_key?" -> DELETE /v1/ephemeral_keys/{key}
- "List all events?" -> GET /v1/events
- "Get event details?" -> GET /v1/events/{id}
- "List all exchange_rates?" -> GET /v1/exchange_rates
- "Get exchange_rate details?" -> GET /v1/exchange_rates/{rate_id}
- "List all file_links?" -> GET /v1/file_links
- "Create a file_link?" -> POST /v1/file_links
- "Get file_link details?" -> GET /v1/file_links/{link}
- "List all files?" -> GET /v1/files
- "Create a file?" -> POST /v1/files
- "Get file details?" -> GET /v1/files/{file}
- "List all accounts?" -> GET /v1/financial_connections/accounts
- "Get account details?" -> GET /v1/financial_connections/accounts/{account}
- "Create a disconnect?" -> POST /v1/financial_connections/accounts/{account}/disconnect
- "List all owners?" -> GET /v1/financial_connections/accounts/{account}/owners
- "Create a refresh?" -> POST /v1/financial_connections/accounts/{account}/refresh
- "Create a subscribe?" -> POST /v1/financial_connections/accounts/{account}/subscribe
- "Create a unsubscribe?" -> POST /v1/financial_connections/accounts/{account}/unsubscribe
- "Create a session?" -> POST /v1/financial_connections/sessions
- "Get session details?" -> GET /v1/financial_connections/sessions/{session}
- "List all transactions?" -> GET /v1/financial_connections/transactions
- "Get transaction details?" -> GET /v1/financial_connections/transactions/{transaction}
- "List all requests?" -> GET /v1/forwarding/requests
- "Create a request?" -> POST /v1/forwarding/requests
- "Get request details?" -> GET /v1/forwarding/requests/{id}
- "List all verification_reports?" -> GET /v1/identity/verification_reports
- "Get verification_report details?" -> GET /v1/identity/verification_reports/{report}
- "List all verification_sessions?" -> GET /v1/identity/verification_sessions
- "Create a verification_session?" -> POST /v1/identity/verification_sessions
- "Get verification_session details?" -> GET /v1/identity/verification_sessions/{session}
- "Create a cancel?" -> POST /v1/identity/verification_sessions/{session}/cancel
- "Create a redact?" -> POST /v1/identity/verification_sessions/{session}/redact
- "List all invoice_payments?" -> GET /v1/invoice_payments
- "Get invoice_payment details?" -> GET /v1/invoice_payments/{invoice_payment}
- "List all invoice_rendering_templates?" -> GET /v1/invoice_rendering_templates
- "Get invoice_rendering_template details?" -> GET /v1/invoice_rendering_templates/{template}
- "Create a archive?" -> POST /v1/invoice_rendering_templates/{template}/archive
- "Create a unarchive?" -> POST /v1/invoice_rendering_templates/{template}/unarchive
- "List all invoiceitems?" -> GET /v1/invoiceitems
- "Create a invoiceitem?" -> POST /v1/invoiceitems
- "Delete a invoiceitem?" -> DELETE /v1/invoiceitems/{invoiceitem}
- "Get invoiceitem details?" -> GET /v1/invoiceitems/{invoiceitem}
- "List all invoices?" -> GET /v1/invoices
- "Create a invoice?" -> POST /v1/invoices
- "Create a create_preview?" -> POST /v1/invoices/create_preview
- "Search search?" -> GET /v1/invoices/search
- "Delete a invoice?" -> DELETE /v1/invoices/{invoice}
- "Get invoice details?" -> GET /v1/invoices/{invoice}
- "Create a add_line?" -> POST /v1/invoices/{invoice}/add_lines
- "Create a attach_payment?" -> POST /v1/invoices/{invoice}/attach_payment
- "Create a finalize?" -> POST /v1/invoices/{invoice}/finalize
- "List all lines?" -> GET /v1/invoices/{invoice}/lines
- "Create a mark_uncollectible?" -> POST /v1/invoices/{invoice}/mark_uncollectible
- "Create a pay?" -> POST /v1/invoices/{invoice}/pay
- "Create a remove_line?" -> POST /v1/invoices/{invoice}/remove_lines
- "Create a send?" -> POST /v1/invoices/{invoice}/send
- "Create a update_line?" -> POST /v1/invoices/{invoice}/update_lines
- "Create a void?" -> POST /v1/invoices/{invoice}/void
- "List all authorizations?" -> GET /v1/issuing/authorizations
- "Get authorization details?" -> GET /v1/issuing/authorizations/{authorization}
- "Create a approve?" -> POST /v1/issuing/authorizations/{authorization}/approve
- "Create a decline?" -> POST /v1/issuing/authorizations/{authorization}/decline
- "List all cardholders?" -> GET /v1/issuing/cardholders
- "Create a cardholder?" -> POST /v1/issuing/cardholders
- "Get cardholder details?" -> GET /v1/issuing/cardholders/{cardholder}
- "List all cards?" -> GET /v1/issuing/cards
- "Create a card?" -> POST /v1/issuing/cards
- "Get card details?" -> GET /v1/issuing/cards/{card}
- "List all disputes?" -> GET /v1/issuing/disputes
- "Create a dispute?" -> POST /v1/issuing/disputes
- "Get dispute details?" -> GET /v1/issuing/disputes/{dispute}
- "Create a submit?" -> POST /v1/issuing/disputes/{dispute}/submit
- "List all personalization_designs?" -> GET /v1/issuing/personalization_designs
- "Create a personalization_design?" -> POST /v1/issuing/personalization_designs
- "Get personalization_design details?" -> GET /v1/issuing/personalization_designs/{personalization_design}
- "List all physical_bundles?" -> GET /v1/issuing/physical_bundles
- "Get physical_bundle details?" -> GET /v1/issuing/physical_bundles/{physical_bundle}
- "Get settlement details?" -> GET /v1/issuing/settlements/{settlement}
- "List all tokens?" -> GET /v1/issuing/tokens
- "Get token details?" -> GET /v1/issuing/tokens/{token}
- "List all transactions?" -> GET /v1/issuing/transactions
- "Get transaction details?" -> GET /v1/issuing/transactions/{transaction}
- "Create a link_account_session?" -> POST /v1/link_account_sessions
- "Get link_account_session details?" -> GET /v1/link_account_sessions/{session}
- "List all linked_accounts?" -> GET /v1/linked_accounts
- "Get linked_account details?" -> GET /v1/linked_accounts/{account}
- "Create a disconnect?" -> POST /v1/linked_accounts/{account}/disconnect
- "List all owners?" -> GET /v1/linked_accounts/{account}/owners
- "Create a refresh?" -> POST /v1/linked_accounts/{account}/refresh
- "Get mandate details?" -> GET /v1/mandates/{mandate}
- "List all payment_attempt_records?" -> GET /v1/payment_attempt_records
- "Get payment_attempt_record details?" -> GET /v1/payment_attempt_records/{id}
- "List all payment_intents?" -> GET /v1/payment_intents
- "Create a payment_intent?" -> POST /v1/payment_intents
- "Search search?" -> GET /v1/payment_intents/search
- "Get payment_intent details?" -> GET /v1/payment_intents/{intent}
- "List all amount_details_line_items?" -> GET /v1/payment_intents/{intent}/amount_details_line_items
- "Create a apply_customer_balance?" -> POST /v1/payment_intents/{intent}/apply_customer_balance
- "Create a cancel?" -> POST /v1/payment_intents/{intent}/cancel
- "Create a capture?" -> POST /v1/payment_intents/{intent}/capture
- "Create a confirm?" -> POST /v1/payment_intents/{intent}/confirm
- "Create a increment_authorization?" -> POST /v1/payment_intents/{intent}/increment_authorization
- "Create a verify_microdeposit?" -> POST /v1/payment_intents/{intent}/verify_microdeposits
- "List all payment_links?" -> GET /v1/payment_links
- "Create a payment_link?" -> POST /v1/payment_links
- "Get payment_link details?" -> GET /v1/payment_links/{payment_link}
- "List all line_items?" -> GET /v1/payment_links/{payment_link}/line_items
- "List all payment_method_configurations?" -> GET /v1/payment_method_configurations
- "Create a payment_method_configuration?" -> POST /v1/payment_method_configurations
- "Get payment_method_configuration details?" -> GET /v1/payment_method_configurations/{configuration}
- "List all payment_method_domains?" -> GET /v1/payment_method_domains
- "Create a payment_method_domain?" -> POST /v1/payment_method_domains
- "Get payment_method_domain details?" -> GET /v1/payment_method_domains/{payment_method_domain}
- "Create a validate?" -> POST /v1/payment_method_domains/{payment_method_domain}/validate
- "List all payment_methods?" -> GET /v1/payment_methods
- "Create a payment_method?" -> POST /v1/payment_methods
- "Get payment_method details?" -> GET /v1/payment_methods/{payment_method}
- "Create a attach?" -> POST /v1/payment_methods/{payment_method}/attach
- "Create a detach?" -> POST /v1/payment_methods/{payment_method}/detach
- "Create a report_payment?" -> POST /v1/payment_records/report_payment
- "Get payment_record details?" -> GET /v1/payment_records/{id}
- "Create a report_payment_attempt?" -> POST /v1/payment_records/{id}/report_payment_attempt
- "Create a report_payment_attempt_canceled?" -> POST /v1/payment_records/{id}/report_payment_attempt_canceled
- "Create a report_payment_attempt_failed?" -> POST /v1/payment_records/{id}/report_payment_attempt_failed
- "Create a report_payment_attempt_guaranteed?" -> POST /v1/payment_records/{id}/report_payment_attempt_guaranteed
- "Create a report_payment_attempt_informational?" -> POST /v1/payment_records/{id}/report_payment_attempt_informational
- "Create a report_refund?" -> POST /v1/payment_records/{id}/report_refund
- "List all payouts?" -> GET /v1/payouts
- "Create a payout?" -> POST /v1/payouts
- "Get payout details?" -> GET /v1/payouts/{payout}
- "Create a cancel?" -> POST /v1/payouts/{payout}/cancel
- "Create a reverse?" -> POST /v1/payouts/{payout}/reverse
- "List all plans?" -> GET /v1/plans
- "Create a plan?" -> POST /v1/plans
- "Delete a plan?" -> DELETE /v1/plans/{plan}
- "Get plan details?" -> GET /v1/plans/{plan}
- "List all prices?" -> GET /v1/prices
- "Create a price?" -> POST /v1/prices
- "Search search?" -> GET /v1/prices/search
- "Get price details?" -> GET /v1/prices/{price}
- "List all products?" -> GET /v1/products
- "Create a product?" -> POST /v1/products
- "Search search?" -> GET /v1/products/search
- "Delete a product?" -> DELETE /v1/products/{id}
- "Get product details?" -> GET /v1/products/{id}
- "List all features?" -> GET /v1/products/{product}/features
- "Create a feature?" -> POST /v1/products/{product}/features
- "Delete a feature?" -> DELETE /v1/products/{product}/features/{id}
- "Get feature details?" -> GET /v1/products/{product}/features/{id}
- "List all promotion_codes?" -> GET /v1/promotion_codes
- "Create a promotion_code?" -> POST /v1/promotion_codes
- "Get promotion_code details?" -> GET /v1/promotion_codes/{promotion_code}
- "List all quotes?" -> GET /v1/quotes
- "Create a quote?" -> POST /v1/quotes
- "Get quote details?" -> GET /v1/quotes/{quote}
- "Create a accept?" -> POST /v1/quotes/{quote}/accept
- "Create a cancel?" -> POST /v1/quotes/{quote}/cancel
- "List all computed_upfront_line_items?" -> GET /v1/quotes/{quote}/computed_upfront_line_items
- "Create a finalize?" -> POST /v1/quotes/{quote}/finalize
- "List all line_items?" -> GET /v1/quotes/{quote}/line_items
- "List all pdf?" -> GET /v1/quotes/{quote}/pdf
- "List all early_fraud_warnings?" -> GET /v1/radar/early_fraud_warnings
- "Get early_fraud_warning details?" -> GET /v1/radar/early_fraud_warnings/{early_fraud_warning}
- "Create a payment_evaluation?" -> POST /v1/radar/payment_evaluations
- "List all value_list_items?" -> GET /v1/radar/value_list_items
- "Create a value_list_item?" -> POST /v1/radar/value_list_items
- "Delete a value_list_item?" -> DELETE /v1/radar/value_list_items/{item}
- "Get value_list_item details?" -> GET /v1/radar/value_list_items/{item}
- "List all value_lists?" -> GET /v1/radar/value_lists
- "Create a value_list?" -> POST /v1/radar/value_lists
- "Delete a value_list?" -> DELETE /v1/radar/value_lists/{value_list}
- "Get value_list details?" -> GET /v1/radar/value_lists/{value_list}
- "List all refunds?" -> GET /v1/refunds
- "Create a refund?" -> POST /v1/refunds
- "Get refund details?" -> GET /v1/refunds/{refund}
- "Create a cancel?" -> POST /v1/refunds/{refund}/cancel
- "List all report_runs?" -> GET /v1/reporting/report_runs
- "Create a report_run?" -> POST /v1/reporting/report_runs
- "Get report_run details?" -> GET /v1/reporting/report_runs/{report_run}
- "List all report_types?" -> GET /v1/reporting/report_types
- "Get report_type details?" -> GET /v1/reporting/report_types/{report_type}
- "List all reviews?" -> GET /v1/reviews
- "Get review details?" -> GET /v1/reviews/{review}
- "Create a approve?" -> POST /v1/reviews/{review}/approve
- "List all setup_attempts?" -> GET /v1/setup_attempts
- "List all setup_intents?" -> GET /v1/setup_intents
- "Create a setup_intent?" -> POST /v1/setup_intents
- "Get setup_intent details?" -> GET /v1/setup_intents/{intent}
- "Create a cancel?" -> POST /v1/setup_intents/{intent}/cancel
- "Create a confirm?" -> POST /v1/setup_intents/{intent}/confirm
- "Create a verify_microdeposit?" -> POST /v1/setup_intents/{intent}/verify_microdeposits
- "List all shipping_rates?" -> GET /v1/shipping_rates
- "Create a shipping_rate?" -> POST /v1/shipping_rates
- "Get shipping_rate details?" -> GET /v1/shipping_rates/{shipping_rate_token}
- "List all scheduled_query_runs?" -> GET /v1/sigma/scheduled_query_runs
- "Get scheduled_query_run details?" -> GET /v1/sigma/scheduled_query_runs/{scheduled_query_run}
- "Create a source?" -> POST /v1/sources
- "Get source details?" -> GET /v1/sources/{source}
- "Get mandate_notification details?" -> GET /v1/sources/{source}/mandate_notifications/{mandate_notification}
- "List all source_transactions?" -> GET /v1/sources/{source}/source_transactions
- "Get source_transaction details?" -> GET /v1/sources/{source}/source_transactions/{source_transaction}
- "Create a verify?" -> POST /v1/sources/{source}/verify
- "List all subscription_items?" -> GET /v1/subscription_items
- "Create a subscription_item?" -> POST /v1/subscription_items
- "Delete a subscription_item?" -> DELETE /v1/subscription_items/{item}
- "Get subscription_item details?" -> GET /v1/subscription_items/{item}
- "List all subscription_schedules?" -> GET /v1/subscription_schedules
- "Create a subscription_schedule?" -> POST /v1/subscription_schedules
- "Get subscription_schedule details?" -> GET /v1/subscription_schedules/{schedule}
- "Create a cancel?" -> POST /v1/subscription_schedules/{schedule}/cancel
- "Create a release?" -> POST /v1/subscription_schedules/{schedule}/release
- "List all subscriptions?" -> GET /v1/subscriptions
- "Create a subscription?" -> POST /v1/subscriptions
- "Search search?" -> GET /v1/subscriptions/search
- "Delete a subscription?" -> DELETE /v1/subscriptions/{subscription_exposed_id}
- "Get subscription details?" -> GET /v1/subscriptions/{subscription_exposed_id}
- "Create a migrate?" -> POST /v1/subscriptions/{subscription}/migrate
- "Create a resume?" -> POST /v1/subscriptions/{subscription}/resume
- "List all find?" -> GET /v1/tax/associations/find
- "Create a calculation?" -> POST /v1/tax/calculations
- "Get calculation details?" -> GET /v1/tax/calculations/{calculation}
- "List all line_items?" -> GET /v1/tax/calculations/{calculation}/line_items
- "List all registrations?" -> GET /v1/tax/registrations
- "Create a registration?" -> POST /v1/tax/registrations
- "Get registration details?" -> GET /v1/tax/registrations/{id}
- "List all settings?" -> GET /v1/tax/settings
- "Create a setting?" -> POST /v1/tax/settings
- "Create a create_from_calculation?" -> POST /v1/tax/transactions/create_from_calculation
- "Create a create_reversal?" -> POST /v1/tax/transactions/create_reversal
- "Get transaction details?" -> GET /v1/tax/transactions/{transaction}
- "List all line_items?" -> GET /v1/tax/transactions/{transaction}/line_items
- "List all tax_codes?" -> GET /v1/tax_codes
- "Get tax_code details?" -> GET /v1/tax_codes/{id}
- "List all tax_ids?" -> GET /v1/tax_ids
- "Create a tax_id?" -> POST /v1/tax_ids
- "Delete a tax_id?" -> DELETE /v1/tax_ids/{id}
- "Get tax_id details?" -> GET /v1/tax_ids/{id}
- "List all tax_rates?" -> GET /v1/tax_rates
- "Create a tax_rate?" -> POST /v1/tax_rates
- "Get tax_rate details?" -> GET /v1/tax_rates/{tax_rate}
- "List all configurations?" -> GET /v1/terminal/configurations
- "Create a configuration?" -> POST /v1/terminal/configurations
- "Delete a configuration?" -> DELETE /v1/terminal/configurations/{configuration}
- "Get configuration details?" -> GET /v1/terminal/configurations/{configuration}
- "Create a connection_token?" -> POST /v1/terminal/connection_tokens
- "List all locations?" -> GET /v1/terminal/locations
- "Create a location?" -> POST /v1/terminal/locations
- "Delete a location?" -> DELETE /v1/terminal/locations/{location}
- "Get location details?" -> GET /v1/terminal/locations/{location}
- "Create a onboarding_link?" -> POST /v1/terminal/onboarding_links
- "List all readers?" -> GET /v1/terminal/readers
- "Create a reader?" -> POST /v1/terminal/readers
- "Delete a reader?" -> DELETE /v1/terminal/readers/{reader}
- "Get reader details?" -> GET /v1/terminal/readers/{reader}
- "Create a cancel_action?" -> POST /v1/terminal/readers/{reader}/cancel_action
- "Create a collect_input?" -> POST /v1/terminal/readers/{reader}/collect_inputs
- "Create a collect_payment_method?" -> POST /v1/terminal/readers/{reader}/collect_payment_method
- "Create a confirm_payment_intent?" -> POST /v1/terminal/readers/{reader}/confirm_payment_intent
- "Create a process_payment_intent?" -> POST /v1/terminal/readers/{reader}/process_payment_intent
- "Create a process_setup_intent?" -> POST /v1/terminal/readers/{reader}/process_setup_intent
- "Create a refund_payment?" -> POST /v1/terminal/readers/{reader}/refund_payment
- "Create a set_reader_display?" -> POST /v1/terminal/readers/{reader}/set_reader_display
- "Create a refund?" -> POST /v1/terminal/refunds
- "Create a confirmation_token?" -> POST /v1/test_helpers/confirmation_tokens
- "Create a fund_cash_balance?" -> POST /v1/test_helpers/customers/{customer}/fund_cash_balance
- "Create a authorization?" -> POST /v1/test_helpers/issuing/authorizations
- "Create a capture?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/capture
- "Create a expire?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/expire
- "Create a finalize_amount?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/finalize_amount
- "Create a respond?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/fraud_challenges/respond
- "Create a increment?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/increment
- "Create a reverse?" -> POST /v1/test_helpers/issuing/authorizations/{authorization}/reverse
- "Create a deliver?" -> POST /v1/test_helpers/issuing/cards/{card}/shipping/deliver
- "Create a fail?" -> POST /v1/test_helpers/issuing/cards/{card}/shipping/fail
- "Create a return?" -> POST /v1/test_helpers/issuing/cards/{card}/shipping/return
- "Create a ship?" -> POST /v1/test_helpers/issuing/cards/{card}/shipping/ship
- "Create a submit?" -> POST /v1/test_helpers/issuing/cards/{card}/shipping/submit
- "Create a activate?" -> POST /v1/test_helpers/issuing/personalization_designs/{personalization_design}/activate
- "Create a deactivate?" -> POST /v1/test_helpers/issuing/personalization_designs/{personalization_design}/deactivate
- "Create a reject?" -> POST /v1/test_helpers/issuing/personalization_designs/{personalization_design}/reject
- "Create a settlement?" -> POST /v1/test_helpers/issuing/settlements
- "Create a complete?" -> POST /v1/test_helpers/issuing/settlements/{settlement}/complete
- "Create a create_force_capture?" -> POST /v1/test_helpers/issuing/transactions/create_force_capture
- "Create a create_unlinked_refund?" -> POST /v1/test_helpers/issuing/transactions/create_unlinked_refund
- "Create a refund?" -> POST /v1/test_helpers/issuing/transactions/{transaction}/refund
- "Create a expire?" -> POST /v1/test_helpers/refunds/{refund}/expire
- "Create a present_payment_method?" -> POST /v1/test_helpers/terminal/readers/{reader}/present_payment_method
- "Create a succeed_input_collection?" -> POST /v1/test_helpers/terminal/readers/{reader}/succeed_input_collection
- "Create a timeout_input_collection?" -> POST /v1/test_helpers/terminal/readers/{reader}/timeout_input_collection
- "List all test_clocks?" -> GET /v1/test_helpers/test_clocks
- "Create a test_clock?" -> POST /v1/test_helpers/test_clocks
- "Delete a test_clock?" -> DELETE /v1/test_helpers/test_clocks/{test_clock}
- "Get test_clock details?" -> GET /v1/test_helpers/test_clocks/{test_clock}
- "Create a advance?" -> POST /v1/test_helpers/test_clocks/{test_clock}/advance
- "Create a fail?" -> POST /v1/test_helpers/treasury/inbound_transfers/{id}/fail
- "Create a return?" -> POST /v1/test_helpers/treasury/inbound_transfers/{id}/return
- "Create a succeed?" -> POST /v1/test_helpers/treasury/inbound_transfers/{id}/succeed
- "Create a fail?" -> POST /v1/test_helpers/treasury/outbound_payments/{id}/fail
- "Create a post?" -> POST /v1/test_helpers/treasury/outbound_payments/{id}/post
- "Create a return?" -> POST /v1/test_helpers/treasury/outbound_payments/{id}/return
- "Create a fail?" -> POST /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/fail
- "Create a post?" -> POST /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/post
- "Create a return?" -> POST /v1/test_helpers/treasury/outbound_transfers/{outbound_transfer}/return
- "Create a received_credit?" -> POST /v1/test_helpers/treasury/received_credits
- "Create a received_debit?" -> POST /v1/test_helpers/treasury/received_debits
- "Create a token?" -> POST /v1/tokens
- "Get token details?" -> GET /v1/tokens/{token}
- "List all topups?" -> GET /v1/topups
- "Create a topup?" -> POST /v1/topups
- "Get topup details?" -> GET /v1/topups/{topup}
- "Create a cancel?" -> POST /v1/topups/{topup}/cancel
- "List all transfers?" -> GET /v1/transfers
- "Create a transfer?" -> POST /v1/transfers
- "List all reversals?" -> GET /v1/transfers/{id}/reversals
- "Create a reversal?" -> POST /v1/transfers/{id}/reversals
- "Get transfer details?" -> GET /v1/transfers/{transfer}
- "Get reversal details?" -> GET /v1/transfers/{transfer}/reversals/{id}
- "List all credit_reversals?" -> GET /v1/treasury/credit_reversals
- "Create a credit_reversal?" -> POST /v1/treasury/credit_reversals
- "Get credit_reversal details?" -> GET /v1/treasury/credit_reversals/{credit_reversal}
- "List all debit_reversals?" -> GET /v1/treasury/debit_reversals
- "Create a debit_reversal?" -> POST /v1/treasury/debit_reversals
- "Get debit_reversal details?" -> GET /v1/treasury/debit_reversals/{debit_reversal}
- "List all financial_accounts?" -> GET /v1/treasury/financial_accounts
- "Create a financial_account?" -> POST /v1/treasury/financial_accounts
- "Get financial_account details?" -> GET /v1/treasury/financial_accounts/{financial_account}
- "Create a close?" -> POST /v1/treasury/financial_accounts/{financial_account}/close
- "List all features?" -> GET /v1/treasury/financial_accounts/{financial_account}/features
- "Create a feature?" -> POST /v1/treasury/financial_accounts/{financial_account}/features
- "List all inbound_transfers?" -> GET /v1/treasury/inbound_transfers
- "Create a inbound_transfer?" -> POST /v1/treasury/inbound_transfers
- "Get inbound_transfer details?" -> GET /v1/treasury/inbound_transfers/{id}
- "Create a cancel?" -> POST /v1/treasury/inbound_transfers/{inbound_transfer}/cancel
- "List all outbound_payments?" -> GET /v1/treasury/outbound_payments
- "Create a outbound_payment?" -> POST /v1/treasury/outbound_payments
- "Get outbound_payment details?" -> GET /v1/treasury/outbound_payments/{id}
- "Create a cancel?" -> POST /v1/treasury/outbound_payments/{id}/cancel
- "List all outbound_transfers?" -> GET /v1/treasury/outbound_transfers
- "Create a outbound_transfer?" -> POST /v1/treasury/outbound_transfers
- "Get outbound_transfer details?" -> GET /v1/treasury/outbound_transfers/{outbound_transfer}
- "Create a cancel?" -> POST /v1/treasury/outbound_transfers/{outbound_transfer}/cancel
- "List all received_credits?" -> GET /v1/treasury/received_credits
- "Get received_credit details?" -> GET /v1/treasury/received_credits/{id}
- "List all received_debits?" -> GET /v1/treasury/received_debits
- "Get received_debit details?" -> GET /v1/treasury/received_debits/{id}
- "List all transaction_entries?" -> GET /v1/treasury/transaction_entries
- "Get transaction_entry details?" -> GET /v1/treasury/transaction_entries/{id}
- "List all transactions?" -> GET /v1/treasury/transactions
- "Get transaction details?" -> GET /v1/treasury/transactions/{id}
- "List all webhook_endpoints?" -> GET /v1/webhook_endpoints
- "Create a webhook_endpoint?" -> POST /v1/webhook_endpoints
- "Delete a webhook_endpoint?" -> DELETE /v1/webhook_endpoints/{webhook_endpoint}
- "Get webhook_endpoint details?" -> GET /v1/webhook_endpoints/{webhook_endpoint}
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- List endpoints may support pagination; check for limit, offset, or cursor params
- Create/update endpoints typically return the created/updated object

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
