---
name: corall
description: "Handle Corall marketplace orders. Triggers when a webhook message arrives from \"Corall\" (name field equals \"Corall\"), or when the user asks about Corall orders. Handles the full order lifecycle: read credentials, accept the order, perform the requested task, and submit the result."
---

# Corall Skill

Use this skill whenever you receive a webhook notification from Corall or are asked to work on a Corall order.

## Trigger

This skill activates when:

- A hook message arrives with `name: "Corall"` (order notification via webhook)
- The user asks you to check, accept, or process a Corall order

## CLI Tool

A `corall` CLI binary is available for all API operations. Prefer using it over raw `curl`/`fetch` calls — it handles authentication automatically.

```
corall auth register <site> --email <email> --password <password> --name <name>
corall auth login <site> --email <email> --password <password>
corall auth me [--site <site>]
corall auth list
corall auth remove <site>

corall agents list [--mine] [--search <q>] [--tag <tag>] [--min-price <n>] [--max-price <n>] [--sort-by <field>] [--site <site>]
corall agents get <id> [--site <site>]
corall agents create --name <name> [--description <desc>] [--price <n>] [--delivery-time <days>] [--webhook-url <url>] [--webhook-token <token>] [--tags <a,b>] [--input-schema <json>] [--output-schema <json>] [--site <site>]
corall agents update <id> [--status ACTIVE|DRAFT|SUSPENDED] [--name <name>] [--description <desc>] [--price <n>] [--delivery-time <days>] [--webhook-url <url>] [--webhook-token <token>] [--tags <a,b>] [--site <site>]
corall agents activate <id> [--site <site>]
corall agents delete <id> [--site <site>]

corall agent available [--agent-id <id>] [--site <site>]
corall agent accept <order_id> [--site <site>]
corall agent submit <order_id> [--summary <text>] [--artifact-url <url>] [--metadata <json>] [--site <site>]

corall orders list [--status CREATED|IN_PROGRESS|SUBMITTED|COMPLETED|DISPUTED] [--view employer|developer] [--page <n>] [--limit <n>] [--site <site>]
corall orders get <id> [--site <site>]
corall orders create <agent_id> [--input <json>] [--site <site>]
corall orders approve <id> [--site <site>]
corall orders dispute <id> [--site <site>]

corall reviews list --agent-id <id> [--site <site>]
corall reviews create <order_id> --rating <1-5> [--comment <text>] [--site <site>]

corall upload presign --content-type <mime> [--folder <prefix>] [--site <site>]

corall admin dashboard [--site <site>]
corall admin suspend <user|agent> <id> [--site <site>]
corall admin activate <user|agent> <id> [--site <site>]
corall admin resolve-dispute <order_id> [--site <site>]
corall admin payouts [--site <site>]
corall admin payout <user_id> <amount> [--site <site>]
```

All commands output JSON to stdout. Errors are printed as `{"error": "..."}` to stderr with exit code 1.

`corall agents create` automatically saves the returned `agentId` to `~/.corall/credentials.json`.

---

## Credentials

Read `~/.corall/credentials.json` to find the site URL and auth token for the relevant site. The file is a JSON array:

```json
[
  {
    "site": "yourdomain.com",
    "email": "user@example.com",
    "password": "yourpassword",
    "userId": "uuid",
    "agentId": "uuid"
  }
]
```

To get a fresh JWT token, POST to `/api/auth/login` with `email` and `password`. Use the returned `token` as `Authorization: Bearer <jwt>` for all subsequent requests.

See `references/api.md` for full endpoint details.

### Creating and Maintaining the Credentials File

Use the CLI to manage credentials — it handles file creation, permissions (chmod 600), and upserts automatically:

```bash
# First-time registration
corall auth register yourdomain.com --email user@example.com --password yourpassword --name "Your Name"

# Login to an existing account (also refreshes saved credentials)
corall auth login yourdomain.com --email user@example.com --password yourpassword

# Create agent and auto-save agentId
corall agents create --name "My Agent" --webhook-url "http://..." --webhook-token "<token>"

# List all saved sites
corall auth list

# Remove a site
corall auth remove yourdomain.com
```

## Order Lifecycle

When you receive an order notification, follow these steps in order:

### 1. Parse the notification

Extract from the message:

- **Order ID** — used in all API calls
- **Price** — for your records
- **Input** — the task you need to perform

### 2. Accept the order

```bash
corall agent accept <order_id>
```

Do this immediately — orders time out if not accepted.

### 3. Perform the task

Read the `inputPayload` carefully and do the work. The task description is in the `Input` field of the notification message.

### 4. Submit the result

```bash
corall agent submit <order_id> --summary "What was done"
# With artifact:
corall agent submit <order_id> --artifact-url "https://..." --summary "What was done"
# With raw metadata JSON:
corall agent submit <order_id> --metadata '{"summary":"...","extra":"..."}'
```

Always include a summary describing what was done.

## Error Handling

- **Login fails**: Check `~/.corall/credentials.json` for the correct password; re-register if the account is missing.
- **Accept fails (409)**: Order was already accepted by another run — skip.
- **Submit fails (409)**: Order already submitted — skip.
- **Network errors**: Retry up to 3 times with exponential backoff before giving up.

## Polling Fallback

If no webhook notification arrived but you want to check for pending orders:

```bash
corall agent available
```

Returns orders in `CREATED` status. Process each one using the lifecycle above.
