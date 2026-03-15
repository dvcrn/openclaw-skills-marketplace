/**
 * Document Business Rule Validation
 * 
 * Additional validation rules beyond arithmetic that catch
 * non-invoice documents and data quality issues.
 */

/**
 * Run document-level business rules.
 * Mutates invoice.validation in place.
 * 
 * @param {object} invoice - Canonical invoice object
 * @returns {object} invoice
 */
function validateDocumentRules(invoice) {
  const warnings = [];
  const errors = [];

  const h = invoice.header;
  const t = invoice.totals;
  const docType = invoice.metadata.documentType;

  // 1. Invoice number missing
  if (!h.invoiceNumber) {
    warnings.push({
      field: 'header.invoiceNumber',
      message: 'No invoice number detected — may be a receipt, confirmation, or incomplete document',
    });
  }

  // 2. Supplier name missing
  if (!h.supplierName) {
    warnings.push({
      field: 'header.supplierName',
      message: 'No supplier/vendor name detected',
    });
  }

  // 3. Buyer entity missing
  if (!h.buyerName) {
    warnings.push({
      field: 'header.buyerName',
      message: 'No buyer/customer name detected — common in receipts but required for invoices',
    });
  }

  // 4. No tax/VAT structure
  if (t.vatTotal === null && (!t.vatBreakdown || t.vatBreakdown.length === 0)) {
    warnings.push({
      field: 'totals.vatTotal',
      message: 'No tax/VAT information detected — may indicate a receipt or non-tax document',
    });
  }

  // 5. No date
  if (!h.invoiceDate) {
    warnings.push({
      field: 'header.invoiceDate',
      message: 'No invoice date detected',
    });
  }

  // 6. No currency detected
  if (!h.currency) {
    warnings.push({
      field: 'header.currency',
      message: 'No currency detected — ambiguous document',
    });
  }

  // 7. Very small amount (potential receipt)
  if (t.grossTotal !== null && t.grossTotal < 10) {
    warnings.push({
      field: 'totals.grossTotal',
      message: `Very small amount (${t.grossTotal}) — may be a receipt rather than an invoice`,
    });
  }

  // 8. No line items
  if (!invoice.lineItems || invoice.lineItems.length === 0) {
    warnings.push({
      field: 'lineItems',
      message: 'No line items detected — may be a summary document or non-invoice',
    });
  }

  // 9. Supplier and buyer VAT numbers both missing
  if (!h.supplierVatNumber && !h.buyerVatNumber) {
    warnings.push({
      field: 'header.vatNumbers',
      message: 'No VAT/tax registration numbers found for supplier or buyer',
    });
  }

  // 10. Due date missing (invoices usually have one, receipts don't)
  if (!h.dueDate && docType === 'invoice') {
    warnings.push({
      field: 'header.dueDate',
      message: 'No due date detected — unusual for an invoice (common in receipts)',
    });
  }

  // 11. Document classified as non-invoice type
  if (docType && !['invoice', 'credit-note'].includes(docType)) {
    warnings.push({
      field: 'metadata.documentType',
      message: `Document classified as "${docType}" — not a standard invoice`,
    });
  }

  // 12. Supplier VAT/tax ID missing (stronger signal than both missing)
  if (!h.supplierVatNumber && h.supplierName) {
    warnings.push({
      field: 'header.supplierVatNumber',
      message: 'Supplier identified but no VAT/tax registration number — may indicate informal/retail receipt',
    });
  }

  // 13. Invoice number looks suspicious (too short, or looks like a transaction/POS ID)
  if (h.invoiceNumber) {
    const invNum = String(h.invoiceNumber).trim();
    if (invNum.length <= 2) {
      warnings.push({
        field: 'header.invoiceNumber',
        message: `Invoice number "${invNum}" is suspiciously short — may be a transaction ID or sequence number`,
      });
    }
    // POS-style transaction IDs
    if (/^(TXN|TRX|AUTH|BATCH|SEQ|POS|TERM)/i.test(invNum)) {
      warnings.push({
        field: 'header.invoiceNumber',
        message: `Invoice number "${invNum}" looks like a POS/terminal reference, not an invoice number`,
      });
    }
  }

  // 14. Receipt-like indicators from fields
  const allText = JSON.stringify(invoice).toLowerCase();
  const receiptSignals = [
    'thank you for your purchase',
    'terminal id',
    'auth code',
    'batch id',
    'card payment',
    'change due',
    'cashier',
  ];
  const foundSignals = receiptSignals.filter(s => allText.includes(s));
  if (foundSignals.length >= 2) {
    warnings.push({
      field: 'metadata.documentType',
      message: `Document contains receipt-like signals: ${foundSignals.join(', ')}`,
    });
  }

  // 15. No payment terms AND no due date AND no bank details (receipt pattern)
  if (!h.paymentTerms && !h.dueDate && !h.bankDetails?.iban && !h.bankDetails?.accountNumber) {
    if (docType === 'invoice' || !docType) {
      warnings.push({
        field: 'header.paymentInfo',
        message: 'No payment terms, due date, or bank details — unusual for an invoice',
      });
    }
  }

  // Calculate a document quality score based on key fields present
  const keyFields = [
    h.invoiceNumber, h.invoiceDate, h.currency, h.supplierName,
    h.buyerName, h.supplierVatNumber, t.netTotal, t.vatTotal, t.grossTotal,
  ];
  const presentCount = keyFields.filter(f => f !== null && f !== undefined).length;
  const qualityScore = presentCount / keyFields.length;

  invoice.validation.documentQuality = {
    score: Math.round(qualityScore * 100) / 100,
    presentFields: presentCount,
    totalChecked: keyFields.length,
    rating: qualityScore >= 0.8 ? 'good' : qualityScore >= 0.5 ? 'partial' : 'poor',
  };

  invoice.validation.warnings.push(...warnings);
  invoice.validation.errors.push(...errors);

  return invoice;
}

module.exports = { validateDocumentRules };
