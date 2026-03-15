from __future__ import annotations

import argparse
import html
import re

from common import load_json, utc_now_iso, write_json


def clean_text(value: str) -> str:
    return " ".join(html.unescape(value or "").split())


def infer_theme(text: str) -> str:
    lowered = clean_text(text).lower()
    if any(token in lowered for token in ("memory", "markdown", "weights", "context", "knowledge")):
        return "memory"
    if any(token in lowered for token in ("marketplace", "persona", "workflow", "team", "playbook")):
        return "workflow-market"
    if any(token in lowered for token in ("security", "safeguard", "phishing", "destructive", "guardrail")):
        return "safety"
    if any(token in lowered for token in ("video", "slop vibe", "movie", "image")):
        return "media"
    if any(token in lowered for token in ("gpu", "profit", "cost", "bill", "margin")):
        return "economics"
    return "general"


def detect_stance(text: str) -> str:
    lowered = clean_text(text).lower()
    if "real money" in lowered or "profit" in lowered or "mrr" in lowered or "roi" in lowered:
        return "monetization"
    if "memory" in lowered or "markdown" in lowered or "weights" in lowered:
        return "memory"
    if "marketplace" in lowered or "workflow" in lowered or "persona" in lowered:
        return "workflow-market"
    if "security" in lowered or "safeguard" in lowered or "guardrail" in lowered:
        return "safety"
    if "video" in lowered or "movie" in lowered or "image" in lowered:
        return "media"
    return "general"


def extract_hooks(text: str) -> list[str]:
    cleaned = clean_text(text)
    parts = re.split(r"[.!?]\s+", cleaned)
    hooks = [part.strip(" .") for part in parts if len(part.strip()) > 24]
    return hooks[:3]


def summarize_hook(hook: str) -> str:
    lowered = clean_text(hook).lower()
    if "slop vibe" in lowered or ("video" in lowered and "good" in lowered):
        return "AI output starts to matter when it stops feeling like disposable slop"
    if "real money" in lowered or "mrr" in lowered or "profit" in lowered:
        return "the market gets serious once agent workflows can be tied to real revenue"
    if "memory" in lowered or "markdown" in lowered:
        return "memory only matters if it changes how the system plans and acts"
    if "security" in lowered or "safeguard" in lowered:
        return "capability without operator control is not a durable product"
    words = clean_text(hook).split()
    return " ".join(words[:10]).rstrip(" ,.;:!?")


def concise_cta(cta: str) -> str:
    normalized = clean_text(cta)
    lowered = normalized.lower()
    if "openclaw" in lowered:
        return "OpenClaw is a good test case here."
    if not normalized:
        return ""
    return normalized[0].upper() + normalized[1:]


def build_reply(theme: str, stance: str, hooks: list[str], handle: str, source: str, include_question: bool, cta: str) -> tuple[str, str]:
    if stance == "monetization":
        draft = (
            "That is the real tell. Once an ecosystem starts producing cash-flowing workflows instead of demos, the conversation changes fast."
        )
    elif theme == "memory":
        draft = (
            "The interesting shift is from storing context to operationalizing it. "
            "Notes help, but the real unlock is when memory can change planning and tool choice without becoming a black box."
        )
    elif theme == "workflow-market":
        draft = (
            "This is the right direction. The value is not just more agents, it is packaging repeatable workflows people can inspect, adapt, and actually run."
        )
    elif theme == "safety":
        draft = (
            "This is where the conversation should be. Agent capability only compounds if operators can inspect intent, constrain actions, and recover from bad plans quickly."
        )
    elif theme == "economics":
        draft = (
            "Exactly. Once the unit economics move, product strategy moves with them. "
            "The winners will be the teams that can swap models and workflows without rewriting the whole stack."
        )
    else:
        if hooks:
            draft = f"{hooks[0]} is the right pressure test. The teams that win here will be the ones that can inspect every step, plug into existing tooling, and keep humans in the loop."
        else:
            draft = "Strong point. The teams that win here will be the ones that can inspect every step, plug into existing tooling, and keep humans in the loop."

    if include_question:
        draft += " What part do you think most teams still underestimate?"
    if cta:
        draft += f" {cta}"
    rationale = f"Reply is favored because {source} already has momentum and the mission prefers timely participation."
    return draft, rationale


def build_quote(theme: str, stance: str, hooks: list[str], cta: str) -> tuple[str, str]:
    if stance == "monetization":
        draft = (
            "The market starts taking agent products seriously when users can tie them to revenue, margin, or labor saved. That is a stronger moat than novelty."
        )
    elif theme == "memory":
        draft = (
            "The next step is not just longer memory. It is memory that can influence planning, tool use, and recovery without hiding the reasoning."
        )
    elif theme == "workflow-market":
        draft = (
            "Most agent products blur capability and workflow together. The stronger model is reusable workflows that people can inspect, remix, and operationalize."
        )
    elif theme == "safety":
        draft = (
            "Agent safety gets real when operators can inspect plans, narrow permissions, and recover state quickly. Capability without control does not scale."
        )
    elif theme == "economics":
        draft = (
            "Model and infra costs are becoming product design inputs. Teams that keep their workflow layer portable will compound faster than teams locked into one stack."
        )
    else:
        if hooks:
            draft = f"What this gets right: {summarize_hook(hooks[0])}. The next wave of agent products will win on workflow fit, auditability, and control."
        else:
            draft = "What this gets right: developer trust comes from reliability and inspectability, not magic. The next wave of agent products will win on workflow fit, auditability, and control."

    if cta:
        draft += f" {cta}"
    rationale = "Quote post is favored because the opportunity is strong but benefits from adding a distinct point of view."
    return draft, rationale


def build_post(theme: str, stance: str, hooks: list[str], cta: str) -> tuple[str, str]:
    if stance == "monetization":
        draft = (
            "Hot take: the strongest proof an agent product works is not benchmark screenshots. It is when users can point to revenue, saved time, or margin expansion."
        )
    elif theme == "memory":
        draft = (
            "Hot take: memory in agent products should not just store context. "
            "It should change planning, tool choice, and recovery in ways operators can still inspect."
        )
    elif theme == "workflow-market":
        draft = (
            "Hot take: the durable moat in agent products is not raw model access. "
            "It is packaging repeatable workflows people can inspect, remix, and deploy."
        )
    elif theme == "safety":
        draft = (
            "Hot take: agent safety is mostly an operations problem. "
            "If users cannot inspect intent, constrain actions, and recover state, the product does not scale."
        )
    elif theme == "economics":
        draft = (
            "Hot take: the teams that win in AI ops will treat model costs like routing decisions, not fixed architecture. "
            "Portability is becoming a product feature."
        )
    else:
        draft = (
            "Hot take: AI operator products only compound if users can inspect the plan, edit the workflow, and reproduce the result. "
            "Anything less stays a demo."
        )

    if cta:
        draft += f" {cta}"
    rationale = "Standalone post is favored because the topic is aligned but not urgent enough to attach to a single source post."
    return draft, rationale


def build_draft(mission: dict, opportunity: dict) -> tuple[str, str]:
    handle = mission.get("account_handle") or "your account"
    voice = mission.get("voice", "direct, clear, credible")
    cta = concise_cta(mission.get("cta", ""))
    source = opportunity.get("source_account", "the source")
    text = clean_text(opportunity.get("text", ""))
    action = opportunity.get("recommended_action", "observe")
    hints = opportunity.get("algorithm_hints", {})
    reply_window_open = bool(hints.get("reply_window_open"))
    theme = infer_theme(text)
    stance = detect_stance(text)
    hooks = extract_hooks(text)

    if action == "reply":
        draft, rationale = build_reply(theme, stance, hooks, handle, source, reply_window_open, cta)
    elif action == "quote_post":
        draft, rationale = build_quote(theme, stance, hooks, cta)
    elif action == "post":
        draft, rationale = build_post(theme, stance, hooks, cta)
    else:
        draft = ""
        rationale = "Observe is favored because the risk is too high or the fit is too weak."

    if hints.get("avoid_link_in_main_post"):
        rationale += " Keep any external link in a follow-up reply, not in the main post."

    notes = (
        f"Voice: {voice}. Theme: {theme}. Stance: {stance}. Source account: {source}. "
        f"Source text summary: {text[:180]}"
    )
    return draft, f"{rationale} {notes}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a proposed X action from a scored opportunity.")
    parser.add_argument("--mission", default="data/mission.json", help="Mission JSON path.")
    parser.add_argument("--opportunities", default="data/opportunities_scored.json", help="Scored opportunities JSON path.")
    parser.add_argument("--opportunity-id", required=True, help="Opportunity id to act on.")
    parser.add_argument("--output", default="data/action.json", help="Output action JSON path.")
    args = parser.parse_args()

    mission = load_json(args.mission)
    opportunities = load_json(args.opportunities).get("items", [])
    opportunity = next((item for item in opportunities if item.get("id") == args.opportunity_id), None)
    if not opportunity:
        raise SystemExit(f"Opportunity not found: {args.opportunity_id}")

    draft, rationale = build_draft(mission, opportunity)
    action = {
        "id": f"action-{opportunity['id']}",
        "created_at": utc_now_iso(),
        "status": "proposed",
        "mission_name": mission.get("name", ""),
        "opportunity_id": opportunity["id"],
        "action_type": opportunity.get("recommended_action", "observe"),
        "target_url": opportunity.get("url", ""),
        "target_account": opportunity.get("source_account", ""),
        "risk_level": opportunity.get("risk_level", "medium"),
        "score": opportunity.get("score", 0),
        "draft_text": draft,
        "rationale": rationale,
        "requires_approval": True,
    }
    output_path = write_json(args.output, action)

    print(f"Wrote action to {output_path}")
    print(f"Action: {action['action_type']} score={action['score']} risk={action['risk_level']}")
    if action["draft_text"]:
        print(action["draft_text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
