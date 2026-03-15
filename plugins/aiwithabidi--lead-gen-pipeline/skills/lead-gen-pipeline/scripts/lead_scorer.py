#!/usr/bin/env python3
"""
AI-powered lead scoring using LLM via OpenRouter.
Takes lead data, returns score 0-100 with reasoning.

Usage:
    python3 lead_scorer.py '{"name":"Jane Smith","company":"Acme Corp","title":"VP Marketing","source":"webinar","actions":["downloaded whitepaper","visited pricing 3x"]}'
    
    # With custom ICP
    python3 lead_scorer.py '{"name":"...","icp":{"industries":["SaaS"],"titles":["VP","Director"]}}'

Output: JSON with score, tier, reasoning, and recommended actions.
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


def score_lead(lead_data: dict) -> dict:
    """Score a lead using LLM analysis."""
    
    icp = lead_data.get("icp", {})
    icp_context = ""
    if icp:
        icp_context = f"\n\nIdeal Customer Profile (ICP):\n{json.dumps(icp, indent=2)}"

    system_prompt = f"""You are an expert lead scoring analyst. Score the lead from 0-100 based on:

1. FIT (30%): Does the lead match the ideal customer profile? Consider title, company, industry.
2. INTENT (30%): Behavioral signals indicating buying intent (pricing page visits, demo requests, content downloads).
3. ENGAGEMENT (20%): Recency and frequency of interactions.
4. SOURCE QUALITY (20%): Lead source reliability (referral=high, webinar=medium-high, cold=low).
{icp_context}

Respond ONLY with valid JSON (no markdown):
{{
  "score": <0-100>,
  "tier": "<hot|warm|cool|cold>",
  "breakdown": {{
    "fit": <0-100>,
    "intent": <0-100>,
    "engagement": <0-100>,
    "source_quality": <0-100>
  }},
  "reasoning": "<2-3 sentence explanation>",
  "recommended_actions": ["<action 1>", "<action 2>"],
  "priority": "<immediate|this-week|nurture|low>"
}}

Tier mapping: 80-100=hot, 60-79=warm, 40-59=cool, 0-39=cold"""

    user_prompt = f"Score this lead:\n{json.dumps(lead_data, indent=2)}"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agxntsix.ai",
        "X-Title": "Lead Scorer",
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
            content = result["choices"][0]["message"]["content"]
            # Parse the JSON response
            # Strip markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            score_data = json.loads(content.strip())
            score_data["lead"] = {
                "name": lead_data.get("name", "Unknown"),
                "company": lead_data.get("company", "Unknown"),
            }
            return score_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"API error {e.code}", "details": error_body}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse LLM response: {e}", "raw": content}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: lead_scorer.py '<lead_json>'")
        print('Example: lead_scorer.py \'{"name":"Jane","company":"Acme","source":"webinar","actions":["visited pricing"]}\'')
        sys.exit(1)

    try:
        lead_data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = score_lead(lead_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
