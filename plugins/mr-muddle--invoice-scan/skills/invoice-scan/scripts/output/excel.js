/**
 * Excel (XLSX) Output Formatter
 *
 * Sheet 1 "Invoice": Zoho-style flat table — one row per line item,
 *   header fields at the top (repeated on every row).
 * Sheet 2 "Validation": arithmetic results, errors, warnings, field confidence.
 */

let XLSX;
try {
  XLSX = require('xlsx');
} catch (e) {
  XLSX = null;
}

const COLUMNS = [
  // ── Header fields ──
  'Customer Name',
  'Invoice Number',
  'LineItem ID',
  'PurchaseOrder',
  'Invoice Date',
  'Due Date',
  'Payment Terms',
  'Invoice Status',
  'Currency Code',
  'Supplier Name',
  'Supplier Address',
  'Supplier VAT Number',
  'Buyer Address',
  'Buyer VAT Number',
  'Payment Reference',
  'IBAN',
  'BIC',
  'Account Number',
  'Sort Code',
  // ── Line item fields ──
  'Is Inclusive Tax',
  'Item Name',
  'SKU',
  'Item Desc',
  'Quantity',
  'Usage unit',
  'Item Price',
  'Item Tax',
  'Item Tax %',
  'Item Tax Amount',
  'Line Total',
  'Discount',
  // ── Totals ──
  'Net Total',
  'VAT Total',
  'Gross Total',
  // ── Validation / metadata ──
  'Arithmetic Valid',
  'Confidence',
  'Language',
  'Provider',
  'Document Type',
  'Quality Rating',
];

function buildRow(invoice, li, lineIdx) {
  const h = invoice.header;
  const t = invoice.totals;
  const m = invoice.metadata;
  const v = invoice.validation;
  const ex = invoice.exceptions;
  li = li || {};

  const po = (invoice.referencedDocuments || []).find(d => d.type === 'PO');
  const lineVat = (li.lineTotal && li.vatRate)
    ? +(li.lineTotal * li.vatRate / 100).toFixed(2)
    : null;

  return [
    h.buyerName,
    h.invoiceNumber,
    lineIdx || null,
    po ? po.reference : null,
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
    // Line
    false,
    li.description || null,
    li.sku || null,
    li.description || null,
    li.quantity,
    li.unitOfMeasure || null,
    li.unitPrice,
    li.vatRate ? 'Standard Rate' : null,
    li.vatRate,
    lineVat,
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
    m.documentType || null,
    v.documentQuality?.rating || null,
  ];
}

function toExcel(invoice) {
  if (!XLSX) {
    throw new Error('xlsx package not installed. Run: npm install xlsx');
  }

  const wb = XLSX.utils.book_new();

  // ── Sheet 1: Invoice (flat, Zoho-style) ──
  const dataRows = [];
  if (invoice.lineItems.length === 0) {
    dataRows.push(buildRow(invoice, null, null));
  } else {
    invoice.lineItems.forEach((li, i) => {
      dataRows.push(buildRow(invoice, li, i + 1));
    });
  }

  const invoiceSheet = XLSX.utils.aoa_to_sheet([COLUMNS, ...dataRows]);

  // Auto-width columns
  invoiceSheet['!cols'] = COLUMNS.map((col, i) => {
    const maxLen = Math.max(
      col.length,
      ...dataRows.map(r => String(r[i] ?? '').length),
    );
    return { wch: Math.min(maxLen + 2, 50) };
  });

  XLSX.utils.book_append_sheet(wb, invoiceSheet, 'Invoice');

  // ── Sheet 2: Validation ──
  const valData = [
    ['Arithmetic Valid', invoice.validation.arithmeticValid ? 'YES' : 'NO'],
    ['Quality Score', invoice.validation.documentQuality?.score],
    ['Quality Rating', invoice.validation.documentQuality?.rating],
    ['', ''],
    ['Errors', ''],
  ];
  for (const err of invoice.validation.errors) {
    valData.push([err.field, err.message]);
  }
  if (invoice.validation.errors.length === 0) valData.push(['(none)', '']);

  valData.push(['', ''], ['Warnings', '']);
  for (const warn of invoice.validation.warnings) {
    valData.push([warn.field, warn.message]);
  }
  if (invoice.validation.warnings.length === 0) valData.push(['(none)', '']);

  // Field confidence
  if (invoice.fields.length > 0) {
    valData.push(['', ''], ['Field', 'Confidence', 'Method']);
    for (const f of invoice.fields) {
      valData.push([f.name, f.confidence, f.extractionMethod]);
    }
  }

  // Referenced documents
  if (invoice.referencedDocuments.length > 0) {
    valData.push(['', ''], ['Referenced Documents', '']);
    valData.push(['Type', 'Reference']);
    for (const rd of invoice.referencedDocuments) {
      valData.push([rd.type, rd.reference]);
    }
  }

  // Stamps
  const stamps = (invoice.fields || []).filter(f => f.name.startsWith('stamp'));
  if (stamps.length > 0) {
    valData.push(['', ''], ['Stamps / Seals', '']);
    for (const s of stamps) {
      valData.push([s.name, s.value]);
    }
  }

  // Handwriting
  const hw = (invoice.fields || []).filter(f => f.extractionMethod === 'icr');
  if (hw.length > 0) {
    valData.push(['', ''], ['Handwritten Annotations', '']);
    for (const h of hw) {
      valData.push([h.name, h.value]);
    }
  }

  const valSheet = XLSX.utils.aoa_to_sheet(valData);
  valSheet['!cols'] = [{ wch: 30 }, { wch: 60 }, { wch: 15 }];
  XLSX.utils.book_append_sheet(wb, valSheet, 'Validation');

  return XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' });
}

module.exports = { toExcel };
