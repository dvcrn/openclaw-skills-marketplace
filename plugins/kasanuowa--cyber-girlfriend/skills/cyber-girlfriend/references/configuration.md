# Configuration

Use a single config file. JSON is the simplest default.

## Required Sections

### `persona`

- `name`: in-character name
- `owner_nickname`: how the companion addresses the owner
- `tone`: short guidance string
- `relationship_style`: short guidance string
- `emoji`: optional

### `delivery`

- `channel`: e.g. `telegram`
- `owner_target`: destination identifier
- `owner_session_key`: recent-message source key
- `generator_target`: isolated generation target/session if the runtime needs one

### `schedule`

- `quiet_hours_start`
- `quiet_hours_end`
- `daily_limit`
- `cooldown_sec`
- `active_thresholds_sec.morning`
- `active_thresholds_sec.afternoon`
- `active_thresholds_sec.evening`
- `active_thresholds_sec.night`
- `mode_windows.morning`
- `mode_windows.afternoon`
- `mode_windows.evening`
- `mode_windows.night`
- `cron_jobs.<mode>.name`
- `cron_jobs.<mode>.description`
- `cron_jobs.<mode>.cron`
- `cron_jobs.<mode>.tz`
- `cron_jobs.<mode>.system_event`
- `cron_jobs.<mode>.enabled`

### `behavior`

- `style_variants`
- `content_types`
- `emotion_thresholds`
- `message_length.min_chars`
- `message_length.max_chars`

### `runtime`

Externalize all runtime hooks here.

Suggested fields:
- `workspace_root`
- `state_dir`
- `recent_messages_path`
- `sessions_store_path`
- `healthcheck_command`
- `jobs_list_command`
- `generate_command_template`
- `send_command_template`
- `generate_retry_attempts`
- `generate_retry_delay_sec`

Do not hardcode a provider or model here unless the user explicitly wants that.
If the runtime depends on a remote model endpoint, expose retry behavior here rather than hardcoding it in prompts.

### `schedule.cron_jobs`

Use this when the runtime has an external scheduler such as OpenClaw cron.

Recommended fields per mode:
- `name`: stable cron job name
- `description`: human-readable purpose
- `cron`: cron expression
- `tz`: timezone for the cron expression
- `system_event`: event text delivered to the runtime
- `enabled`: optional boolean
- `id`: optional existing job id for stable patching

Keep these values in config so users can retime `morning|afternoon|evening|night` without editing handler docs or Python code.

### `sources`

Optional source blocks.

Suggested X block:
- `enabled`
- `chrome_path`
- `trending_url`
- `cache_path`
- `refresh_ttl_sec`
- `max_items`

## State Files

Recommended:
- `companion-state.json`
- `share-cache.json`

Track only behaviorally useful state:
- pacing
- last style/content type
- preference counters
- last owner reply metadata
- source cache timestamp
