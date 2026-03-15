const fs = require("node:fs");
const path = require("node:path");
const { DatabaseSync } = require("node:sqlite");
const { applySchema } = require("./schema");

function nowMs() {
  return Date.now();
}

function coerceInt(value, fallback) {
  const n = Number.parseInt(String(value), 10);
  return Number.isFinite(n) ? n : fallback;
}

function isUniqueConstraint(err) {
  const msg = String((err && err.message) || "");
  return msg.includes("UNIQUE constraint failed");
}

function parseJsonSafe(raw, fallback) {
  try {
    return JSON.parse(String(raw || ""));
  } catch {
    return fallback;
  }
}

class EventStore {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  open() {
    if (this.db) return this;
    fs.mkdirSync(path.dirname(this.dbPath), { recursive: true });
    this.db = new DatabaseSync(this.dbPath);
    this.db.exec("PRAGMA busy_timeout = 5000");
    applySchema(this.db);
    return this;
  }

  close() {
    if (!this.db) return;
    this.db.close();
    this.db = null;
  }

  insertEvent(input) {
    const tsNow = coerceInt(input.created_at, nowMs());
    const stmt = this.db.prepare(`
      INSERT INTO message_event(
        event_id, peer_id, message_id, msg_ts, hash, unread_count, preview, payload_json,
        state, source, a2a_message_id, created_at, updated_at
      ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      String(input.event_id),
      String(input.peer_id),
      input.message_id == null ? null : String(input.message_id),
      coerceInt(input.msg_ts, 0),
      String(input.hash || ""),
      coerceInt(input.unread_count, 0),
      String(input.preview || ""),
      JSON.stringify(input.payload || {}),
      String(input.state || "NEW"),
      String(input.source || "MQTT"),
      input.a2a_message_id == null ? null : String(input.a2a_message_id),
      tsNow,
      coerceInt(input.updated_at, tsNow)
    );
  }

  insertIncomingEvent(input) {
    const eventId = String(input.event_id);
    const tsNow = nowMs();
    
    this.db.exec("BEGIN");
    try {
      try {
        this.db.prepare(`
          INSERT INTO message_event(
            event_id, peer_id, message_id, msg_ts, hash, unread_count, preview, payload_json,
            state, source, a2a_message_id, created_at, updated_at
          ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
          eventId,
          String(input.peer_id),
          input.message_id == null ? null : String(input.message_id),
          coerceInt(input.msg_ts, 0),
          String(input.hash || ""),
          coerceInt(input.unread_count, 0),
          String(input.preview || ""),
          JSON.stringify(input.payload || {}),
          String(input.state || "NEW"),
          String(input.source || "MQTT"),
          input.a2a_message_id == null ? null : String(input.a2a_message_id),
          coerceInt(input.created_at, tsNow),
          coerceInt(input.updated_at, tsNow)
        );
      } catch (err) {
        if (isUniqueConstraint(err)) {
          this.db.exec("ROLLBACK");
          return { created: false, eventId, reason: "event_exists" };
        }
        throw err;
      }

      if (input.push_enabled) {
        try {
          this.db.prepare(`
            INSERT INTO push_outbox(
              event_id, target, attempt, next_retry_at, status, created_at, updated_at
            ) VALUES(?, ?, 0, ?, 'PENDING', ?, ?)
          `).run(
            eventId,
            String(input.push_target || "openclaw"),
            tsNow,
            tsNow,
            tsNow
          );
        } catch (err) {
          if (isUniqueConstraint(err)) {
            this.db.exec("ROLLBACK");
            return { created: false, eventId, reason: "push_outbox_conflict" };
          }
          throw err;
        }
      }
      
      this.db.exec("COMMIT");
      return { created: true, eventId };
    } catch (err) {
      this.db.exec("ROLLBACK");
      throw err;
    }
  }

  pullEvents({ consumerId, cursor, limit }) {
    const stmt = this.db.prepare(`
      SELECT
        e.seq,
        e.event_id,
        e.peer_id,
        e.message_id,
        e.msg_ts,
        e.unread_count,
        e.preview,
        e.payload_json,
        e.state,
        e.created_at,
        e.updated_at
      FROM message_event e
      LEFT JOIN consumer_ack a
        ON a.event_id = e.event_id
       AND a.consumer_id = ?
      WHERE e.seq > ?
        AND a.event_id IS NULL
      ORDER BY e.seq ASC
      LIMIT ?
    `);
    const rows = stmt.all(String(consumerId), coerceInt(cursor, 0), coerceInt(limit, 20));
    return rows.map((row) => {
      let payload = {};
      try {
        payload = JSON.parse(row.payload_json || "{}");
      } catch {
        payload = { raw: row.payload_json || "" };
      }
      return {
        seq: coerceInt(row.seq, 0),
        event_id: String(row.event_id),
        peer_id: String(row.peer_id),
        message_id: row.message_id == null ? null : String(row.message_id),
        msg_ts: coerceInt(row.msg_ts, 0),
        unread_count: coerceInt(row.unread_count, 0),
        preview: String(row.preview || ""),
        state: String(row.state || ""),
        created_at: coerceInt(row.created_at, 0),
        updated_at: coerceInt(row.updated_at, 0),
        payload,
      };
    });
  }

  ackEvent({ consumerId, eventId }) {
    const ts = nowMs();
    
    const exists = this.db.prepare(`
      SELECT 1 FROM message_event WHERE event_id = ?
    `).get(String(eventId));
    
    if (!exists) {
      throw new Error(`cannot ack non-existent event: ${eventId}`);
    }
    
    this.db.prepare(`
      INSERT OR IGNORE INTO consumer_ack(consumer_id, event_id, acked_at)
      VALUES(?, ?, ?)
    `).run(String(consumerId), String(eventId), ts);

    const result = this.db.prepare(`
      UPDATE message_event
      SET state='CONSUMED', updated_at=?
      WHERE event_id=?
    `).run(ts, String(eventId));
    
    if (result.changes === 0) {
      throw new Error(`failed to update event state: ${eventId}`);
    }

    return ts;
  }

  peekUnread({ consumerId }) {
    const unreadRow = this.db.prepare(`
      SELECT COUNT(1) AS c
      FROM message_event e
      LEFT JOIN consumer_ack a
        ON a.event_id = e.event_id
       AND a.consumer_id = ?
      WHERE a.event_id IS NULL
    `).get(String(consumerId));

    const pendingRow = this.db.prepare(`
      SELECT COUNT(1) AS c
      FROM push_outbox
      WHERE status IN ('PENDING', 'RETRY', 'SENT')
    `).get();

    return {
      unread: coerceInt(unreadRow && unreadRow.c, 0),
      pending_push: coerceInt(pendingRow && pendingRow.c, 0),
    };
  }

  enqueueA2aOutbox(input) {
    const tsNow = nowMs();
    const messageId = String(input.message_id || "").trim();
    if (!messageId) {
      throw new Error("message_id is required");
    }
    try {
      this.db.prepare(`
        INSERT INTO a2a_outbox(
          message_id, target_agent_id, message_type, qos, envelope_json,
          status, attempt, next_retry_at, last_error, created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, 'PENDING', 0, ?, NULL, ?, ?)
      `).run(
        messageId,
        String(input.target_agent_id || "").trim(),
        String(input.message_type || "").trim(),
        coerceInt(input.qos, 1),
        JSON.stringify(input.envelope || {}),
        tsNow,
        tsNow,
        tsNow
      );
      return { created: true, message_id: messageId };
    } catch (err) {
      if (isUniqueConstraint(err)) {
        return { created: false, message_id: messageId };
      }
      throw err;
    }
  }

  listPendingA2aOutbox({ now, batchSize }) {
    const tsNow = coerceInt(now, nowMs());
    const limit = coerceInt(batchSize, 50);
    const rows = this.db.prepare(`
      SELECT
        id,
        message_id,
        target_agent_id,
        message_type,
        qos,
        envelope_json,
        status,
        attempt
      FROM a2a_outbox
      WHERE status IN ('PENDING', 'RETRY')
        AND next_retry_at <= ?
      ORDER BY id ASC
      LIMIT ?
    `).all(tsNow, limit);
    return rows.map((row) => ({
      id: coerceInt(row.id, 0),
      message_id: String(row.message_id || ""),
      target_agent_id: String(row.target_agent_id || ""),
      message_type: String(row.message_type || ""),
      qos: coerceInt(row.qos, 1),
      envelope: parseJsonSafe(row.envelope_json, {}),
      status: String(row.status || ""),
      attempt: coerceInt(row.attempt, 0),
    }));
  }

  markA2aOutboxSent({ id }) {
    const ts = nowMs();
    this.db.prepare(`
      UPDATE a2a_outbox
      SET status='SENT', updated_at=?, last_error=NULL
      WHERE id=?
    `).run(ts, coerceInt(id, 0));
  }

  markA2aOutboxRetry({ id, attempt, nextRetryAt, lastError }) {
    const ts = nowMs();
    this.db.prepare(`
      UPDATE a2a_outbox
      SET status='RETRY', attempt=?, next_retry_at=?, updated_at=?, last_error=?
      WHERE id=?
    `).run(
      coerceInt(attempt, 0),
      coerceInt(nextRetryAt, ts),
      ts,
      String(lastError || "").slice(0, 1000),
      coerceInt(id, 0)
    );
  }

  listPendingPushOutbox({ now, batchSize }) {
    const tsNow = coerceInt(now, nowMs());
    const limit = coerceInt(batchSize, 20);
    return this.db.prepare(`
      SELECT
        o.id AS outbox_id,
        o.event_id,
        o.attempt,
        e.peer_id,
        e.unread_count,
        e.preview,
        e.payload_json,
        e.state
      FROM push_outbox o
      JOIN message_event e ON e.event_id = o.event_id
      WHERE o.status IN ('PENDING', 'RETRY')
        AND o.next_retry_at <= ?
      ORDER BY o.id ASC
      LIMIT ?
    `).all(tsNow, limit);
  }

  listSentPushOutbox({ batchSize }) {
    const limit = coerceInt(batchSize, 20);
    return this.db.prepare(`
      SELECT
        o.id AS outbox_id,
        o.event_id,
        o.attempt,
        o.next_retry_at,
        o.updated_at,
        e.peer_id,
        e.unread_count,
        e.preview,
        e.payload_json,
        e.state
      FROM push_outbox o
      JOIN message_event e ON e.event_id = o.event_id
      WHERE o.status = 'SENT'
      ORDER BY o.id ASC
      LIMIT ?
    `).all(limit);
  }

  isEventAckedByConsumer({ consumerId, eventId }) {
    const row = this.db.prepare(`
      SELECT 1 AS ok
      FROM consumer_ack
      WHERE consumer_id = ?
        AND event_id = ?
      LIMIT 1
    `).get(String(consumerId), String(eventId));
    return Boolean(row && row.ok === 1);
  }

  markPushSent({ outboxId, eventId, ackDeadlineAt }) {
    const ts = nowMs();
    const deadline = coerceInt(ackDeadlineAt, ts);
    this.db.prepare(`
      UPDATE push_outbox
      SET status='SENT', next_retry_at=?, updated_at=?, last_error=NULL
      WHERE id=?
    `).run(deadline, ts, coerceInt(outboxId, 0));
    this.db.prepare(`
      UPDATE message_event
      SET state='PUSHED', updated_at=?
      WHERE event_id=?
    `).run(ts, String(eventId));
  }

  markPushAcked({ outboxId, eventId }) {
    const ts = nowMs();
    this.db.prepare(`
      UPDATE push_outbox
      SET status='ACKED', updated_at=?, last_error=NULL
      WHERE id=?
    `).run(ts, coerceInt(outboxId, 0));
    this.db.prepare(`
      UPDATE message_event
      SET state='CONSUMED', updated_at=?
      WHERE event_id=?
    `).run(ts, String(eventId));
  }

  markPushRetry({ outboxId, attempt, nextRetryAt, lastError }) {
    const ts = nowMs();
    this.db.prepare(`
      UPDATE push_outbox
      SET status='RETRY', attempt=?, next_retry_at=?, updated_at=?, last_error=?
      WHERE id=?
    `).run(
      coerceInt(attempt, 0),
      coerceInt(nextRetryAt, ts),
      ts,
      String(lastError || "").slice(0, 1000),
      coerceInt(outboxId, 0)
    );
  }

  getLatestEvents(limit) {
    return this.db.prepare(`
      SELECT seq, event_id, peer_id, unread_count, preview, state, created_at
      FROM message_event
      ORDER BY seq DESC
      LIMIT ?
    `).all(coerceInt(limit, 5));
  }

  getPendingPush(limit) {
    return this.db.prepare(`
      SELECT event_id, status, attempt, next_retry_at, COALESCE(last_error, '') AS err
      FROM push_outbox
      WHERE status IN ('PENDING', 'RETRY', 'SENT')
      ORDER BY id DESC
      LIMIT ?
    `).all(coerceInt(limit, 5));
  }
}

module.exports = {
  EventStore,
  nowMs,
};
