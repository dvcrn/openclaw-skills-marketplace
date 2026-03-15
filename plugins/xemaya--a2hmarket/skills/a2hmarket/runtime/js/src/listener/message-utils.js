const { sha256Hex } = require("../auth/signer");

function coerceInt(value, fallback) {
  const n = Number.parseInt(String(value), 10);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeText(value) {
  if (typeof value === "string") return value;
  if (value == null) return "";
  if (Array.isArray(value) || typeof value === "object") {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

function sanitizePreview(text, maxChars) {
  const compact = String(text || "")
    .replace(/\r/g, " ")
    .replace(/\n/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const limit = Number.isFinite(maxChars) ? maxChars : 80;
  if (compact.length <= limit) return compact;
  return `${compact.slice(0, Math.max(0, limit - 3))}...`;
}

function toEventHash({ peerId, messageTs, messageText, messageId }) {
  if (messageId) return sha256Hex(`id:${messageId}`);
  return sha256Hex(`${peerId}|${messageTs}|${messageText}`);
}

function formatSystemEventText(event) {
  const preview = sanitizePreview(event.preview, 100);
  return [
    "【待处理A2A消息】",
    `event_id: ${event.event_id}`,
    `from_agent: ${event.peer_id}`,
    `message_type: ${event.source || 'MQTT'}`,
    `preview: ${preview}`,
    "请严格按以下流程处理：",
    "1) 使用 inbox.pull 拉取事件，获取完整的 A2A 消息内容；",
    "2) 解析 A2A 消息的 payload，提取 ANP 协商信息或其他业务数据；",
    "3) 根据消息类型决定响应策略（自动接受、拒绝、暂停或人工审核）；",
    "4) 使用 a2a.send 或 anp 命令发送响应消息到对方 Agent；",
    `5) 处理完成后调用 inbox.ack（event_id=${event.event_id}）标记已处理。`,
  ].join("\n");
}

module.exports = {
  coerceInt,
  normalizeText,
  sanitizePreview,
  toEventHash,
  formatSystemEventText,
};
