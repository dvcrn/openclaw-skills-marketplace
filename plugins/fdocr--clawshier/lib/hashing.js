const crypto = require("crypto");

function fingerprint(vendor, date, total) {
  const input = [vendor, date, total]
    .map((v) => String(v).trim().toLowerCase())
    .join("|");
  return crypto.createHash("sha256").update(input).digest("hex");
}

module.exports = { fingerprint };
