/**
 * Output Format Registry
 */

const { toJSON } = require('./json');
const { toCSV } = require('./csv');
const { toExcel } = require('./excel');

const formatters = {
  json: (invoice, opts) => toJSON(invoice, opts?.pretty !== false),
  csv: (invoice, opts) => toCSV(invoice, opts),
  excel: (invoice, opts) => toExcel(invoice, opts),
  xlsx: (invoice, opts) => toExcel(invoice, opts),
};

function formatOutput(invoice, format = 'json', options = {}) {
  const formatter = formatters[format];
  if (!formatter) {
    throw new Error(`Unknown format "${format}". Available: ${Object.keys(formatters).join(', ')}`);
  }
  return formatter(invoice, options);
}

function listFormats() {
  return ['json', 'csv', 'excel'];
}

module.exports = { formatOutput, listFormats };
