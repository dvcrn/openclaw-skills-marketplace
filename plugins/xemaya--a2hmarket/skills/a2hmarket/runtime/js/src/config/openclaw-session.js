const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const DEFAULT_OPENCLAW_SESSION_KEY = "a2hmarket:main:main";
const DEFAULT_OPENCLAW_SESSION_LABEL = "A2HMarket Main Session";

function looksLikeSessionKey(value) {
  return /^[^:\s]+(?::[^:\s]+){2,}$/.test(String(value || "").trim());
}

function looksLikeUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    String(value || "").trim()
  );
}

function parseJsonFromOutput(raw) {
  const text = String(raw || "").trim();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    // Some OpenClaw builds may prepend warning lines; extract the first JSON object.
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start < 0 || end <= start) return null;
    const sliced = text.slice(start, end + 1);
    try {
      return JSON.parse(sliced);
    } catch {
      return null;
    }
  }
}

function resolveOpenclawCommand(openclawBin, openclawNodeScript) {
  if (openclawNodeScript) {
    const abs = path.resolve(openclawNodeScript);
    if (!fs.existsSync(abs)) {
      throw new Error(`A2HMARKET_OPENCLAW_NODE_SCRIPT not found: ${abs}`);
    }
    return ["node", abs];
  }
  return [openclawBin || "openclaw"];
}

function ensureOpenclawSessionBinding(options) {
  const openclawCommand = Array.isArray(options && options.openclawCommand)
    ? options.openclawCommand
    : ["openclaw"];
  const sessionKey = String(options && options.sessionKey ? options.sessionKey : "").trim();
  const sessionLabel = String(
    options && options.sessionLabel ? options.sessionLabel : DEFAULT_OPENCLAW_SESSION_LABEL
  ).trim();
  const timeoutMs = Number.isFinite(options && options.timeoutMs)
    ? Math.max(1000, Number(options.timeoutMs))
    : 15000;
  const execFn = options && typeof options.execFn === "function" ? options.execFn : spawnSync;

  if (!sessionKey) {
    return { ok: false, detail: "missing session key", sessionId: "", canonicalKey: "" };
  }
  if (!looksLikeSessionKey(sessionKey)) {
    return {
      ok: false,
      detail: `invalid session key format: ${sessionKey}. expected <namespace>:<profile>:<name>`,
      sessionId: "",
      canonicalKey: "",
    };
  }

  const runPatch = (paramsPayload) => {
    const params = JSON.stringify(paramsPayload);
    const command = [
      ...openclawCommand,
      "gateway",
      "call",
      "sessions.patch",
      "--params",
      params,
      "--json",
    ];
    let result;
    try {
      result = execFn(command[0], command.slice(1), {
        encoding: "utf8",
        timeout: timeoutMs,
        maxBuffer: 1024 * 1024,
      });
    } catch (err) {
      return {
        ok: false,
        detail: String((err && err.message) || err),
        parsed: null,
      };
    }

    const output = `${result.stdout || ""}\n${result.stderr || ""}`.trim();
    if (result.error) {
      return {
        ok: false,
        detail: String(result.error.message || result.error),
        parsed: null,
      };
    }
    if (result.status !== 0) {
      return {
        ok: false,
        detail: output || `exit=${result.status}`,
        parsed: null,
      };
    }
    const parsed = parseJsonFromOutput(result.stdout || output);
    if (!parsed || typeof parsed !== "object") {
      return {
        ok: false,
        detail: `failed to parse sessions.patch output: ${output.slice(0, 300)}`,
        parsed: null,
      };
    }
    return {
      ok: true,
      detail: "",
      parsed,
    };
  };

  let patched = runPatch({
    key: sessionKey,
    label: sessionLabel || DEFAULT_OPENCLAW_SESSION_LABEL,
  });
  if (!patched.ok && /label already in use/i.test(String(patched.detail || ""))) {
    patched = runPatch({ key: sessionKey });
  }
  if (!patched.ok) {
    return {
      ok: false,
      detail: patched.detail,
      sessionId: "",
      canonicalKey: "",
    };
  }

  const canonicalKey = String((patched.parsed && patched.parsed.key) || "").trim() || sessionKey;
  const sessionId = String(
    (patched.parsed && patched.parsed.entry && patched.parsed.entry.sessionId) || ""
  ).trim();
  if (!sessionId || !looksLikeUuid(sessionId)) {
    return {
      ok: false,
      detail: `sessions.patch returned invalid sessionId for key=${canonicalKey}`,
      sessionId: "",
      canonicalKey,
    };
  }

  return {
    ok: true,
    detail: "",
    sessionId,
    canonicalKey,
    raw: patched.parsed,
  };
}

function getOpenclawSessionStatePath(homeDir) {
  const root = String(homeDir || process.env.HOME || os.homedir() || "").trim();
  if (!root) return "";
  return path.join(root, ".a2hmarket", "state", "openclaw-session.json");
}

function writeOpenclawSessionState(payload, options) {
  const filePath = getOpenclawSessionStatePath(options && options.homeDir);
  if (!filePath) return "";
  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
    return filePath;
  } catch {
    return "";
  }
}

module.exports = {
  DEFAULT_OPENCLAW_SESSION_KEY,
  DEFAULT_OPENCLAW_SESSION_LABEL,
  looksLikeSessionKey,
  looksLikeUuid,
  resolveOpenclawCommand,
  ensureOpenclawSessionBinding,
  getOpenclawSessionStatePath,
  writeOpenclawSessionState,
};
