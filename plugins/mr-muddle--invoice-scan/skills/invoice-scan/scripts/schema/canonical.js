/**
 * Canonical Invoice Schema
 * 
 * This is THE standard output format. Every provider adapter must
 * normalise to this schema. All output formats (JSON, CSV, Excel)
 * derive from this structure.
 * 
 * @version 1.0.0
 */

const SCHEMA_VERSION = '1.0.0';

/**
 * Returns a blank canonical invoice object.
 * Use as a template — fill in from provider adapters.
 */
function createBlankInvoice() {
  return {
    schemaVersion: SCHEMA_VERSION,

    header: {
      invoiceNumber: null,
      invoiceDate: null,           // YYYY-MM-DD
      dueDate: null,               // YYYY-MM-DD
      currency: null,              // ISO 4217 (e.g., "GBP")
      supplierName: null,
      supplierAddress: null,
      supplierVatNumber: null,
      buyerName: null,
      buyerAddress: null,
      buyerVatNumber: null,
      paymentTerms: null,
      paymentReference: null,
      bankDetails: {
        iban: null,
        bic: null,
        accountNumber: null,
        sortCode: null,
      },
    },

    referencedDocuments: [],
    // Each: { type: string, reference: string }
    // Types: "PO", "contract", "GRN", "inspection", "timesheet",
    //        "project", "proforma", "other"

    lineItems: [],
    // Each: {
    //   description: string,
    //   quantity: number,
    //   unitOfMeasure: string,
    //   unitPrice: number,
    //   lineTotal: number,
    //   vatRate: number,
    //   sku: string|null,
    //   discount: number|null,
    //   type: "item"|"shipping"|"charge",  // default "item"
    // }

    totals: {
      netTotal: null,              // line items only (excludes shipping)
      shipping: null,              // invoice-level shipping/freight/postage
      shippingVatRate: null,       // VAT rate applied to shipping (%)
      vatBreakdown: [],            // [{ rate: number, amount: number, taxableBase: number }]
      vatTotal: null,
      grossTotal: null,            // net + shipping + VAT
    },

    metadata: {
      confidence: null,            // 0.0–1.0 overall
      language: null,              // ISO 639-1
      pageCount: null,
      processingDurationMs: null,
      provider: null,              // which AI provider was used
      extractionTimestamp: null,   // ISO 8601 datetime
      documentType: null,          // "invoice", "credit-note", etc.
    },

    fields: [],
    // Per-field detail: {
    //   name: string,             // canonical field name (e.g., "header.invoiceNumber")
    //   value: any,
    //   confidence: number,       // 0.0–1.0
    //   boundingBox: { x, y, width, height, page } | null,
    //   extractionMethod: string, // "ocr", "icr", "stamp", "inferred"
    //   failureReason: string|null,
    // }

    validation: {
      arithmeticValid: null,
      errors: [],                  // [{ field: string, message: string }]
      warnings: [],                // [{ field: string, message: string }]
    },

    exceptions: {
      overallStatus: null,         // "success", "partial", "failed"
      failedFields: [],            // [{ name, reason, suggestion }]
      processingAttempts: 1,
    },
  };
}

/**
 * Validate that an object conforms to canonical schema.
 * Returns { valid: boolean, errors: string[] }
 */
function validateSchema(invoice) {
  const errors = [];

  if (!invoice.schemaVersion) errors.push('Missing schemaVersion');
  if (!invoice.header) errors.push('Missing header');
  if (!invoice.lineItems) errors.push('Missing lineItems');
  if (!Array.isArray(invoice.lineItems)) errors.push('lineItems must be an array');
  if (!invoice.totals) errors.push('Missing totals');
  if (!invoice.metadata) errors.push('Missing metadata');
  if (!invoice.validation) errors.push('Missing validation');

  // Header required fields (should be present even if null)
  if (invoice.header) {
    const requiredHeaderFields = ['invoiceNumber', 'invoiceDate', 'currency', 'supplierName'];
    for (const field of requiredHeaderFields) {
      if (invoice.header[field] === undefined) {
        errors.push(`Missing header.${field}`);
      }
    }
  }

  // Line items structure
  if (Array.isArray(invoice.lineItems)) {
    invoice.lineItems.forEach((item, i) => {
      if (item.description === undefined) errors.push(`lineItems[${i}]: missing description`);
      if (item.quantity === undefined) errors.push(`lineItems[${i}]: missing quantity`);
      if (item.unitPrice === undefined) errors.push(`lineItems[${i}]: missing unitPrice`);
      if (item.lineTotal === undefined) errors.push(`lineItems[${i}]: missing lineTotal`);
    });
  }

  return { valid: errors.length === 0, errors };
}

module.exports = { SCHEMA_VERSION, createBlankInvoice, validateSchema };
