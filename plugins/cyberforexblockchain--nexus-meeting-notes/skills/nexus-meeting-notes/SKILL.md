---
name: nexus-meeting-notes
description: "Transform raw meeting transcripts into structured minutes with attendees, decisions, action items, owners, and deadlines. Built for autonomous agents processing audio transcription output."
---

# NEXUS Meeting Scribe

> Autonomous meeting intelligence for AI agents on Cardano

## When to use

Your agent has raw meeting transcript text (from Whisper, AssemblyAI, or manual notes) and needs to produce structured, actionable meeting minutes. The output identifies who said what, what was decided, and who owns each follow-up task.

## What makes this different

Most summarizers produce a paragraph. Meeting Scribe produces **structured data**: separate arrays for attendees, agenda topics, decisions, action items (with owners and deadlines), and unresolved questions. This makes downstream automation trivial — your agent can directly create Jira tickets, send follow-up emails, or update project trackers from the output.

## How agents use this

1. Audio transcription agent produces raw text from a recorded meeting
2. Agent sends transcript to Meeting Scribe via POST
3. Receives structured JSON: `{attendees, topics, decisions, action_items, open_questions}`
4. Agent routes action items to task management, decisions to documentation

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/meeting-notes \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"transcript": "John: We need to ship the API by Friday. Sarah: I will handle testing. Bob: What about the payment integration? John: Lets push payments to next sprint."}'
```

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/meeting-notes` | POST | Transcript as JSON body |

## Security & Privacy

Meeting transcripts often contain sensitive business discussions. All data is encrypted via HTTPS/TLS. No transcripts are stored — processed in memory and discarded immediately. Payment proofs verified on Cardano via Masumi Protocol.

## Model Invocation Note

This skill uses server-side LLM processing to parse transcripts. The AI identifies speakers, extracts decisions, and assigns action items. You may opt out by not installing this skill.

## Trust Statement

By using this skill, meeting transcript data is transmitted to NEXUS for AI processing. All payments are non-custodial via Cardano blockchain. Visit https://ai-service-hub-15.emergent.host for full documentation.
