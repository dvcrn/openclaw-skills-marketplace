# Validation Rules

## Arithmetic Checks

1. **Line items sum** — sum of non-shipping lineTotal must equal netTotal (±0.02 tolerance)
2. **VAT calculation** — vatBreakdown grouped by rate with taxable base per band
3. **Gross = Net + Shipping + VAT** — grossTotal must equal netTotal + shipping + vatTotal (±0.02)
4. **Line total = qty × price** — per-line check with tolerance

## Shipping Detection

Lines matching these keywords are auto-tagged `type: "shipping"` and promoted to `totals.shipping`:
shipping, freight, delivery, carriage, transport, postage, handling, express post, courier, dispatch, p&p, packing, shipment

Net total is adjusted to exclude shipping (items only). Shipping's VAT rate is tracked separately in `totals.shippingVatRate`.

## Multi-Rate VAT

vatBreakdown groups all items + shipping by VAT rate:
```json
[
  { "rate": 0, "taxableBase": 30.00, "amount": 0.00 },
  { "rate": 5, "taxableBase": 50.00, "amount": 2.50 },
  { "rate": 20, "taxableBase": 100.00, "amount": 20.00 }
]
```

## Document Classification (9 types)

| Type | Accept: strict | Accept: relaxed |
|---|---|---|
| invoice | ✅ | ✅ |
| credit-note | ✅ | ✅ |
| receipt | ❌ | ✅ |
| proforma | ❌ | ✅ |
| purchase-order | ❌ | ❌ |
| delivery-note | ❌ | ❌ |
| confirmation | ❌ | ❌ |
| statement | ❌ | ❌ |
| other-financial | ❌ | ❌ |
| not-financial | ❌ | ❌ |

`accept: any` extracts from everything, just classifies.

## Business Rules (15 checks)

### Critical (errors)
1. Missing invoice number
2. Missing supplier name
3. Missing currency
4. Invalid date formats
5. Gross total mismatch (>1% deviation)

### Important (warnings)
6. Missing buyer name
7. Missing invoice date
8. Missing due date
9. Missing payment terms
10. No line items extracted
11. Suspicious invoice number (too short, generic like "001")
12. Receipt signals detected (keywords: "receipt", "cash register", thermal paper indicators)
13. Missing bank/payment details
14. Missing VAT number (when VAT amounts present)
15. Low confidence score (<0.5)

## Quality Score

Score = presentFields / totalChecked (9 key fields):
- invoiceNumber, invoiceDate, currency, supplierName, buyerName, netTotal, vatTotal, grossTotal, lineItems(>0)

Ratings: good (≥0.7), partial (≥0.3), poor (<0.3)

## Locale Number Parsing

Automatic detection and normalisation:
- US/UK: 1,234.56
- European: 1.234,56
- French: 1 234,56
- Russian: 4 631-32
- Indian: 1,23,456.78
- Chinese: ¥12,345.67

All normalised to standard decimal (1234.56) before arithmetic validation.
