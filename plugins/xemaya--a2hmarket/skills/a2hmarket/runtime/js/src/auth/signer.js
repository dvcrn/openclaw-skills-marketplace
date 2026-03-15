const crypto = require("node:crypto");

function computeHttpSignature({ secret, method, path, agentId, timestampSec }) {
  const normalizedSecret = String(secret || "");
  const normalizedMethod = String(method || "").toUpperCase();
  const normalizedPath = String(path || "");
  const normalizedAgentId = String(agentId || "");
  const normalizedTimestamp = String(timestampSec || "");
  const payload = `${normalizedMethod}&${normalizedPath}&${normalizedAgentId}&${normalizedTimestamp}`;

  return crypto.createHmac("sha256", normalizedSecret).update(payload).digest("hex");
}

function sha256Hex(input) {
  return crypto.createHash("sha256").update(String(input || ""), "utf8").digest("hex");
}

module.exports = {
  computeHttpSignature,
  sha256Hex,
};
