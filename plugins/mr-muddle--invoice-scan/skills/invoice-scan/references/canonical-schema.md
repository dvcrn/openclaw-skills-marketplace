# Canonical Invoice Schema v1.0.0

Every scan produces this structure regardless of provider.

## Top-Level

```json
{
  "schemaVersion": "1.0.0",
  "header": {},
  "referencedDocuments": [],
  "lineItems": [],
  "totals": {},
  "metadata": {},
  "fields": [],
  "validation": {},
  "exceptions": {}
}
```

## header

| Field | Type | Notes |
|---|---|---|
| invoiceNumber | string | |
| invoiceDate | string | YYYY-MM-DD |
| dueDate | string | YYYY-MM-DD |
| currency | string | ISO 4217 |
| supplierName | string | |
| supplierAddress | string | |
| supplierVatNumber | string | |
| buyerName | string | |
| buyerAddress | string | |
| buyerVatNumber | string | |
| paymentTerms | string | |
| paymentReference | string | |
| bankDetails.iban | string | |
| bankDetails.bic | string | |
| bankDetails.accountNumber | string | |
| bankDetails.sortCode | string | |

## lineItems[]

| Field | Type |
|---|---|
| description | string |
| quantity | number |
| unitOfMeasure | string |
| unitPrice | number |
| lineTotal | number |
| vatRate | number | percentage |
| sku | string |
| discount | number |

## referencedDocuments[]

type: PO | contract | GRN | inspection | timesheet | project | proforma | other
reference: string

## totals

netTotal (items only, excludes shipping), shipping (invoice-level shipping/freight), shippingVatRate (% applied to shipping), vatBreakdown[{rate, amount, taxableBase}], vatTotal, grossTotal (net + shipping + VAT)

## metadata

confidence (0–1), language (ISO 639-1), pageCount, processingDurationMs, provider, extractionTimestamp (ISO 8601), documentType

## fields[]

Per-field: name, value, confidence, boundingBox ({x, y, width, height, page} or null), extractionMethod (ocr|icr|stamp|inferred), failureReason

## lineItems[].type

- `item` — regular line item (default)
- `shipping` — auto-detected shipping/freight/postage charge (promoted to totals.shipping)
- `charge` — other invoice-level charges (reserved for future use)

## validation

arithmeticValid (bool), errors[{field, message}], warnings[{field, message}], documentQuality: {score, presentFields, totalChecked, rating}

## exceptions

overallStatus: success | partial | failed | rejected
failedFields[], processingAttempts, rejectionReason
