# Access and Auth

## Webhook Setup

1. In Bitrix24 open `Developer resources -> Other -> Inbound webhook`.
2. Create a webhook and copy its URL.
3. Save it:

```bash
python3 scripts/bitrix24_call.py user.current --url "<webhook>" --json
```

This saves the webhook to `~/.config/bitrix24-skill/config.json` and verifies it works in one step.

Expected format:

```text
https://your-portal.bitrix24.ru/rest/<user_id>/<webhook>/
```

After that, the skill reuses the saved webhook automatically for all calls.

To replace an existing webhook:

```bash
python3 scripts/save_webhook.py --url "<new-webhook>" --force --check
```

## Agent Setup Behavior

When a user asks for setup help or a REST call fails:

1. Check saved config with `scripts/check_webhook.py --json`
2. If the user already shared a webhook in the conversation, save it and retry
3. Only ask the user for a webhook if no saved config exists

Mask the webhook secret in user-facing output.

## Permissions

Grant the permission groups that match the methods you will call.

Recommended full-coverage set:

- CRM
- Tasks
- Calendar
- Disk or Drive
- IM or Chat
- User and department access

## `CLIENT_ID` For Bot Integrations

For `imbot` integrations, Bitrix24 bot registration requires `CLIENT_ID`.

- Provide `CLIENT_ID` when registering the bot
- Persist it as part of the bot credentials
- Pass the same `CLIENT_ID` into all later `imbot.*` calls
- Treat `CLIENT_ID` as a secret

## Official MCP Docs Endpoint

```text
https://mcp-dev.bitrix24.tech/mcp
```

Tools exposed by the server:

- `bitrix-search`
- `bitrix-app-development-doc-details`
- `bitrix-method-details`
- `bitrix-article-details`
- `bitrix-event-details`

## When To Use OAuth Instead Of A Webhook

Use a webhook when:

- you are connecting one portal quickly
- the integration is admin-managed
- you want the shortest setup path

Use OAuth when:

- your service lives outside Bitrix24
- users connect their own portals to your service
- you need renewable tokens instead of a fixed webhook secret

Key official docs:

- Full OAuth: `https://apidocs.bitrix24.ru/settings/oauth/index.html`
- REST call overview: `https://apidocs.bitrix24.ru/sdk/bx24-js-sdk/how-to-call-rest-methods/index.html`
- Install callback: `https://apidocs.bitrix24.ru/settings/app-installation/mass-market-apps/installation-callback.html`

## OAuth Facts From MCP Docs

- Authorization server: `https://oauth.bitrix24.tech/`
- Authorization starts at `https://portal.bitrix24.com/oauth/authorize/`
- Temporary authorization `code` is valid for 30 seconds
- Token exchange at `https://oauth.bitrix24.tech/oauth/token/`
- Returns `access_token`, `refresh_token`, `client_endpoint`, `server_endpoint`, `scope`

Useful MCP titles for auth topics:

- `Полный протокол авторизации OAuth 2.0`
- `Упрощенный вариант получения токенов OAuth 2.0`
- `Вызов методов REST`
- `Callback установки`

## Install Callback For UI-Less Apps

If you build a local or UI-less app, Bitrix24 can POST OAuth credentials to an install callback URL. That flow is documented in `Callback установки`.

- Save the received `access_token` and `refresh_token`
- Refresh access tokens on your backend
- Do not rely on browser-side JS install helpers for the callback flow
