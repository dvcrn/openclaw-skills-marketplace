const { spawn } = require("node:child_process");
const { nowMs } = require("../store/event-store");
const { formatSystemEventText, coerceInt } = require("./message-utils");

function calculateBackoffMs(attempt, maxDelayMs) {
  const normalizedAttempt = Math.max(1, Math.min(10, coerceInt(attempt, 1)));
  const base = 1000 * 2 ** (normalizedAttempt - 1);
  const capped = Math.min(base, coerceInt(maxDelayMs, 5 * 60 * 1000));
  return Math.max(1000, capped);
}

async function runOpenclawPush(cfg, text) {
  const timeoutSec = Math.max(30, coerceInt(cfg.openclawPushTimeoutSec, 120));
  const command = [
    ...cfg.openclawCommand,
    "agent",
    "--session-id",
    cfg.openclawSessionId,
    "--thinking",
    cfg.openclawPushThinking || "off",
    "--timeout",
    String(timeoutSec),
    "--message",
    text,
    "--json",
  ];
  const started = nowMs();
  
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let timeoutHandle = null;
    let exited = false;
    
    const child = spawn(command[0], command.slice(1), {
      encoding: "utf8",
      maxBuffer: 1024 * 1024,
    });
    
    const cleanup = () => {
      if (timeoutHandle) {
        clearTimeout(timeoutHandle);
        timeoutHandle = null;
      }
      if (!exited) {
        exited = true;
        try {
          child.kill("SIGTERM");
        } catch {}
      }
    };
    
    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });
    
    child.on("error", (err) => {
      cleanup();
      const elapsed = nowMs() - started;
      resolve({
        ok: false,
        detail: `elapsed_ms=${elapsed} ${err.message || String(err)}`.trim(),
      });
    });
    
    child.on("exit", (code) => {
      cleanup();
      exited = true;
      const elapsed = nowMs() - started;
      const output = `${stdout}\n${stderr}`.trim();
      
      if (code === 0) {
        resolve({ ok: true, detail: `elapsed_ms=${elapsed} ${output}`.trim() });
      } else {
        resolve({ ok: false, detail: `elapsed_ms=${elapsed} ${output || `exit=${code}`}`.trim() });
      }
    });
    
    timeoutHandle = setTimeout(() => {
      if (!exited) {
        cleanup();
        const elapsed = nowMs() - started;
        resolve({
          ok: false,
          detail: `elapsed_ms=${elapsed} timeout after ${timeoutSec}s`.trim(),
        });
      }
    }, (timeoutSec + 10) * 1000);
  });
}

async function flushPushOutbox(store, cfg, logger, options) {
  if (!cfg.pushEnabled) {
    return { dispatched: 0, acked: 0, retried: 0, skipped: 0 };
  }
  const nowFn = options && typeof options.now === "function" ? options.now : nowMs;
  const pushFn = options && typeof options.push === "function" ? options.push : runOpenclawPush;
  const tsNow = nowFn();
  const pushBatchSize = coerceInt(cfg.pushBatchSize, 20);
  const ackConsumer = String(cfg.pushAckConsumer || "openclaw");
  const ackWaitMs = Math.max(1000, coerceInt(cfg.pushAckWaitMs, 15000));
  const pushOnce = cfg.pushOnce !== false;
  let dispatched = 0;
  let acked = 0;
  let retried = 0;
  let skipped = 0;

  // Reconcile outbox items that were already dispatched.
  const sentRows = store.listSentPushOutbox({
    batchSize: pushBatchSize,
  });
  for (const row of sentRows) {
    if (store.isEventAckedByConsumer({ consumerId: ackConsumer, eventId: row.event_id })) {
      store.markPushAcked({
        outboxId: row.outbox_id,
        eventId: row.event_id,
      });
      acked += 1;
      continue;
    }

    if (pushOnce) {
      store.markPushAcked({
        outboxId: row.outbox_id,
        eventId: row.event_id,
      });
      skipped += 1;
      logger.debug(
        `push skipped (push_once=true) event_id=${row.event_id} attempt=${row.attempt} consumer=${ackConsumer}`
      );
      continue;
    }

    const deadline = coerceInt(row.next_retry_at, 0);
    if (deadline > tsNow) continue;

    const nextAttempt = coerceInt(row.attempt, 0) + 1;
    const delayMs = calculateBackoffMs(nextAttempt, cfg.pushRetryMaxDelayMs);
    const nextRetryAt = nowFn() + delayMs;
    store.markPushRetry({
      outboxId: row.outbox_id,
      attempt: nextAttempt,
      nextRetryAt,
      lastError: `ack timeout consumer=${ackConsumer} wait_ms=${Math.max(0, tsNow - coerceInt(row.updated_at, tsNow))}`,
    });
    retried += 1;
    logger.warn(
      `push ack timeout event_id=${row.event_id} attempt=${nextAttempt} retry_in_ms=${delayMs} consumer=${ackConsumer}`
    );
  }

  // Dispatch pending/retry rows. Mark success only after ACK is observed.
  const rows = store.listPendingPushOutbox({
    now: nowFn(),
    batchSize: pushBatchSize,
  });
  for (const row of rows) {
    if (store.isEventAckedByConsumer({ consumerId: ackConsumer, eventId: row.event_id })) {
      store.markPushAcked({
        outboxId: row.outbox_id,
        eventId: row.event_id,
      });
      acked += 1;
      continue;
    }

    const text = formatSystemEventText(row);
    const result = await pushFn(cfg, text);
    if (result.ok) {
      store.markPushSent({
        outboxId: row.outbox_id,
        eventId: row.event_id,
        ackDeadlineAt: nowFn() + ackWaitMs,
      });
      dispatched += 1;
      logger.info(
        `push dispatched event_id=${row.event_id} consumer=${ackConsumer} ack_wait_ms=${ackWaitMs}`
      );
      continue;
    }

    const nextAttempt = coerceInt(row.attempt, 0) + 1;
    const delayMs = calculateBackoffMs(nextAttempt, cfg.pushRetryMaxDelayMs);
    const nextRetryAt = nowFn() + delayMs;
    store.markPushRetry({
      outboxId: row.outbox_id,
      attempt: nextAttempt,
      nextRetryAt,
      lastError: result.detail,
    });
    retried += 1;
    logger.warn(
      `push failed event_id=${row.event_id} attempt=${nextAttempt} retry_in_ms=${delayMs} detail=${result.detail.slice(0, 200)}`
    );
  }

  return { dispatched, acked, retried, skipped };
}

module.exports = {
  flushPushOutbox,
  calculateBackoffMs,
};
