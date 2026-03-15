const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS message_event (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  peer_id TEXT NOT NULL,
  message_id TEXT,
  msg_ts INTEGER NOT NULL DEFAULT 0,
  hash TEXT NOT NULL,
  unread_count INTEGER NOT NULL DEFAULT 0,
  preview TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  state TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'MQTT',
  a2a_message_id TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_message_event_msg_id
  ON message_event(message_id)
  WHERE message_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_message_event_peer_hash
  ON message_event(peer_id, hash);

CREATE TABLE IF NOT EXISTS push_outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  target TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0,
  next_retry_at INTEGER NOT NULL,
  status TEXT NOT NULL,
  last_error TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_push_outbox_status_retry
  ON push_outbox(status, next_retry_at);

CREATE TABLE IF NOT EXISTS a2a_outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id TEXT NOT NULL UNIQUE,
  target_agent_id TEXT NOT NULL,
  message_type TEXT NOT NULL,
  qos INTEGER NOT NULL DEFAULT 1,
  envelope_json TEXT NOT NULL,
  status TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0,
  next_retry_at INTEGER NOT NULL,
  last_error TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_a2a_outbox_status_retry
  ON a2a_outbox(status, next_retry_at);

CREATE TABLE IF NOT EXISTS consumer_ack (
  consumer_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  acked_at INTEGER NOT NULL,
  PRIMARY KEY (consumer_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_consumer_ack_event_id
  ON consumer_ack(event_id);
`;

function columnExists(db, tableName, columnName) {
  const stmt = db.prepare(`PRAGMA table_info(${tableName});`);
  const rows = stmt.all();
  return rows.some((row) => String(row.name) === columnName);
}

function applySchema(db) {
  db.exec("PRAGMA journal_mode=WAL;");
  db.exec("PRAGMA synchronous=NORMAL;");
  db.exec(SCHEMA_SQL);

  if (!columnExists(db, "message_event", "source")) {
    db.exec("ALTER TABLE message_event ADD COLUMN source TEXT NOT NULL DEFAULT 'IM';");
  }
  if (!columnExists(db, "message_event", "a2a_message_id")) {
    db.exec("ALTER TABLE message_event ADD COLUMN a2a_message_id TEXT;");
  }
  if (columnExists(db, "message_event", "a2a_message_id")) {
    db.exec(`
      CREATE UNIQUE INDEX IF NOT EXISTS idx_message_event_a2a_message_id
        ON message_event(a2a_message_id)
        WHERE a2a_message_id IS NOT NULL;
    `);
  }
}

module.exports = {
  applySchema,
};
