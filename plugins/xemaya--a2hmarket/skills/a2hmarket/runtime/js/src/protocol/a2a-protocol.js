const crypto = require("node:crypto");
const { sha256Hex } = require("../auth/signer");

const PROTOCOL = "a2hmarket-a2a";
const SCHEMA_VERSION = "1.0.0";

function randomId(prefix) {
  return `${prefix}_${Date.now()}_${crypto.randomBytes(4).toString("hex")}`;
}

function toBeijingTimeISO() {
  const now = new Date();
  const utc8Ms = now.getTime() + (8 * 60 * 60 * 1000);
  const beijing = new Date(utc8Ms);
  const year = beijing.getUTCFullYear();
  const month = String(beijing.getUTCMonth() + 1).padStart(2, '0');
  const day = String(beijing.getUTCDate()).padStart(2, '0');
  const hours = String(beijing.getUTCHours()).padStart(2, '0');
  const minutes = String(beijing.getUTCMinutes()).padStart(2, '0');
  const seconds = String(beijing.getUTCSeconds()).padStart(2, '0');
  const ms = String(beijing.getUTCMilliseconds()).padStart(3, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${ms}+08:00`;
}

function canonicalize(value) {
  if (value == null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalize(item)).join(",")}]`;
  }
  const keys = Object.keys(value).sort();
  const pairs = keys.map((k) => `${JSON.stringify(k)}:${canonicalize(value[k])}`);
  return `{${pairs.join(",")}}`;
}

function computeEnvelopeSignature(secret, envelopeWithoutSignature) {
  const payload = canonicalize(envelopeWithoutSignature);
  return crypto.createHmac("sha256", String(secret || "")).update(payload).digest("hex");
}

function buildEnvelope({
  senderId,
  targetId,
  messageType,
  payload,
  traceId,
  messageId,
  timestampIso,
  nonce,
}) {
  const normalizedPayload = payload && typeof payload === "object" ? payload : {};
  return {
    protocol: PROTOCOL,
    schema_version: SCHEMA_VERSION,
    message_type: String(messageType || ""),
    message_id: String(messageId || randomId("msg")),
    trace_id: String(traceId || randomId("trace")),
    sender_id: String(senderId || ""),
    target_id: String(targetId || ""),
    timestamp: String(timestampIso || toBeijingTimeISO()),
    nonce: String(nonce || crypto.randomBytes(8).toString("hex")),
    payload: normalizedPayload,
    payload_hash: sha256Hex(canonicalize(normalizedPayload)),
    signature: "",
  };
}

function signEnvelope(secret, envelope) {
  const cloned = { ...envelope };
  delete cloned.signature;
  const signature = computeEnvelopeSignature(secret, cloned);
  return {
    ...cloned,
    signature,
  };
}

function verifyEnvelope(secret, envelope, options) {
  const opts = options || {};
  const toleranceMs =
    Number.isFinite(Number(opts.timestampToleranceMs)) ? Number(opts.timestampToleranceMs) : 5 * 60 * 1000;

  const core = verifyEnvelopeCore(envelope, { timestampToleranceMs: toleranceMs });
  if (!core.ok) return core;

  const base = { ...envelope };
  delete base.signature;
  const expectedSignature = computeEnvelopeSignature(secret, base);
  if (expectedSignature !== envelope.signature) {
    return { ok: false, reason: "signature mismatch" };
  }
  return { ok: true };
}

function verifyEnvelopeCore(envelope, options) {
  const opts = options || {};
  const toleranceMs =
    Number.isFinite(Number(opts.timestampToleranceMs)) ? Number(opts.timestampToleranceMs) : 5 * 60 * 1000;

  if (!envelope || typeof envelope !== "object") {
    return { ok: false, reason: "invalid envelope type" };
  }
  if (envelope.protocol !== PROTOCOL) {
    return { ok: false, reason: "protocol mismatch" };
  }
  if (envelope.schema_version !== SCHEMA_VERSION) {
    return { ok: false, reason: "schema_version mismatch" };
  }
  if (!envelope.message_id || !envelope.sender_id || !envelope.message_type) {
    return { ok: false, reason: "missing required fields" };
  }
  const ts = Date.parse(String(envelope.timestamp || ""));
  if (!Number.isFinite(ts)) {
    return { ok: false, reason: "invalid timestamp" };
  }
  if (Math.abs(Date.now() - ts) > toleranceMs) {
    return { ok: false, reason: "timestamp out of tolerance" };
  }
  const expectedPayloadHash = sha256Hex(canonicalize(envelope.payload || {}));
  if (expectedPayloadHash !== envelope.payload_hash) {
    return { ok: false, reason: "payload_hash mismatch" };
  }
  return { ok: true };
}

module.exports = {
  PROTOCOL,
  SCHEMA_VERSION,
  canonicalize,
  buildEnvelope,
  signEnvelope,
  verifyEnvelopeCore,
  verifyEnvelope,
};
