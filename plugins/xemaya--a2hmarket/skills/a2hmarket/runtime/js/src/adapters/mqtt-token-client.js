const { computeHttpSignature } = require("../auth/signer");

function nowMs() {
  return Date.now();
}

function parseTokenResponse(rawBody) {
  if (!rawBody || typeof rawBody !== "object") {
    throw new Error("invalid token response payload");
  }

  // gateway shape
  // { success: true, data: {...} }
  if (rawBody.success === true && rawBody.data && typeof rawBody.data === "object") {
    return rawBody.data;
  }

  // compatible shape
  if (rawBody.code === "200" && rawBody.data && typeof rawBody.data === "object") {
    return rawBody.data;
  }

  if (rawBody.data && typeof rawBody.data === "object" && rawBody.data.username && rawBody.data.password) {
    return rawBody.data;
  }

  throw new Error(`unexpected token response shape: ${JSON.stringify(rawBody).slice(0, 300)}`);
}

class MqttTokenClient {
  constructor(cfg) {
    this.cfg = cfg;
    this.cache = new Map();
  }

  buildClientId(agentId) {
    return `${this.cfg.mqttClientGroupId || "GID_agent"}@@@${agentId}`;
  }

  shouldReuse(cached, forceRefresh) {
    if (forceRefresh || !cached) return false;
    const expireTime = Number(cached.expire_time || 0);
    if (!Number.isFinite(expireTime) || expireTime <= 0) return false;
    const threshold = Number(this.cfg.mqttTokenRefreshThresholdMs || 60 * 60 * 1000);
    return expireTime - nowMs() > threshold;
  }

  async requestToken({ agentId, agentSecret, clientId }) {
    const apiPath = String(this.cfg.mqttTokenPath || "/mqtt-token/api/v1/token");
    const signPath = String(this.cfg.mqttTokenSignPath || "").trim() || apiPath;
    const timestampSec = Math.floor(nowMs() / 1000);
    const signature = computeHttpSignature({
      secret: agentSecret,
      method: "POST",
      path: signPath,
      agentId,
      timestampSec,
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const tokenBaseUrl = this.cfg.mqttTokenBaseUrl || this.cfg.baseUrl;
      const response = await fetch(`${tokenBaseUrl}${apiPath}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Agent-Id": agentId,
          "X-Timestamp": String(timestampSec),
          "X-Agent-Signature": signature,
        },
        body: JSON.stringify({ client_id: clientId }),
        signal: controller.signal,
      });
      const raw = await response.text();
      if (!response.ok) {
        throw new Error(`status=${response.status} body=${raw.slice(0, 300)}`);
      }
      const parsed = raw.trim() ? JSON.parse(raw) : {};
      return parseTokenResponse(parsed);
    } finally {
      clearTimeout(timeout);
    }
  }

  async getToken({ agentId, agentSecret, clientId, forceRefresh }) {
    const resolvedClientId = String(clientId || this.buildClientId(agentId)).trim();
    if (!resolvedClientId) {
      throw new Error("clientId is required");
    }
    const cacheKey = `${agentId}::${resolvedClientId}`;
    const cached = this.cache.get(cacheKey);
    if (this.shouldReuse(cached, forceRefresh)) {
      return { ...cached, source: "cache" };
    }

    // Remove expired/stale cache entry to prevent memory leak
    if (cached) {
      this.cache.delete(cacheKey);
    }

    const fresh = await this.requestToken({
      agentId,
      agentSecret,
      clientId: resolvedClientId,
    });
    const normalized = {
      client_id: fresh.client_id || resolvedClientId,
      instance_id: fresh.instance_id || "",
      username: fresh.username || "",
      password: fresh.password || "",
      token: fresh.token || "",
      expire_time: Number(fresh.expire_time || 0),
    };
    this.cache.set(cacheKey, normalized);
    return { ...normalized, source: "remote" };
  }
}

module.exports = {
  MqttTokenClient,
  parseTokenResponse,
};
