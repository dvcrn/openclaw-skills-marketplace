---
name: telegram-business
description: "Telegram bot for business automation — lead capture forms, inline keyboard menus, FAQ matching, appointment booking flows, and payment integration. Use for building customer-facing Telegram bots, community management, and lead generation."
homepage: https://www.agxntsix.ai
---

# Telegram Business Bot

Build business automation on Telegram — lead capture forms, appointment booking, FAQ bots, payments, and community management.

## Quick Start

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."

# Send a message
python3 {baseDir}/scripts/telegram_business.py send-message <chat_id> "Hello from your business bot!"

# Send inline keyboard
python3 {baseDir}/scripts/telegram_business.py send-menu <chat_id> "How can I help?" '[{"text":"📅 Book Appointment","callback_data":"book"},{"text":"❓ FAQ","callback_data":"faq"},{"text":"💬 Talk to Sales","callback_data":"sales"}]'

# Start lead capture
python3 {baseDir}/scripts/telegram_business.py send-lead-form <chat_id>
```

## Bot Setup

### 1. Create Bot via @BotFather
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose name and username (must end in `bot`)
4. Copy the token → set as `TELEGRAM_BOT_TOKEN`

### 2. Configure Bot
```
/setdescription - Business description shown on bot profile
/setabouttext - Short about text
/setuserpic - Bot avatar
/setcommands - Set command menu:
  start - Get started
  book - Book appointment
  faq - Frequently asked questions
  contact - Contact us
  help - Get help
```

### 3. Webhook Setup
```bash
# Set webhook (use your server URL)
python3 {baseDir}/scripts/telegram_business.py set-webhook "https://your-domain.com/webhook/telegram"

# Get webhook info
python3 {baseDir}/scripts/telegram_business.py get-webhook

# Delete webhook (switch to polling)
python3 {baseDir}/scripts/telegram_business.py delete-webhook
```

## Available Commands

### Messaging
```bash
# Send text
python3 {baseDir}/scripts/telegram_business.py send-message <chat_id> "Hello!"

# Send with HTML formatting
python3 {baseDir}/scripts/telegram_business.py send-message <chat_id> "<b>Bold</b> and <i>italic</i>" --html

# Send with Markdown
python3 {baseDir}/scripts/telegram_business.py send-message <chat_id> "**Bold** and _italic_" --markdown

# Reply to a message
python3 {baseDir}/scripts/telegram_business.py send-message <chat_id> "Got it!" --reply-to <message_id>
```

### Inline Keyboards
```bash
# Simple menu (buttons in rows of 2)
python3 {baseDir}/scripts/telegram_business.py send-menu <chat_id> "Choose an option:" '[
  {"text":"Option A","callback_data":"opt_a"},
  {"text":"Option B","callback_data":"opt_b"},
  {"text":"Option C","callback_data":"opt_c"}
]'

# URL buttons
python3 {baseDir}/scripts/telegram_business.py send-menu <chat_id> "Visit us:" '[
  {"text":"🌐 Website","url":"https://example.com"},
  {"text":"📸 Instagram","url":"https://instagram.com/example"}
]'

# Answer callback query (acknowledge button press)
python3 {baseDir}/scripts/telegram_business.py answer-callback <callback_query_id> "Processing..."

# Edit message (update after button press)
python3 {baseDir}/scripts/telegram_business.py edit-message <chat_id> <message_id> "Updated text!"
```

### Lead Capture
```bash
# Send lead capture form (multi-step inline flow)
python3 {baseDir}/scripts/telegram_business.py send-lead-form <chat_id>

# Process lead data (after collecting via conversation)
python3 {baseDir}/scripts/telegram_business.py process-lead '{"chat_id":123,"name":"John Doe","email":"john@example.com","phone":"+15551234567","interest":"AI automation","source":"telegram"}'
```

### FAQ System
```bash
# Match question to FAQ
python3 {baseDir}/scripts/telegram_business.py faq-match "What are your business hours?"

# Send FAQ menu
python3 {baseDir}/scripts/telegram_business.py send-faq-menu <chat_id>
```

### Media
```bash
# Send photo
python3 {baseDir}/scripts/telegram_business.py send-photo <chat_id> "https://example.com/image.jpg" "Caption here"

# Send document
python3 {baseDir}/scripts/telegram_business.py send-document <chat_id> "/path/to/file.pdf"

# Send contact card
python3 {baseDir}/scripts/telegram_business.py send-contact <chat_id> "+15551234567" "John" "Doe"
```

## Lead Capture Flow

The bot guides users through a multi-step form:

1. **Start** → Welcome message with menu buttons
2. **"Get Quote"** → Asks for name
3. User sends name → Asks for email
4. User sends email → Asks for phone (optional)
5. User sends phone → Asks for service interest (buttons)
6. User selects service → Confirmation + thank you
7. Lead data is output as JSON for CRM integration

### Integration with CRM
```bash
# Capture lead from Telegram, score it, add to GHL
LEAD='{"name":"John","email":"john@x.com","phone":"+1555...","source":"telegram"}'
SCORE=$(python3 ../lead-gen-pipeline/{baseDir}/scripts/lead_scorer.py "$LEAD")
python3 ../ghl-crm/{baseDir}/scripts/ghl_api.py contacts create "$LEAD"
```

## FAQ Automation

Define your FAQ in the script's `FAQ_DATABASE`:

```python
FAQ_DATABASE = [
    {"q": "What are your hours?", "a": "We're open Mon-Fri 9am-6pm EST.", "keywords": ["hours", "open", "schedule"]},
    {"q": "Where are you located?", "a": "123 Main St, New York, NY", "keywords": ["location", "address", "where"]},
    {"q": "How much does it cost?", "a": "Plans start at $99/mo. Reply 'pricing' for details.", "keywords": ["cost", "price", "pricing", "how much"]},
]
```

The FAQ matcher uses keyword matching + fuzzy similarity. For AI-powered matching, pipe through the LLM.

## Payment Integration

Telegram supports native payments via Payment Providers (Stripe, etc.):

```bash
# Send invoice
python3 {baseDir}/scripts/telegram_business.py send-invoice <chat_id> '{
  "title": "Consultation Fee",
  "description": "1-hour AI automation consultation",
  "payload": "consultation_001",
  "provider_token": "STRIPE_TOKEN",
  "currency": "USD",
  "prices": [{"label": "Consultation", "amount": 9900}]
}'
```

**Note:** `amount` is in smallest currency unit (cents for USD). $99.00 = 9900.

## Group Management

```bash
# Get chat info
python3 {baseDir}/scripts/telegram_business.py get-chat <chat_id>

# Get member count
python3 {baseDir}/scripts/telegram_business.py get-member-count <chat_id>

# Pin a message
python3 {baseDir}/scripts/telegram_business.py pin-message <chat_id> <message_id>

# Set chat description
python3 {baseDir}/scripts/telegram_business.py set-description <chat_id> "Welcome to our community!"
```

## Webhook Payload Handling

When using webhooks, incoming updates look like:

**Message:**
```json
{"update_id": 123, "message": {"chat": {"id": 456}, "from": {"id": 789, "first_name": "John"}, "text": "/start"}}
```

**Callback (button press):**
```json
{"update_id": 124, "callback_query": {"id": "abc", "data": "book", "message": {"chat": {"id": 456}}}}
```

Parse with:
```bash
python3 {baseDir}/scripts/telegram_business.py parse-update '<json>'
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
