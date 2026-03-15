/**
 * CSV Output Formatter
 *
 * Zoho-style flat format: one row per line item, header fields repeated.
 * Column order: header → line item → totals → validation → metadata
 */

const DELIMITER = ',';

function esc(val) {
  if (val === null || val === undefined) return '';
  const str = String(val);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

const COLUMNS = [
  // ── Header fields ──
  'Customer Name',        // buyerName
  'Invoice Number',       // invoiceNumber
  'LineItem ID',          // line item index
  'PurchaseOrder',        // PO ref
  'Invoice Date',         // invoiceDate
  'Due Date',             // dueDate
  'Payment Terms',        // paymentTerms
  'Invoice Status',       // overallStatus
  'Currency Code',        // currency
  'Supplier Name',        // supplierName
  'Supplier Address',     // supplierAddress
  'Supplier VAT Number',  // supplierVatNumber
  'Buyer Address',        // buyerAddress
  'Buyer VAT Number',     // buyerVatNumber
  'Payment Reference',    // paymentReference
  'IBAN',                 // bankDetails.iban
  'BIC',                  // bankDetails.bic
  'Account Number',       // bankDetails.accountNumber
  'Sort Code',            // bankDetails.sortCode
  // ── Line item fields ──
  'Is Inclusive Tax',      // (always false for now)
  'Item Name',            // description
  'SKU',                  // sku
  'Item Desc',            // description (full)
  'Quantity',             // quantity
  'Usage unit',           // unitOfMeasure
  'Item Price',           // unitPrice
  'Item Tax',             // tax type label
  'Item Tax %',           // vatRate
  'Item Tax Amount',      // computed VAT amount
  'Line Total',           // lineTotal
  'Discount',             // discount
  // ── Totals ──
  'Net Total',            // netTotal
  'VAT Total',            // vatTotal
  'Gross Total',          // grossTotal
  // ── Validation / metadata ──
  'Arithmetic Valid',     // Y/N
  'Confidence',           // 0-1
  'Language',             // ISO 639-1
  'Provider',             // e.g. claude
  'Document Type',        // invoice, credit-note, etc.
  'Quality Rating',       // good/partial/poor
  'Notes',                // notes field
  'Terms & Conditions',   // paymentTerms
];

function buildRow(invoice, lineItem, lineIdx) {
  const h = invoice.header;
  const t = invoice.totals;
  const m = invoice.metadata;
  const v = invoice.validation;
  const ex = invoice.exceptions;
  const li = lineItem || {};

  // Find PO reference
  const po = (invoice.referencedDocuments || []).find(d => d.type === 'PO');

  // Compute line VAT amount
  const lineVatAmount = (li.lineTotal && li.vatRate)
    ? +(li.lineTotal * li.vatRate / 100).toFixed(2)
    : '';

  return [
    h.buyerName,
    h.invoiceNumber,
    lineIdx,
    po ? po.reference : '',
    h.invoiceDate,
    h.dueDate,
    h.paymentTerms,
    ex.overallStatus,
    h.currency,
    h.supplierName,
    h.supplierAddress,
    h.supplierVatNumber,
    h.buyerAddress,
    h.buyerVatNumber,
    h.paymentReference,
    h.bankDetails?.iban,
    h.bankDetails?.bic,
    h.bankDetails?.accountNumber,
    h.bankDetails?.sortCode,
    // Line item
    'False',
    li.description,
    li.sku,
    li.description,
    li.quantity,
    li.unitOfMeasure,
    li.unitPrice,
    li.vatRate ? 'Standard Rate' : '',
    li.vatRate,
    lineVatAmount,
    li.lineTotal,
    li.discount,
    // Totals
    t.netTotal,
    t.vatTotal,
    t.grossTotal,
    // Validation
    v.arithmeticValid ? 'Y' : 'N',
    m.confidence,
    m.language,
    m.provider,
    m.documentType || '',
    v.documentQuality?.rating || '',
    '', // notes
    h.paymentTerms,
  ].map(esc);
}

/**
 * Convert canonical invoice to CSV string.
 */
function toCSV(invoice, options = {}) {
  const delim = options.delimiter || DELIMITER;
  const rows = [COLUMNS.join(delim)];

  if (invoice.lineItems.length === 0) {
    rows.push(buildRow(invoice, null, '').join(delim));
  } else {
    invoice.lineItems.forEach((li, i) => {
      rows.push(buildRow(invoice, li, i + 1).join(delim));
    });
  }

  return rows.join('\n');
}

module.exports = { toCSV };
