const fs = require("node:fs");
const { execFileSync } = require("node:child_process");
const { EventStore } = require("../store/event-store");

function isProcessRunning(pid) {
  if (!Number.isFinite(pid) || pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function getProcessCommand(pid) {
  try {
    return String(
      execFileSync("ps", ["-p", String(pid), "-o", "command="], {
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"],
      })
    ).trim();
  } catch {
    return "";
  }
}

function isListenerProcess(pid) {
  if (!isProcessRunning(pid)) return false;
  const cmd = getProcessCommand(pid);
  if (!cmd) return false;
  return /\ba2hmarket\.js\b/.test(cmd) && /\blistener\b/.test(cmd) && /\brun\b/.test(cmd);
}

function getListenerProcess(lockPath) {
  if (!lockPath || !fs.existsSync(lockPath)) {
    return { running: false, pid: 0 };
  }
  let raw = "";
  try {
    raw = fs.readFileSync(lockPath, "utf8");
  } catch {
    return { running: false, pid: 0 };
  }
  const pid = Number.parseInt(String(raw || "").trim(), 10);
  if (!Number.isFinite(pid) || pid <= 0) {
    return { running: false, pid: 0 };
  }
  return {
    running: isListenerProcess(pid),
    pid,
  };
}

function enqueueOutboundEnvelope({ cfg, targetAgentId, messageType, qos, envelope }) {
  const store = new EventStore(cfg.dbPath).open();
  try {
    const messageId = String((envelope && envelope.message_id) || "").trim();
    if (!messageId) {
      throw new Error("envelope.message_id is required");
    }
    const result = store.enqueueA2aOutbox({
      message_id: messageId,
      target_agent_id: String(targetAgentId || "").trim(),
      message_type: String(messageType || "").trim(),
      qos: Number.parseInt(String(qos == null ? 1 : qos), 10),
      envelope: envelope || {},
    });
    return result;
  } finally {
    store.close();
  }
}

module.exports = {
  getListenerProcess,
  enqueueOutboundEnvelope,
};
