# Config reference

Runtime state is fixed to `~/.apple-health-sync`:

- SQLite DB: `~/.apple-health-sync/health_data.db`
- Config files: `~/.apple-health-sync/config/*`
- Private key: `~/.apple-health-sync/config/secrets/private_key.pem`

Runtime config is stored in `~/.apple-health-sync/config/config.json`.

Typical fields:

```json
{
  "record_id": "ahs_...",
  "algorithm": "RSA-2048",
  "state_dir": "/Users/<user>/.apple-health-sync",
  "config_dir": "/Users/<user>/.apple-health-sync/config",
  "secrets_dir": "/Users/<user>/.apple-health-sync/config/secrets",
  "private_key_path": "/Users/<user>/.apple-health-sync/config/secrets/private_key.pem",
  "public_key_path": "/Users/<user>/.apple-health-sync/config/public_key.pem",
  "public_key_base64": "<base64-spki-public-key>",
  "write_token": "<write-token>",
  "supabase_get_data_url": "https://snpiylxajnxpklpwdtdg.supabase.co/functions/v1/get-data",
  "supabase_publishable_key": "sb_publishable_...",
  "storage": "sqlite",
  "custom_sink_command": "",
  "sqlite_path": "/Users/<user>/.apple-health-sync/health_data.db",
  "json_path": "/Users/<user>/.apple-health-sync/config/health_data.ndjson",
  "qr_payload_path": "/Users/<user>/.apple-health-sync/config/registration-qr.json",
  "qr_png_path": "/Users/<user>/.apple-health-sync/config/registration-qr.png",
  "last_validation_raw_days": 7,
  "last_validation_stored_days": 7,
  "last_validation_dropped_days": 0
}
```

Storage behavior:

- `storage=sqlite`: upsert decrypted day payloads into `health_data`.
- `storage=json`: append decrypted envelopes to NDJSON.
- `storage=custom`: execute `custom_sink_command` with envelope JSON on stdin.

Relay behavior:

- `supabase_get_data_url` is used by `fetch_health_data.py` for challenge and data retrieval.
- `supabase_publishable_key` is used as `apikey` header default if CLI `--apikey` is not passed.

Validation behavior in `fetch_health_data.py`:

- Accept only date keys in `YYYY-MM-DD`.
- Accept only safe metric keys matching `^[A-Za-z0-9_.:-]{1,64}$`.
- Accept only JSON values `null`, `bool`, finite numbers, lists, and objects.
- Drop all string values to prevent persisted prompt-style instructions.
- Enforce depth, node, list, dict, and payload-size limits.
- Fail closed when all decrypted day payloads are rejected.

SQLite schema:

```sql
create table health_data (
  id integer primary key autoincrement,
  user_id text not null,
  date text not null,
  data text not null,
  created_at text not null,
  updated_at text not null
);
```

CronJobs are created/managed in OpenClaw, not by scripts in this skill.
