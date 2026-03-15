const { nowMs } = require("../store/event-store");
const { coerceInt } = require("./message-utils");

function calculateBackoffMs(attempt, maxDelayMs) {
  const normalizedAttempt = Math.max(1, Math.min(10, coerceInt(attempt, 1)));
  const base = 1000 * 2 ** (normalizedAttempt - 1);
  const capped = Math.min(base, coerceInt(maxDelayMs, 60 * 1000));
  return Math.max(1000, capped);
}

async function flushA2aOutbox(store, cfg, logger, options) {
  const publish = options && typeof options.publish === "function" ? options.publish : null;
  if (!publish) {
    return { sent: 0, retried: 0 };
  }
  const nowFn = options && typeof options.now === "function" ? options.now : nowMs;
  const batchSize = coerceInt(cfg.a2aOutboxBatchSize, 50);
  const rows = store.listPendingA2aOutbox({
    now: nowFn(),
    batchSize,
  });

  let sent = 0;
  let retried = 0;
  for (const row of rows) {
    try {
      logger.info(
        `a2a outbox dispatching message_id=${row.message_id} target_id=${row.target_agent_id} message_type=${row.message_type} attempt=${row.attempt || 0}`
      );
      logger.debug(`a2a outbox envelope: ${JSON.stringify(row.envelope).slice(0, 500)}`);
      await publish(row.target_agent_id, row.envelope, row.qos);
      store.markA2aOutboxSent({ id: row.id });
      sent += 1;
      logger.info(
        `a2a outbox sent successfully message_id=${row.message_id} target_id=${row.target_agent_id} message_type=${row.message_type}`
      );
    } catch (err) {
      const nextAttempt = coerceInt(row.attempt, 0) + 1;
      const delayMs = calculateBackoffMs(nextAttempt, cfg.a2aOutboxRetryMaxDelayMs);
      const nextRetryAt = nowFn() + delayMs;
      const detail = (err && err.message) || String(err);
      store.markA2aOutboxRetry({
        id: row.id,
        attempt: nextAttempt,
        nextRetryAt,
        lastError: detail,
      });
      retried += 1;
      logger.warn(
        `a2a outbox retry message_id=${row.message_id} attempt=${nextAttempt} retry_in_ms=${delayMs} detail=${String(detail).slice(0, 200)}`
      );
    }
  }

  return { sent, retried };
}

module.exports = {
  flushA2aOutbox,
  calculateBackoffMs,
};
