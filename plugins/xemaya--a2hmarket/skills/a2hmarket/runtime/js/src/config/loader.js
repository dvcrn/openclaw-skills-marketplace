const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {
  DEFAULT_DB_PATH,
  DEFAULT_LOCK_PATH,
  DEFAULT_LOG_PATH,
  DEFAULT_PID_PATH,
  resolvePath,
} = require("./paths");
const {
  DEFAULT_OPENCLAW_SESSION_KEY,
  DEFAULT_OPENCLAW_SESSION_LABEL,
  looksLikeSessionKey,
  looksLikeUuid,
  resolveOpenclawCommand,
  ensureOpenclawSessionBinding,
  writeOpenclawSessionState,
} = require("./openclaw-session");

function nowMs() {
  return Date.now();
}

function parseBool(raw, fallback) {
  if (raw == null) return fallback;
  const value = String(raw).trim().toLowerCase();
  if (["1", "true", "yes", "y", "on"].includes(value)) return true;
  if (["0", "false", "no", "n", "off"].includes(value)) return false;
  return fallback;
}

function parseIntBound(raw, fallback, min, max) {
  let n = Number.parseInt(String(raw == null ? fallback : raw), 10);
  if (!Number.isFinite(n)) n = fallback;
  if (Number.isFinite(min)) n = Math.max(min, n);
  if (Number.isFinite(max)) n = Math.min(max, n);
  return n;
}

function loadShellExports(configPath) {
  const values = {};
  if (!configPath || !fs.existsSync(configPath)) return values;

  const lines = fs.readFileSync(configPath, "utf8").split(/\r?\n/);
  const pattern = /^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/;
  for (const rawLine of lines) {
    const line = String(rawLine || "").trim();
    if (!line || line.startsWith("#")) continue;
    const matched = rawLine.match(pattern);
    if (!matched) continue;
    const key = matched[1];
    let value = matched[2].trim();
    // Strip inline comment (# not inside quotes) - MQTT clientId must be ASCII-only
    let inQuote = null;
    for (let i = 0; i < value.length; i++) {
      const c = value[i];
      if (c === '"' || c === "'") {
        if (inQuote === c) inQuote = null;
        else if (!inQuote) inQuote = c;
      } else if (c === "#" && !inQuote) {
        value = value.slice(0, i).trim();
        break;
      }
    }
    if (value.length >= 2 && value[0] === value[value.length - 1] && (value[0] === '"' || value[0] === "'")) {
      value = value.slice(1, -1);
    }
    values[key] = value;
  }
  return values;
}

function resolveConfigPath() {
  const { A2HMARKET_ROOT } = require("./paths");
  const authoritativePath = path.join(A2HMARKET_ROOT, "config", "config.sh");
  const explicit = String(process.env.A2HMARKET_CONFIG_PATH || "").trim();
  if (!explicit) return authoritativePath;

  const explicitPath = path.resolve(explicit);
  const authorityResolved = path.resolve(authoritativePath);
  if (explicitPath !== authorityResolved) {
    throw new Error(
      `A2HMARKET_CONFIG_PATH is not allowed: ${explicitPath}. authoritative config path is ${authorityResolved}`
    );
  }
  return authoritativePath;
}

function resolveListenerConfig() {
  const configPath = resolveConfigPath();
  if (!fs.existsSync(configPath)) {
    throw new Error(`missing authoritative config: ${configPath}`);
  }
  const shellCfg = loadShellExports(configPath);
  const pick = (key, fallback) => {
    const shellVal = shellCfg[key];
    if (shellVal != null && String(shellVal).trim() !== "") return String(shellVal).trim();
    const envVal = process.env[key];
    if (envVal != null && String(envVal).trim() !== "") return String(envVal).trim();
    return fallback == null ? "" : String(fallback);
  };

  const baseUrl = pick("BASE_URL", "");
  const agentId = pick("AGENT_ID", "");
  const agentSecret = pick("AGENT_SECRET", "");
  if (!baseUrl) {
    throw new Error("missing BASE_URL");
  }
  if (!agentId || !agentSecret) {
    throw new Error("missing credentials: BASE_URL/AGENT_ID/AGENT_SECRET");
  }

  // Runtime 默认配置
  const RUNTIME_DEFAULTS = {
    A2HMARKET_PUSH_ENABLED: "true",
    A2HMARKET_OPENCLAW_SESSION_KEY: "a2hmarket:main:main",
    A2HMARKET_OPENCLAW_SESSION_LABEL: "A2HMarket Main Session",
    A2HMARKET_OPENCLAW_SESSION_STRICT: "true",
    A2HMARKET_OPENCLAW_BIN: "openclaw",
    A2HMARKET_OPENCLAW_PUSH_TIMEOUT_SEC: "120",
    A2HMARKET_OPENCLAW_PUSH_THINKING: "off",
    A2HMARKET_PUSH_ONCE: "true",
    A2HMARKET_MQTT_TOKEN_BASE_URL: baseUrl,
    A2HMARKET_MQTT_ENDPOINT: "post-cn-e4k4o78q702.mqtt.aliyuncs.com",
    A2HMARKET_MQTT_PORT: "8883",
    A2HMARKET_MQTT_PROTOCOL: "mqtts",
    A2HMARKET_MQTT_GROUP_ID: "GID_agent",
    A2HMARKET_MQTT_TOPIC_ID: "P2P_TOPIC",
    A2HMARKET_POLL_INTERVAL_MS: "5000",
    A2HMARKET_PUSH_BATCH_SIZE: "20",
    A2HMARKET_PUSH_ACK_WAIT_MS: "15000",
    A2HMARKET_PUSH_RETRY_MAX_DELAY_MS: "300000",
    A2HMARKET_A2A_SHARED_SECRET: "",
    A2HMARKET_A2A_OUTBOX_BATCH_SIZE: "50",
    A2HMARKET_A2A_OUTBOX_RETRY_MAX_DELAY_MS: String(60 * 1000),
    A2HMARKET_MQTT_RECONNECT_PERIOD_MS: "5000",
    A2HMARKET_MQTT_CONNECT_TIMEOUT_MS: "15000",
    A2HMARKET_MQTT_TOKEN_REFRESH_THRESHOLD_MS: String(60 * 60 * 1000),
    A2HMARKET_MQTT_TOKEN_PATH: "/mqtt-token/api/v1/token",
    A2HMARKET_MQTT_TOKEN_SIGN_PATH: "",
    A2HMARKET_PUSH_ACK_CONSUMER: "openclaw",
  };

  const pickWithDefault = (key) => {
    const value = pick(key, RUNTIME_DEFAULTS[key] || "");
    return value;
  };

  let pushEnabled = parseBool(pickWithDefault("A2HMARKET_PUSH_ENABLED"), true);

  const openclawBin = pickWithDefault("A2HMARKET_OPENCLAW_BIN");
  const openclawNodeScript = pick("A2HMARKET_OPENCLAW_NODE_SCRIPT", "") || null;
  const openclawCommand = pushEnabled
    ? resolveOpenclawCommand(openclawBin, openclawNodeScript)
    : [];
  const openclawSessionLabel = pickWithDefault("A2HMARKET_OPENCLAW_SESSION_LABEL");
  const openclawSessionStrict = parseBool(pickWithDefault("A2HMARKET_OPENCLAW_SESSION_STRICT"), true);
  const configuredSessionKey = pickWithDefault("A2HMARKET_OPENCLAW_SESSION_KEY");
  const openclawSessionKeyRaw = configuredSessionKey || DEFAULT_OPENCLAW_SESSION_KEY;
  let openclawSessionId = "";
  let openclawSessionKeyCanonical = "";
  let openclawSessionBootstrapError = "";
  let openclawSessionBootstrapStatePath = "";

  if (pushEnabled) {
    if (!openclawSessionKeyRaw) {
      throw new Error("missing A2HMARKET_OPENCLAW_SESSION_KEY while push is enabled");
    }
    if (openclawSessionKeyRaw !== DEFAULT_OPENCLAW_SESSION_KEY) {
      const detail = `A2HMARKET_OPENCLAW_SESSION_KEY must be ${DEFAULT_OPENCLAW_SESSION_KEY}, got ${openclawSessionKeyRaw}`;
      if (openclawSessionStrict) {
        throw new Error(detail);
      }
      pushEnabled = false;
      openclawSessionBootstrapError = detail;
    }

    if (pushEnabled && !looksLikeSessionKey(openclawSessionKeyRaw)) {
      const legacySessionId = pick("A2HMARKET_OPENCLAW_SESSION_ID", "");
      if (looksLikeUuid(legacySessionId) && !pick("A2HMARKET_OPENCLAW_SESSION_KEY", "")) {
        openclawSessionId = legacySessionId;
      } else if (openclawSessionStrict) {
        throw new Error(
          `invalid A2HMARKET_OPENCLAW_SESSION_KEY: ${openclawSessionKeyRaw}. expected <namespace>:<profile>:<name>`
        );
      } else {
        pushEnabled = false;
        openclawSessionBootstrapError = `invalid A2HMARKET_OPENCLAW_SESSION_KEY: ${openclawSessionKeyRaw}`;
      }
    }

    if (pushEnabled && !openclawSessionId) {
      const ensured = ensureOpenclawSessionBinding({
        openclawCommand,
        sessionKey: openclawSessionKeyRaw,
        sessionLabel: openclawSessionLabel,
      });
      if (ensured.ok) {
        openclawSessionId = ensured.sessionId;
        openclawSessionKeyCanonical = ensured.canonicalKey;
      } else if (openclawSessionStrict) {
        throw new Error(
          `failed to ensure A2HMARKET_OPENCLAW_SESSION_KEY=${openclawSessionKeyRaw}: ${ensured.detail}`
        );
      } else {
        pushEnabled = false;
        openclawSessionBootstrapError = String(ensured.detail || "session bootstrap failed");
      }
    }
  }

  if (pushEnabled && !openclawSessionId) {
    throw new Error("failed to resolve OpenClaw push session id while push is enabled");
  }

  if (openclawSessionKeyRaw) {
    openclawSessionBootstrapStatePath = writeOpenclawSessionState({
      key: openclawSessionKeyRaw,
      canonicalKey: openclawSessionKeyCanonical || openclawSessionKeyRaw,
      sessionId: openclawSessionId || "",
      label: openclawSessionLabel,
      strict: openclawSessionStrict,
      pushEnabled,
      bootstrapError: openclawSessionBootstrapError || "",
      updatedAtMs: nowMs(),
    });
  }
  const mqttTokenBaseUrl = pickWithDefault("A2HMARKET_MQTT_TOKEN_BASE_URL").replace(/\/+$/, "");

  return {
    configPath,
    baseUrl: baseUrl.replace(/\/+$/, ""),
    mqttTokenPath: pickWithDefault("A2HMARKET_MQTT_TOKEN_PATH"),
    mqttTokenSignPath: pickWithDefault("A2HMARKET_MQTT_TOKEN_SIGN_PATH"),
    mqttTokenBaseUrl,
    mqttClientGroupId: pickWithDefault("A2HMARKET_MQTT_GROUP_ID"),
    mqttTopicId: pickWithDefault("A2HMARKET_MQTT_TOPIC_ID"),
    mqttEndpoint: pickWithDefault("A2HMARKET_MQTT_ENDPOINT"),
    mqttPort: parseIntBound(pickWithDefault("A2HMARKET_MQTT_PORT"), 8883, 1, 65535),
    mqttProtocol: pickWithDefault("A2HMARKET_MQTT_PROTOCOL"),
    mqttReconnectPeriodMs: parseIntBound(
      pickWithDefault("A2HMARKET_MQTT_RECONNECT_PERIOD_MS"),
      5000,
      1000,
      60000
    ),
    mqttConnectTimeoutMs: parseIntBound(
      pickWithDefault("A2HMARKET_MQTT_CONNECT_TIMEOUT_MS"),
      15000,
      1000,
      120000
    ),
    a2aOutboxBatchSize: parseIntBound(
      pickWithDefault("A2HMARKET_A2A_OUTBOX_BATCH_SIZE"),
      50,
      1,
      500
    ),
    a2aOutboxRetryMaxDelayMs: parseIntBound(
      pickWithDefault("A2HMARKET_A2A_OUTBOX_RETRY_MAX_DELAY_MS"),
      60 * 1000,
      1000,
      30 * 60 * 1000
    ),
    a2aSharedSecret: pickWithDefault("A2HMARKET_A2A_SHARED_SECRET"),
    mqttTokenRefreshThresholdMs: parseIntBound(
      pickWithDefault("A2HMARKET_MQTT_TOKEN_REFRESH_THRESHOLD_MS"),
      60 * 60 * 1000,
      5000,
      24 * 60 * 60 * 1000
    ),
    agentId,
    agentSecret,
    dbPath: resolvePath(pick("A2HMARKET_DB_PATH", DEFAULT_DB_PATH), DEFAULT_DB_PATH),
    lockPath: resolvePath(pick("A2HMARKET_LISTENER_LOCK_FILE", DEFAULT_LOCK_PATH), DEFAULT_LOCK_PATH),
    logPath: resolvePath(pick("A2HMARKET_LISTENER_LOG_FILE", DEFAULT_LOG_PATH), DEFAULT_LOG_PATH),
    pidPath: resolvePath(pick("A2HMARKET_LISTENER_PID_FILE", DEFAULT_PID_PATH), DEFAULT_PID_PATH),
    pollIntervalMs: parseIntBound(pickWithDefault("A2HMARKET_POLL_INTERVAL_MS"), 5000, 500),
    pushEnabled,
    openclawCommand,
    openclawSessionId,
    openclawSessionKey: openclawSessionKeyRaw,
    openclawSessionKeyCanonical,
    openclawSessionLabel,
    openclawSessionStrict,
    openclawSessionBootstrapError,
    openclawSessionBootstrapStatePath,
    openclawPushThinking: pickWithDefault("A2HMARKET_OPENCLAW_PUSH_THINKING"),
    openclawPushTimeoutSec: parseIntBound(
      pickWithDefault("A2HMARKET_OPENCLAW_PUSH_TIMEOUT_SEC"),
      120,
      30,
      1800
    ),
    pushAckConsumer: pickWithDefault("A2HMARKET_PUSH_ACK_CONSUMER"),
    pushAckWaitMs: parseIntBound(
      pickWithDefault("A2HMARKET_PUSH_ACK_WAIT_MS"),
      15000,
      1000,
      10 * 60 * 1000
    ),
    pushRetryMaxDelayMs: parseIntBound(
      pickWithDefault("A2HMARKET_PUSH_RETRY_MAX_DELAY_MS"),
      5 * 60 * 1000,
      10000,
      60 * 60 * 1000
    ),
    pushBatchSize: parseIntBound(pickWithDefault("A2HMARKET_PUSH_BATCH_SIZE"), 20, 1, 200),
    pushOnce: parseBool(pickWithDefault("A2HMARKET_PUSH_ONCE"), true),
    startedAtMs: nowMs(),
  };
}

module.exports = {
  loadShellExports,
  resolveConfigPath,
  resolveListenerConfig,
  parseBool,
  parseIntBound,
};
