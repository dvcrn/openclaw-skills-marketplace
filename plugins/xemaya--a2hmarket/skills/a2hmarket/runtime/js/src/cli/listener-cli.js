const { resolveListenerConfig } = require("../config/loader");
const { runListener } = require("../listener/listener-engine");
const { parseOptions } = require("./arg-parser");
const { createLogger } = require("../listener/logger");
const { checkListenerStatus, cleanStaleLock } = require("../listener/lock");
const { DEFAULT_LOCK_PATH, resolvePath } = require("../config/paths");

function printUsage() {
  process.stdout.write(
    [
      "Usage:",
      "  a2hmarket listener run [--once] [--verbose]  # 启动 listener",
      "  a2hmarket listener status                    # 查看运行状态",
      "  a2hmarket listener clean                     # 清理过期锁文件",
    ].join("\n") + "\n"
  );
}

function statusListenerCli() {
  let lockPath = DEFAULT_LOCK_PATH;
  try {
    const cfg = resolveListenerConfig();
    lockPath = cfg.lockPath;
  } catch (err) {
    lockPath = resolvePath(process.env.A2HMARKET_LISTENER_LOCK_FILE, DEFAULT_LOCK_PATH);
  }
  
  try {
    const status = checkListenerStatus(lockPath);
    
    if (status.running) {
      process.stdout.write(
        `Listener 状态: 运行中\n` +
        `进程 PID: ${status.pid}\n` +
        `锁文件: ${status.lockPath}\n`
      );
      return 0;
    } else if (status.stale) {
      process.stdout.write(
        `Listener 状态: 未运行（存在过期锁文件）\n` +
        `锁文件: ${status.lockPath}\n` +
        `提示: 运行 'a2hmarket listener clean' 清理过期锁\n`
      );
      return 1;
    } else {
      process.stdout.write(
        `Listener 状态: 未运行\n`
      );
      return 1;
    }
  } catch (err) {
    process.stderr.write(`[a2hmarket-listener] ${err && err.message ? err.message : String(err)}\n`);
    return 1;
  }
}

function cleanListenerCli() {
  let lockPath = DEFAULT_LOCK_PATH;
  try {
    const cfg = resolveListenerConfig();
    lockPath = cfg.lockPath;
  } catch (err) {
    lockPath = resolvePath(process.env.A2HMARKET_LISTENER_LOCK_FILE, DEFAULT_LOCK_PATH);
  }
  
  try {
    const cleaned = cleanStaleLock(lockPath);
    if (cleaned) {
      process.stdout.write(`已清理过期锁文件: ${lockPath}\n`);
    } else {
      process.stdout.write(`无需清理（listener 正在运行或锁文件不存在）\n`);
    }
    return 0;
  } catch (err) {
    process.stderr.write(`[a2hmarket-listener] ${err && err.message ? err.message : String(err)}\n`);
    return 1;
  }
}

async function runListenerCli(args) {
  const command = args[0];
  
  if (command === 'status') {
    return statusListenerCli();
  }
  
  if (command === 'clean') {
    return cleanListenerCli();
  }
  
  const options = parseOptions(args.slice(1));
  if (!command || command !== "run" || options.help || options.h) {
    printUsage();
    return 1;
  }

  try {
    const cfg = resolveListenerConfig();
    
    const status = checkListenerStatus(cfg.lockPath);
    if (status.running) {
      process.stderr.write(
        `[a2hmarket-listener] 错误：listener 已在运行\n` +
        `  进程 PID: ${status.pid}\n` +
        `  锁文件: ${status.lockPath}\n\n` +
        `如需停止现有实例，请运行:\n` +
        `  kill ${status.pid}\n` +
        `或使用:\n` +
        `  ./a2hmarket/scripts/a2hmarket-ops.sh stop\n\n`
      );
      return 1;
    }
    
    if (status.stale) {
      process.stderr.write(
        `[a2hmarket-listener] 警告：发现过期锁文件，已自动清理\n`
      );
      cleanStaleLock(cfg.lockPath);
    }
    
    const logger = createLogger(Boolean(options.verbose));
    logger.info(`credential source=static agent_id=${cfg.agentId}`);
    if (cfg.pushEnabled && cfg.openclawSessionKey) {
      logger.info(
        `openclaw session resolved key=${cfg.openclawSessionKey} canonical=${cfg.openclawSessionKeyCanonical || cfg.openclawSessionKey} session_id=${cfg.openclawSessionId}`
      );
    } else if (!cfg.pushEnabled && cfg.openclawSessionBootstrapError) {
      logger.warn(`openclaw push disabled: ${cfg.openclawSessionBootstrapError}`);
    }
    const code = await runListener(cfg, {
      once: Boolean(options.once),
      logger,
    });
    return code;
  } catch (err) {
    process.stderr.write(`[a2hmarket-listener] ${err && err.message ? err.message : String(err)}\n`);
    return 1;
  }
}

module.exports = {
  runListenerCli,
};
