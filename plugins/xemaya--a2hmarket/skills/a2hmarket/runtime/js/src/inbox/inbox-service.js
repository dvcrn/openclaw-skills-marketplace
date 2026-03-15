const { resolveDbPath } = require("../config/paths");
const { EventStore, nowMs } = require("../store/event-store");

function coerceInt(value, fallback, min, max) {
  const n = Number.parseInt(String(value), 10);
  let out = Number.isFinite(n) ? n : fallback;
  if (Number.isFinite(min)) out = Math.max(min, out);
  if (Number.isFinite(max)) out = Math.min(max, out);
  return out;
}

async function pull({ dbPath, consumerId, cursor, maxEvents, waitMs, pollIntervalMs }) {
  const store = new EventStore(resolveDbPath(dbPath)).open();
  try {
    const normalizedConsumer = String(consumerId || "default");
    const normalizedCursor = coerceInt(cursor, 0, 0);
    const normalizedLimit = coerceInt(maxEvents, 20, 1, 200);
    const normalizedWait = coerceInt(waitMs, 0, 0, 300000);
    const normalizedPollInterval = coerceInt(pollIntervalMs, 300, 50, 10000);
    const deadline = nowMs() + normalizedWait;

    while (true) {
      const events = store.pullEvents({
        consumerId: normalizedConsumer,
        cursor: normalizedCursor,
        limit: normalizedLimit,
      });

      if (events.length > 0) {
        return {
          ok: true,
          consumer_id: normalizedConsumer,
          cursor: events[events.length - 1].seq,
          events,
        };
      }

      if (nowMs() >= deadline) {
        return {
          ok: true,
          consumer_id: normalizedConsumer,
          cursor: normalizedCursor,
          events: [],
        };
      }

      await new Promise((resolve) => setTimeout(resolve, normalizedPollInterval));
    }
  } finally {
    store.close();
  }
}

async function ack({ dbPath, consumerId, eventId }) {
  const store = new EventStore(resolveDbPath(dbPath)).open();
  try {
    const normalizedConsumer = String(consumerId || "default");
    const normalizedEventId = String(eventId || "").trim();
    if (!normalizedEventId) {
      throw new Error("event_id is required");
    }

    const ackedAt = store.ackEvent({
      consumerId: normalizedConsumer,
      eventId: normalizedEventId,
    });
    return {
      ok: true,
      consumer_id: normalizedConsumer,
      event_id: normalizedEventId,
      acked_at: ackedAt,
    };
  } finally {
    store.close();
  }
}

async function peek({ dbPath, consumerId }) {
  const store = new EventStore(resolveDbPath(dbPath)).open();
  try {
    const normalizedConsumer = String(consumerId || "default");
    const result = store.peekUnread({ consumerId: normalizedConsumer });
    return {
      ok: true,
      consumer_id: normalizedConsumer,
      unread: result.unread,
      pending_push: result.pending_push,
    };
  } finally {
    store.close();
  }
}

module.exports = {
  pull,
  ack,
  peek,
};
