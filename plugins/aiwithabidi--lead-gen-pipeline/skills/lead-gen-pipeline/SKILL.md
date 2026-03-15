---
name: lead-gen-pipeline
description: "Automated lead generation pipeline with AI-powered lead scoring and personalized follow-up generation. Score leads 0-100 with reasoning, generate context-aware follow-ups in multiple tones. Integrates with any CRM. Use for sales automation, cold outreach, and pipeline management."
homepage: https://www.agxntsix.ai
---

# Lead Gen Pipeline

AI-powered lead generation pipeline. Score leads intelligently, generate personalized follow-ups, and manage your sales pipeline.

## Quick Start

```bash
export OPENROUTER_API_KEY="your-key"

# Score a lead
python3 {baseDir}/scripts/lead_scorer.py '{"name":"Jane Smith","company":"Acme Corp","title":"VP Marketing","source":"webinar","actions":["downloaded whitepaper","visited pricing page 3x","opened 5 emails"]}'

# Generate follow-up
python3 {baseDir}/scripts/followup_generator.py '{"name":"Jane Smith","company":"Acme Corp","context":"Attended our AI webinar, downloaded whitepaper","stage":"warm","tone":"professional"}'
```

## Lead Scoring

The AI scorer evaluates leads on multiple dimensions:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Fit** | 30% | Does the lead match your ICP? (title, company size, industry) |
| **Intent** | 30% | Behavioral signals (page visits, downloads, email engagement) |
| **Engagement** | 20% | How actively are they interacting? (recency, frequency) |
| **Source Quality** | 20% | Where did they come from? (referral > webinar > cold) |

### Score Ranges
- **80-100:** 🔥 Hot — reach out immediately, high buying intent
- **60-79:** 🟡 Warm — nurture with targeted content, book a call
- **40-59:** 🟠 Cool — add to drip sequence, monitor engagement
- **0-39:** 🔵 Cold — low priority, long-term nurture only

```bash
# Score with custom ICP
python3 {baseDir}/scripts/lead_scorer.py '{"name":"...","company":"...","icp":{"industries":["SaaS","fintech"],"minEmployees":50,"titles":["VP","Director","C-suite"]}}'
```

## Follow-Up Generation

Generate personalized follow-up messages for any pipeline stage:

```bash
# Professional follow-up after demo
python3 {baseDir}/scripts/followup_generator.py '{
  "name": "Jane Smith",
  "company": "Acme Corp",
  "context": "Had a 30-min demo, interested in enterprise plan, concerned about onboarding time",
  "stage": "post-demo",
  "tone": "professional",
  "channel": "email"
}'

# Casual SMS check-in
python3 {baseDir}/scripts/followup_generator.py '{
  "name": "Mike",
  "context": "Met at conference, exchanged cards, talked about AI automation",
  "stage": "initial",
  "tone": "casual",
  "channel": "sms"
}'

# Urgent closing message
python3 {baseDir}/scripts/followup_generator.py '{
  "name": "Sarah Johnson",
  "company": "TechFlow",
  "context": "Proposal sent 5 days ago, no response, deal worth $25k, quarter ending",
  "stage": "closing",
  "tone": "urgent",
  "channel": "email"
}'
```

### Supported Tones
- **professional** — formal business communication
- **casual** — friendly, conversational
- **urgent** — time-sensitive, action-oriented
- **friendly** — warm, relationship-focused
- **consultative** — expert advice framing

### Supported Channels
- **email** — full email with subject line
- **sms** — short, punchy (< 160 chars)
- **whatsapp** — conversational, emoji-friendly
- **linkedin** — professional networking tone

### Pipeline Stages
- **initial** — first contact / cold outreach
- **warm** — engaged but no meeting yet
- **booked** — meeting/demo scheduled
- **post-demo** — after initial call/demo
- **proposal** — proposal sent
- **closing** — negotiation / final decision
- **revival** — re-engaging cold/lost lead

## Cold Outreach Templates

### The AIDA Framework
1. **Attention** — Hook with relevant pain point
2. **Interest** — Show you understand their world
3. **Desire** — Paint the outcome
4. **Action** — Clear, low-friction CTA

### Outreach Sequences

**Day 1:** Initial value-first email
**Day 3:** Follow-up with case study / social proof
**Day 7:** Different angle (video, voice note, meme)
**Day 14:** Break-up email ("Should I close your file?")

Generate any of these:
```bash
python3 {baseDir}/scripts/followup_generator.py '{"name":"...","stage":"initial","sequence_step":1}'
python3 {baseDir}/scripts/followup_generator.py '{"name":"...","stage":"initial","sequence_step":4}'
```

## CRM Integration Patterns

### With GHL (GoHighLevel)
```bash
# 1. Score incoming lead
SCORE=$(python3 {baseDir}/scripts/lead_scorer.py '{"name":"...","source":"facebook_ad"}')

# 2. Create contact in GHL with score tag
python3 ../ghl-crm/{baseDir}/scripts/ghl_api.py contacts create '{"firstName":"...","tags":["score-85","hot-lead"]}'

# 3. Add to appropriate pipeline stage
python3 ../ghl-crm/{baseDir}/scripts/ghl_api.py opportunities create '{"pipelineId":"...","stageId":"hot-stage-id","contactId":"..."}'

# 4. Generate and send follow-up
MSG=$(python3 {baseDir}/scripts/followup_generator.py '{"name":"...","stage":"warm","channel":"sms"}')
python3 ../ghl-crm/{baseDir}/scripts/ghl_api.py conversations send-sms <contactId> "$MSG"
```

### With Any CRM
The scripts output JSON — pipe into any CRM API wrapper. Lead scores include reasoning that can be stored as CRM notes.

## Response Handling

When a lead replies, re-score with updated context:
```bash
python3 {baseDir}/scripts/lead_scorer.py '{"name":"Jane","company":"Acme","actions":["replied to email","asked about pricing","requested demo"]}'
```

Then generate contextual response:
```bash
python3 {baseDir}/scripts/followup_generator.py '{"name":"Jane","context":"She asked about pricing and wants a demo","stage":"warm","tone":"professional"}'
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
