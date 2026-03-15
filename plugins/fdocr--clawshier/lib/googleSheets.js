const { google } = require("googleapis");
const path = require("path");

let _sheets = null;

function getClient() {
  if (_sheets) return _sheets;

  const keyPath = path.resolve(process.env.GOOGLE_SERVICE_ACCOUNT_KEY);
  const auth = new google.auth.GoogleAuth({
    keyFile: keyPath,
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });

  _sheets = google.sheets({ version: "v4", auth });
  return _sheets;
}

async function appendRow(spreadsheetId, row) {
  const sheets = getClient();
  const res = await sheets.spreadsheets.values.append({
    spreadsheetId,
    range: "Sheet1!A:J",
    valueInputOption: "USER_ENTERED",
    insertDataOption: "INSERT_ROWS",
    requestBody: { values: [row] },
  });

  const updatedRange = res.data.updates?.updatedRange || "";
  const match = updatedRange.match(/(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
}

async function getColumn(spreadsheetId, column) {
  const sheets = getClient();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range: `Sheet1!${column}:${column}`,
  });
  return (res.data.values || []).flat();
}

module.exports = { appendRow, getColumn };
