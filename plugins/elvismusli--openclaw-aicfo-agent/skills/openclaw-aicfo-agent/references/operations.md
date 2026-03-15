# Operations

## Environment

```bash
export AICFO_APP_URL="https://aiceo.city"
export AICFO_API_KEY="aicfo_sk_..."
```

Optional:

```bash
export AICFO_COMPANY_ID="<company-id>"
```

## Bootstrap

```bash
node bin/openclaw-aicfo-adapter.mjs session
node bin/openclaw-aicfo-adapter.mjs tools
```

## Company Discovery

```bash
node bin/openclaw-aicfo-adapter.mjs companies
```

## Dashboard

```bash
node bin/openclaw-aicfo-adapter.mjs dashboard \
  '{"company_id":"<company-id>"}'
```

## Query Entities

```bash
node bin/openclaw-aicfo-adapter.mjs query \
  '{"company_id":"<company-id>","domain":"finance","limit":10,"view":"summary"}'
```

## Search Entities

```bash
node bin/openclaw-aicfo-adapter.mjs search \
  '{"company_id":"<company-id>","query":"investor","limit":10}'
```

## Get Entity

Native ID form:

```bash
node bin/openclaw-aicfo-adapter.mjs get-entity \
  '{"company_id":"<company-id>","qualified_id":"snapshot-1","view":"summary"}'
```

Domain + ID form:

```bash
node bin/openclaw-aicfo-adapter.mjs get-entity \
  '{"company_id":"<company-id>","domain":"finance","id":"snapshot-1","view":"summary"}'
```

## Read Raw File

```bash
node bin/openclaw-aicfo-adapter.mjs get-file \
  '{"company_id":"<company-id>","path":"finance/_summary.qmd"}'
```

## List Connectors

```bash
node bin/openclaw-aicfo-adapter.mjs connectors \
  '{"company_id":"<company-id>"}'
```

## Telegram

```bash
node bin/openclaw-aicfo-adapter.mjs connector \
  '{"company_id":"<company-id>","provider":"telegram","action":"list_chats","input":{"limit":25,"offset":0,"enabledOnly":true}}'
```

```bash
node bin/openclaw-aicfo-adapter.mjs connector \
  '{"company_id":"<company-id>","provider":"telegram","action":"get_recent_messages","input":{"chatId":"-4930599199","limit":20,"offset":0}}'
```

## Google Drive

```bash
node bin/openclaw-aicfo-adapter.mjs connector \
  '{"company_id":"<company-id>","provider":"google_drive","action":"list_files","input":{"root":"shared_with_me"}}'
```

## Documents

```bash
node bin/openclaw-aicfo-adapter.mjs documents \
  '{"company_id":"<company-id>","limit":20,"status":"processing"}'
```
