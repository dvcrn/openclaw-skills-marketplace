# Delivery channel identifiers
CHANNEL_TELEGRAM = "telegram"
CHANNEL_DISCORD = "discord"
CHANNEL_EMAIL = "email"

# Tag embedded in every job description for channel-scoped filtering
# Format: [remind-me:<channel>:<chatId>]
TAG_PREFIX = "remind-me"

# openclaw CLI binary
OPENCLAW_BIN = "openclaw"

# Valid schedule kinds accepted by the script
SCHEDULE_KIND_EVERY = "every"
SCHEDULE_KIND_CRON = "cron"
SCHEDULE_KIND_AT = "at"

VALID_SCHEDULE_KINDS = (SCHEDULE_KIND_EVERY, SCHEDULE_KIND_CRON, SCHEDULE_KIND_AT)

# at: schedules are always one-shot — enforced in service
AT_IS_ALWAYS_ONCE = True
