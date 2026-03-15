const os = require("node:os");
const path = require("node:path");

const A2HMARKET_ROOT = path.resolve(__dirname, "../../../..");
const DEFAULT_DB_PATH = path.join(A2HMARKET_ROOT, "runtime", "store", "a2hmarket_listener.db");
const DEFAULT_CONFIG_PATH = path.join(A2HMARKET_ROOT, "config", "config.sh");
const DEFAULT_PID_PATH = path.join(A2HMARKET_ROOT, "runtime", "store", "listener.pid");
const DEFAULT_LOCK_PATH = path.join(A2HMARKET_ROOT, "runtime", "store", "a2hmarket_listener.lock");
const DEFAULT_LOG_PATH = path.join(A2HMARKET_ROOT, "runtime", "logs", "listener.log");

function resolveDbPath(input) {
  const raw = String(input || process.env.A2HMARKET_DB_PATH || DEFAULT_DB_PATH).trim();
  if (!raw) return DEFAULT_DB_PATH;
  if (path.isAbsolute(raw)) return raw;
  return path.resolve(process.cwd(), raw);
}

function resolvePath(input, fallbackAbsolutePath) {
  const raw = String(input || fallbackAbsolutePath).trim();
  if (!raw) return fallbackAbsolutePath;
  if (path.isAbsolute(raw)) return raw;
  return path.resolve(process.cwd(), raw);
}

module.exports = {
  A2HMARKET_ROOT,
  DEFAULT_DB_PATH,
  DEFAULT_CONFIG_PATH,
  DEFAULT_PID_PATH,
  DEFAULT_LOCK_PATH,
  DEFAULT_LOG_PATH,
  resolveDbPath,
  resolvePath,
};
