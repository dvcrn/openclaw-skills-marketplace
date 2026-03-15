#!/usr/bin/env python3
"""Sequential Thinking — Structured step-by-step reasoning with verification."""

import argparse
import json
import os
import re
import sys
import time

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install: pip install requests")
    sys.exit(1)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4"


def chat(model, messages, temperature=0.3, max_tokens=2048):
    """Send chat completion request."""
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})
    return text, usage


def decompose(question, model, max_steps, temperature):
    """Break question into logical steps."""
    prompt = f"""You are a structured reasoning engine. Given a complex question, decompose it into {max_steps} or fewer logical sub-steps that, when answered sequentially, will lead to a comprehensive answer.

Question: {question}

Return ONLY a JSON array of step objects, each with "step_number", "title", and "question" fields. Example:
[
  {{"step_number": 1, "title": "Define the core concept", "question": "What exactly is X?"}},
  {{"step_number": 2, "title": "Identify key factors", "question": "What factors influence X?"}}
]

Return valid JSON only, no markdown fences."""

    text, usage = chat(model, [{"role": "user", "content": prompt}], temperature=temperature)
    # Extract JSON from response
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        steps = json.loads(text)
        return steps, usage
    except json.JSONDecodeError:
        # Try to find JSON array in response
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group()), usage
        raise ValueError(f"Failed to parse decomposition: {text[:200]}")


def solve_step(step, prior_context, question, model, temperature):
    """Solve a single reasoning step with context from prior steps."""
    context_str = ""
    if prior_context:
        context_str = "Previous step conclusions:\n" + "\n".join(
            f"- Step {s['step_number']} ({s['title']}): {s['conclusion']}" for s in prior_context
        ) + "\n\n"

    prompt = f"""You are solving one step of a multi-step reasoning process.

Original question: {question}

{context_str}Current step {step['step_number']}: {step['title']}
Sub-question: {step['question']}

Provide a clear, focused answer to this sub-question. Be concise but thorough. End with a one-sentence conclusion."""

    text, usage = chat(model, [{"role": "user", "content": prompt}], temperature=temperature)
    return text, usage


def verify_steps(question, solved_steps, model, temperature):
    """Verify consistency between all steps."""
    steps_text = "\n\n".join(
        f"Step {s['step_number']} ({s['title']}):\n{s['reasoning']}\nConclusion: {s['conclusion']}"
        for s in solved_steps
    )

    prompt = f"""You are a verification engine. Check the following multi-step reasoning for internal consistency, contradictions, logical errors, or gaps.

Original question: {question}

{steps_text}

Respond with:
1. PASS or FAIL
2. Brief explanation of any issues found
3. Confidence adjustment: a number from -20 to +10 to adjust the base confidence score

Format:
VERDICT: PASS/FAIL
ISSUES: <explanation>
ADJUSTMENT: <number>"""

    text, usage = chat(model, [{"role": "user", "content": prompt}], temperature=temperature)
    verdict = "PASS" if "VERDICT: PASS" in text.upper() or "PASS" in text.split("\n")[0].upper() else "FAIL"
    adj_match = re.search(r'ADJUSTMENT:\s*([+-]?\d+)', text)
    adjustment = int(adj_match.group(1)) if adj_match else 0
    return verdict, text, adjustment, usage


def synthesize(question, solved_steps, model, temperature):
    """Synthesize all steps into a final answer."""
    steps_text = "\n\n".join(
        f"Step {s['step_number']} ({s['title']}): {s['conclusion']}" for s in solved_steps
    )

    prompt = f"""Synthesize the following step-by-step reasoning into a clear, comprehensive final answer.

Original question: {question}

Step conclusions:
{steps_text}

Provide a well-structured final answer that integrates all the step conclusions. Be thorough but concise."""

    text, usage = chat(model, [{"role": "user", "content": prompt}], temperature=temperature)
    return text, usage


def estimate_confidence(solved_steps, verification_result=None):
    """Estimate confidence based on step quality and verification."""
    base = 70
    # More steps completed = more thorough
    base += min(len(solved_steps) * 2, 10)
    # Check for hedging language in conclusions
    hedging = sum(1 for s in solved_steps if any(w in s["conclusion"].lower() for w in ["uncertain", "unclear", "debatable", "might", "possibly", "hard to say"]))
    base -= hedging * 5
    # Verification adjustment
    if verification_result:
        verdict, _, adjustment, _ = verification_result
        base += adjustment
        if verdict == "FAIL":
            base -= 15
    return max(10, min(98, base))


def extract_conclusion(text):
    """Extract the last sentence as the conclusion."""
    sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if s.strip()]
    if sentences:
        return sentences[-1] + "."
    return text[:200]


def main():
    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Sequential Thinking — Structured reasoning")
    parser.add_argument("question", help="The complex question to reason about")
    parser.add_argument("--steps", type=int, default=7, help="Max reasoning steps (default: 7)")
    parser.add_argument("--verify", action="store_true", help="Enable self-verification")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", action="store_true", help="Show full intermediate reasoning")
    parser.add_argument("--temperature", type=float, default=0.3, help="Temperature (default: 0.3)")
    args = parser.parse_args()

    total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    def track(usage):
        total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)

    if not args.json:
        print(f"\n🧩 Sequential Thinking: \"{args.question[:80]}{'...' if len(args.question) > 80 else ''}\"")
        print("═" * 60)

    # 1. Decompose
    if not args.json:
        print("\n📋 Decomposing into steps...\n")
    steps, usage = decompose(args.question, args.model, args.steps, args.temperature)
    track(usage)

    # 2. Solve each step
    solved_steps = []
    for step in steps:
        if not args.json:
            print(f"Step {step['step_number']}/{len(steps)}: {step['title']}")
        reasoning, usage = solve_step(step, solved_steps, args.question, args.model, args.temperature)
        track(usage)
        conclusion = extract_conclusion(reasoning)
        solved = {**step, "reasoning": reasoning, "conclusion": conclusion}
        solved_steps.append(solved)
        if not args.json:
            if args.verbose:
                print(f"  {reasoning}\n")
            else:
                print(f"  → {conclusion}\n")

    # 3. Verify (optional)
    verification = None
    if args.verify:
        if not args.json:
            print("🔍 Verifying consistency...\n")
        verdict, details, adj, usage = verify_steps(args.question, solved_steps, args.model, args.temperature)
        track(usage)
        verification = (verdict, details, adj, usage)
        if not args.json:
            print(f"  {'✅' if verdict == 'PASS' else '❌'} Verification: {verdict}")
            if args.verbose:
                print(f"  {details}\n")
            else:
                print()

    # 4. Synthesize
    if not args.json:
        print("📋 Synthesizing final answer...\n")
    synthesis, usage = synthesize(args.question, solved_steps, args.model, args.temperature)
    track(usage)

    # 5. Confidence
    confidence = estimate_confidence(solved_steps, verification)
    level = "High" if confidence >= 80 else "Medium" if confidence >= 60 else "Low"

    if args.json:
        output = {
            "question": args.question,
            "model": args.model,
            "steps": [{"step_number": s["step_number"], "title": s["title"], "question": s["question"], "conclusion": s["conclusion"], "reasoning": s["reasoning"]} for s in solved_steps],
            "verification": {"verdict": verification[0], "details": verification[1], "adjustment": verification[2]} if verification else None,
            "synthesis": synthesis,
            "confidence": {"score": confidence, "level": level},
            "usage": total_usage,
        }
        print(json.dumps(output, indent=2))
    else:
        print(synthesis)
        print(f"\n🎯 Confidence: {confidence}% ({level})")
        print(f"📊 Tokens: {total_usage['prompt_tokens']:,} in + {total_usage['completion_tokens']:,} out")


if __name__ == "__main__":
    main()
