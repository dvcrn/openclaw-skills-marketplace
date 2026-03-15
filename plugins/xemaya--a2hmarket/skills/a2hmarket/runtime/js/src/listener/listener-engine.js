const { EventStore, nowMs } = require("../store/event-store");
const { flushPushOutbox } = require("./push-dispatcher");
const { flushA2aOutbox } = require("./a2a-outbox-dispatcher");
const { acquireSingleInstanceLock } = require("./lock");
const { startA2aService } = require("../a2a/service");


async function runListener(cfg, options) {
  const store = new EventStore(cfg.dbPath).open();
  const once = Boolean(options && options.once);
  const logger = options.logger;
  const lock = acquireSingleInstanceLock(cfg.lockPath);
  const a2aService = await startA2aService({ cfg, store, logger });
  let stopRequested = false;
  let consecutiveFailures = 0;
  const MAX_CONSECUTIVE_FAILURES = 10;

  const stop = () => {
    stopRequested = true;
  };
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);

  logger.info(
    `listener started (a2a-only) db=${cfg.dbPath} flush_interval_ms=${cfg.pollIntervalMs || 5000} push_enabled=${cfg.pushEnabled} session_id=${cfg.pushEnabled ? cfg.openclawSessionId : "-"}`
  );
  try {
    while (!stopRequested) {
      const start = nowMs();
      let stats = {
        pushDispatched: 0,
        pushAcked: 0,
        pushRetried: 0,
        pushSkipped: 0,
        a2aSent: 0,
        a2aRetried: 0,
      };
      
      try {
        const pushStats = await flushPushOutbox(store, cfg, logger);
        stats.pushDispatched = pushStats.dispatched;
        stats.pushAcked = pushStats.acked;
        stats.pushRetried = pushStats.retried;
        stats.pushSkipped = pushStats.skipped || 0;
        consecutiveFailures = 0;
      } catch (err) {
        consecutiveFailures++;
        logger.error(`flush push outbox failed: ${(err && err.message) || String(err)}`);
        if (isCriticalError(err) || consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
          logger.error(`critical error or too many failures (${consecutiveFailures}/${MAX_CONSECUTIVE_FAILURES}), stopping listener`);
          throw err;
        }
      }
      
      try {
        const a2aStats = await flushA2aOutbox(store, cfg, logger, {
          publish: a2aService.publishEnvelope,
        });
        stats.a2aSent = a2aStats.sent;
        stats.a2aRetried = a2aStats.retried;
        consecutiveFailures = 0;
      } catch (err) {
        consecutiveFailures++;
        logger.error(`flush a2a outbox failed: ${(err && err.message) || String(err)}`);
        if (isCriticalError(err) || consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
          logger.error(`critical error or too many failures (${consecutiveFailures}/${MAX_CONSECUTIVE_FAILURES}), stopping listener`);
          throw err;
        }
      }
      
      if (stats.pushDispatched > 0 || stats.pushAcked > 0 || stats.pushRetried > 0 || stats.pushSkipped > 0 || stats.a2aSent > 0 || stats.a2aRetried > 0) {
        logger.info(
          `cycle done dispatched=${stats.pushDispatched} acked=${stats.pushAcked} retried=${stats.pushRetried} skipped=${stats.pushSkipped} a2a_sent=${stats.a2aSent} a2a_retried=${stats.a2aRetried}`
        );
      }

      if (once) break;
      const elapsed = nowMs() - start;
      const flushIntervalMs = cfg.pollIntervalMs || 5000;
      const sleepMs = Math.max(100, flushIntervalMs - elapsed);
      await new Promise((resolve) => setTimeout(resolve, sleepMs));
    }
  } finally {
    await a2aService.stop();
    store.close();
    lock.release();
    logger.info("listener stopped");
  }
  return 0;
}

function isCriticalError(err) {
  const msg = String((err && err.message) || "");
  if (msg.includes("database is locked")) return true;
  if (msg.includes("SQLITE_FULL")) return true;
  if (msg.includes("EACCES")) return true;
  if (msg.includes("ENOSPC")) return true;
  return false;
}

module.exports = {
  runListener,
};
