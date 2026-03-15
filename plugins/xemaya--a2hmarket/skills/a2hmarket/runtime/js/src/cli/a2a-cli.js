const { parseOptions } = require("./arg-parser");
const { resolveListenerConfig } = require("../config/loader");
const { createLogger } = require("../listener/logger");
const { MqttTokenClient } = require("../adapters/mqtt-token-client");
const { buildEnvelope, signEnvelope } = require("../protocol/a2a-protocol");
const { getListenerProcess, enqueueOutboundEnvelope } = require("../a2a/outbound-queue");

function printUsage() {
  process.stdout.write(
    [
      "Usage:",
      "  a2hmarket a2a send --target-agent-id <agent_id> (--text <message> | --payload-json <json>) [--message-type <type>] [--trace-id <id>] [--qos <0|1>] [--verbose]",
      "",
      "Note:",
      "  - a2a send is disabled by default for OpenClaw safety.",
      "  - enable only for debugging via A2HMARKET_ENABLE_A2A_SEND=true.",
      "  - trade negotiation is handled by SKILL layer (not CLI).",
    ].join("\n") + "\n"
  );
}

function parsePayload(options) {
  const payloadJson = options["payload-json"];
  const text = options.text;

  if (payloadJson != null) {
    let parsed = null;
    try {
      parsed = JSON.parse(String(payloadJson));
    } catch (err) {
      throw new Error(`invalid --payload-json: ${(err && err.message) || String(err)}`);
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("--payload-json must be a JSON object");
    }
    if (text != null && parsed.text == null) {
      parsed.text = String(text);
    }
    return parsed;
  }

  if (text == null || String(text).trim() === "") {
    throw new Error("either --text or --payload-json is required");
  }
  return { text: String(text) };
}

function parseQos(raw) {
  if (raw == null) return 1;
  const qos = Number.parseInt(String(raw), 10);
  if (!Number.isFinite(qos) || (qos !== 0 && qos !== 1)) {
    throw new Error("--qos must be 0 or 1");
  }
  return qos;
}

function isA2aSendEnabled() {
  const raw = String(process.env.A2HMARKET_ENABLE_A2A_SEND || "false").trim().toLowerCase();
  return raw === "1" || raw === "true" || raw === "yes" || raw === "on";
}

async function runA2aSend(options) {
  if (!isA2aSendEnabled()) {
    throw new Error("a2a send is disabled by policy; trade negotiation is handled by SKILL layer");
  }

  const targetAgentId = String(options["target-agent-id"] || options.target || "").trim();
  if (!targetAgentId) {
    throw new Error("--target-agent-id is required");
  }

  const payload = parsePayload(options);
  const messageType = String(options["message-type"] || "chat.request").trim() || "chat.request";
  const qos = parseQos(options.qos);

  const originalPushEnabled = process.env.A2HMARKET_PUSH_ENABLED;
  if (originalPushEnabled == null) {
    process.env.A2HMARKET_PUSH_ENABLED = "false";
  }
  let cfg = null;
  try {
    cfg = resolveListenerConfig();
  } finally {
    if (originalPushEnabled == null) {
      delete process.env.A2HMARKET_PUSH_ENABLED;
    }
  }
  const logger = createLogger(Boolean(options.verbose));

  const signSecret = cfg.a2aSharedSecret || cfg.agentSecret;
  if (!signSecret) {
    throw new Error("missing signing secret: configure A2HMARKET_A2A_SHARED_SECRET or AGENT_SECRET");
  }

  const tokenClient = new MqttTokenClient(cfg);
  const envelope = signEnvelope(
    signSecret,
    buildEnvelope({
      senderId: cfg.agentId,
      targetId: targetAgentId,
      messageType,
      traceId: options["trace-id"] ? String(options["trace-id"]) : undefined,
      payload,
    })
  );
  const sentTopic = `${cfg.mqttTopicId}/p2p/${tokenClient.buildClientId(targetAgentId)}`;
  const listener = getListenerProcess(cfg.lockPath);
  if (listener.running) {
    const queued = enqueueOutboundEnvelope({
      cfg,
      targetAgentId,
      messageType,
      qos,
      envelope,
    });
    process.stdout.write(
      JSON.stringify(
        {
          ok: true,
          queued: true,
          duplicate: !queued.created,
          queue_mode: "listener",
          listener_pid: listener.pid,
          topic: sentTopic,
          sender_id: cfg.agentId,
          target_id: targetAgentId,
          message_type: messageType,
          message_id: envelope.message_id,
          trace_id: envelope.trace_id,
        },
        null,
        2
      ) + "\n"
    );
    return 0;
  }
  logger.warn("a2a send rejected: listener is not running (strict listener-only mode)");
  throw new Error("listener is not running; send is listener-only. start listener first");
}

async function runA2aCli(args) {
  const command = args[0];
  const options = parseOptions(args.slice(1));
  if (!command || options.help || options.h) {
    printUsage();
    return 1;
  }
  if (command !== "send") {
    printUsage();
    return 1;
  }

  try {
    return await runA2aSend(options);
  } catch (err) {
    process.stderr.write(`[a2hmarket-a2a] ${(err && err.message) || String(err)}\n`);
    return 1;
  }
}

module.exports = {
  runA2aCli,
  parsePayload,
  parseQos,
  isA2aSendEnabled,
};
