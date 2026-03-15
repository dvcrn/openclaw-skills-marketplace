const { randomUUID } = require("node:crypto");
const { verifyEnvelope, verifyEnvelopeCore } = require("../protocol/a2a-protocol");
const { toEventHash, sanitizePreview } = require("../listener/message-utils");

function nowMs() {
  return Date.now();
}

function extractPreview(envelope) {
  const payload = envelope && envelope.payload ? envelope.payload : {};
  const text = payload.text || payload.message || payload.preview || "";
  if (text) return sanitizePreview(String(text), 100);
  return sanitizePreview(JSON.stringify(payload), 100);
}

function eventIdFromEnvelope() {
  return `a2hmarket_a2a_${Math.floor(Date.now() / 1000)}_${randomUUID().replace(/-/g, "").slice(0, 8)}`;
}

function isInboundTopic(topic, cfg) {
  const prefix = `${cfg.mqttTopicId}/p2p/`;
  return String(topic || "").startsWith(prefix);
}

function parseEnvelope(rawPayload) {
  if (typeof rawPayload === "string") return JSON.parse(rawPayload);
  if (Buffer.isBuffer(rawPayload)) return JSON.parse(rawPayload.toString("utf8"));
  if (rawPayload && typeof rawPayload === "object") return rawPayload;
  throw new Error("unsupported payload type");
}

function handleA2aMessage({ topic, payload, envelope: parsedEnvelope, store, cfg, logger }) {
  if (!isInboundTopic(topic, cfg)) {
    return { accepted: false, reason: "ignored_topic" };
  }

  let envelope = parsedEnvelope;
  if (!envelope) {
    try {
      envelope = parseEnvelope(payload);
    } catch (err) {
      return { accepted: false, reason: `invalid_json:${err && err.message ? err.message : String(err)}` };
    }
  }

  const core = verifyEnvelopeCore(envelope);
  if (!core.ok) {
    return { accepted: false, reason: `invalid_envelope:${core.reason}` };
  }
  if (cfg.a2aSharedSecret) {
    const verified = verifyEnvelope(cfg.a2aSharedSecret, envelope);
    if (!verified.ok) {
      return { accepted: false, reason: `signature_rejected:${verified.reason}` };
    }
  } else {
    logger.debug("a2a shared secret not configured; signature verification skipped");
  }

  const peerId = String(envelope.sender_id || "").trim() || "unknown";
  const messageTs = Number.isFinite(Date.parse(String(envelope.timestamp || "")))
    ? Date.parse(String(envelope.timestamp))
    : nowMs();
  const preview = extractPreview(envelope);
  const hash = toEventHash({
    peerId,
    messageTs,
    messageText: preview,
    messageId: envelope.message_id || null,
  });

  const inserted = store.insertIncomingEvent({
    event_id: eventIdFromEnvelope(),
    peer_id: peerId,
    message_id: envelope.message_id || null,
    msg_ts: messageTs,
    hash,
    unread_count: 1,
    preview,
    payload: envelope,
    state: "NEW",
    source: "MQTT",
    a2a_message_id: envelope.message_id || null,
    push_enabled: cfg.pushEnabled,
    push_target: "openclaw",
  });

  if (!inserted.created) {
    return { accepted: false, reason: "duplicate_message_id" };
  }
  return {
    accepted: true,
    event_id: inserted.eventId,
    peer_id: peerId,
    message_id: envelope.message_id || null,
  };
}

module.exports = {
  handleA2aMessage,
  isInboundTopic,
};
