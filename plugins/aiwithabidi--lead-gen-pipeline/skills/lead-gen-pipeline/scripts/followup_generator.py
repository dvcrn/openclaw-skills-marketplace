#!/usr/bin/env python3
"""
AI-powered follow-up message generator.
Generates personalized follow-up messages based on lead context, stage, and tone.

Usage:
    python3 followup_generator.py '{"name":"Jane","company":"Acme","context":"Had demo, interested in enterprise","stage":"post-demo","tone":"professional","channel":"email"}'

Requires: OPENROUTER_API_KEY
"""

import os
import sys
import json
import urllib.request
import urllib.error

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-haiku-4.5"


def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print(json.dumps({"error": "OPENROUTER_API_KEY environment variable not set"}))
        sys.exit(1)
    return key


def generate_followup(config: dict) -> dict:
    """Generate a personalized follow-up message."""

    name = config.get("name", "there")
    company = config.get("company", "")
    context = config.get("context", "")
    stage = config.get("stage", "warm")
    tone = config.get("tone", "professional")
    channel = config.get("channel", "email")
    sequence_step = config.get("sequence_step", None)
    sender_name = config.get("sender_name", "")
    sender_company = config.get("sender_company", "")
    product = config.get("product", "")
    conversation_history = config.get("conversation_history", "")

    channel_instructions = {
        "email": "Write a complete email with subject line. Keep body to 3-5 short paragraphs. Include clear CTA.",
        "sms": "Write a short SMS message under 160 characters. Punchy, direct, conversational. Include one clear CTA.",
        "whatsapp": "Write a WhatsApp message. Conversational, can use emojis sparingly. 2-4 sentences max.",
        "linkedin": "Write a LinkedIn message. Professional but personable. Reference their profile/company. 2-3 sentences.",
    }

    stage_context = {
        "initial": "This is a cold/first outreach. Focus on value, not selling. Ask a question.",
        "warm": "They've shown interest but no meeting yet. Build on their engagement, propose next step.",
        "booked": "Meeting is scheduled. Confirm details, set expectations, share prep material.",
        "post-demo": "They've seen a demo/had a call. Reference specific points discussed, address concerns, propose next steps.",
        "proposal": "Proposal has been sent. Follow up on it, address potential objections, create gentle urgency.",
        "closing": "Final decision stage. Address remaining concerns, summarize value, make it easy to say yes.",
        "revival": "Re-engaging a cold/lost lead. New angle, new value, don't reference being ignored.",
    }

    sequence_context = ""
    if sequence_step:
        steps = {
            1: "First email in sequence. Lead with value, pattern-interrupt subject line.",
            2: "Second touch (Day 3). Share a case study or social proof.",
            3: "Third touch (Day 7). Try a different angle — video, insight, or humor.",
            4: "Final email (Day 14). Break-up email. 'Should I close your file?' Creates urgency via loss aversion.",
        }
        sequence_context = f"\nSequence step {sequence_step}: {steps.get(sequence_step, 'Continue the sequence naturally.')}"

    system_prompt = f"""You are an expert sales copywriter. Generate a follow-up message.

Tone: {tone}
Channel: {channel}
{channel_instructions.get(channel, channel_instructions['email'])}

Stage: {stage}
{stage_context.get(stage, '')}
{sequence_context}

Rules:
- Personalize using the lead's name and context
- Never be pushy or salesy — be helpful and genuine
- One clear call-to-action
- Match the tone exactly
- For email: start response with "Subject: ..." on its own line
- Keep it concise — shorter is almost always better

Respond with ONLY valid JSON (no markdown):
{{
  "message": "<the full message text>",
  "subject": "<email subject line if channel is email, otherwise null>",
  "cta": "<the call to action extracted>",
  "tone_used": "{tone}",
  "channel": "{channel}",
  "tips": "<one tactical tip for this specific follow-up>"
}}"""

    context_parts = []
    if company:
        context_parts.append(f"Company: {company}")
    if context:
        context_parts.append(f"Context: {context}")
    if conversation_history:
        context_parts.append(f"Previous conversation: {conversation_history}")
    if sender_name:
        context_parts.append(f"Sending as: {sender_name}")
    if sender_company:
        context_parts.append(f"From company: {sender_company}")
    if product:
        context_parts.append(f"Product/service: {product}")

    user_prompt = f"Generate a {tone} {channel} follow-up for {name}.\n" + "\n".join(context_parts)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agxntsix.ai",
        "X-Title": "Follow-up Generator",
    }

    try:
        req = urllib.request.Request(
            OPENROUTER_URL,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            content = result["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content.strip())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"API error {e.code}", "details": error_body}
    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM response", "raw": content}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: followup_generator.py '<config_json>'")
        print('Example: followup_generator.py \'{"name":"Jane","context":"Had a demo","stage":"post-demo","tone":"professional","channel":"email"}\'')
        sys.exit(1)

    try:
        config = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = generate_followup(config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
