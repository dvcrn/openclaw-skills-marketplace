/**
 * Arithmetic Validation
 * 
 * Validates that invoice numbers add up correctly:
 * - Line items sum to net total
 * - Tax calculations are correct
 * - Net + tax = gross
 */

const TOLERANCE = 0.02; // 2p tolerance for rounding

/**
 * Validate arithmetic consistency of an invoice.
 * Mutates invoice.validation in place.
 * 
 * @param {object} invoice - Canonical invoice object
 * @returns {object} invoice - Same object with validation populated
 */
function validateArithmetic(invoice) {
  const errors = [];
  const warnings = [];

  // 1. Line items sum → net total (excluding shipping lines)
  if (invoice.lineItems.length > 0 && invoice.totals.netTotal !== null) {
    const itemLines = invoice.lineItems.filter(li => li.type !== 'shipping');
    const lineSum = itemLines.reduce((sum, li) => sum + (li.lineTotal || 0), 0);

    if (Math.abs(lineSum - invoice.totals.netTotal) > TOLERANCE) {
      errors.push({
        field: 'totals.netTotal',
        message: `Line items sum (${lineSum.toFixed(2)}) does not match net total (${invoice.totals.netTotal.toFixed(2)})`,
      });
    }
  }

  // 2. Individual line item: qty × price = line total
  invoice.lineItems.forEach((li, i) => {
    if (li.quantity !== null && li.unitPrice !== null && li.lineTotal !== null) {
      const expected = li.quantity * li.unitPrice;
      // Account for discounts
      const afterDiscount = li.discount ? expected - li.discount : expected;
      if (Math.abs(afterDiscount - li.lineTotal) > TOLERANCE) {
        errors.push({
          field: `lineItems[${i}].lineTotal`,
          message: `qty (${li.quantity}) × price (${li.unitPrice}) = ${expected.toFixed(2)}, but lineTotal is ${li.lineTotal.toFixed(2)}`,
        });
      }
    }
  });

  // 3. VAT calculation
  if (invoice.totals.netTotal !== null && invoice.totals.vatTotal !== null) {
    // Check against VAT breakdown if available
    if (invoice.totals.vatBreakdown.length > 0) {
      const breakdownSum = invoice.totals.vatBreakdown.reduce((sum, vb) => sum + vb.amount, 0);
      if (Math.abs(breakdownSum - invoice.totals.vatTotal) > TOLERANCE) {
        errors.push({
          field: 'totals.vatTotal',
          message: `VAT breakdown sum (${breakdownSum.toFixed(2)}) does not match vatTotal (${invoice.totals.vatTotal.toFixed(2)})`,
        });
      }
    }

    // If single VAT rate, check the math
    if (invoice.totals.vatBreakdown.length === 1) {
      const rate = invoice.totals.vatBreakdown[0].rate;
      if (rate) {
        const expectedVat = invoice.totals.netTotal * (rate / 100);
        if (Math.abs(expectedVat - invoice.totals.vatTotal) > TOLERANCE) {
          warnings.push({
            field: 'totals.vatTotal',
            message: `Expected VAT at ${rate}% = ${expectedVat.toFixed(2)}, got ${invoice.totals.vatTotal.toFixed(2)}`,
          });
        }
      }
    }
  }

  // 4. Net + Shipping + VAT = Gross
  if (invoice.totals.netTotal !== null && invoice.totals.vatTotal !== null && invoice.totals.grossTotal !== null) {
    const shipping = invoice.totals.shipping || 0;
    const expectedGross = invoice.totals.netTotal + shipping + invoice.totals.vatTotal;
    if (Math.abs(expectedGross - invoice.totals.grossTotal) > TOLERANCE) {
      errors.push({
        field: 'totals.grossTotal',
        message: `net (${invoice.totals.netTotal.toFixed(2)}) + shipping (${shipping.toFixed(2)}) + VAT (${invoice.totals.vatTotal.toFixed(2)}) = ${expectedGross.toFixed(2)}, but gross is ${invoice.totals.grossTotal.toFixed(2)}`,
      });
    }
  }

  // 5. Basic sanity checks
  if (invoice.totals.grossTotal !== null && invoice.totals.netTotal !== null) {
    if (invoice.totals.grossTotal < invoice.totals.netTotal) {
      warnings.push({
        field: 'totals.grossTotal',
        message: 'Gross total is less than net total — possible negative tax or error',
      });
    }
  }

  invoice.validation.arithmeticValid = errors.length === 0;
  invoice.validation.errors.push(...errors);
  invoice.validation.warnings.push(...warnings);

  return invoice;
}

module.exports = { validateArithmetic, TOLERANCE };
