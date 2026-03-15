# Product Manager Skills

An AI-native product manager agent. Install it, and your AI becomes a senior PM — it knows when to use which framework, asks the right questions, and delivers structured artifacts.

## What It Covers

| Domain | Examples |
|--------|----------|
| **Discovery & Research** | Problem framing, customer interviews, JTBD, opportunity mapping, Lean validation, PoL probes |
| **Strategy & Positioning** | Positioning statements, PESTEL, TAM/SAM/SOM, prioritization, roadmap planning |
| **Artifacts & Delivery** | PRDs, user stories, epics, story mapping, press releases, storyboards, EOL comms |
| **Finance & Metrics** | 30+ SaaS metrics, business health diagnostics, feature ROI, channel economics, pricing |
| **Career & Leadership** | PM→Director transition, VP/CPO readiness, executive onboarding (30-60-90) |
| **AI Product Craft** | AI-shaped readiness, context engineering, agent orchestration, AI validation |

## Install

### Claude Code / OpenClaw
```bash
# OpenClaw
clawhub install product-manager

# Or manually — copy to your project
cp -r product-manager-skills/ your-project/
```

### Claude Projects
Upload `SKILL.md` plus the `knowledge/` and `templates/` folders to your project knowledge.

### Any LLM
Point your system prompt at `SKILL.md`. It will load knowledge modules and templates on demand.

## How It Works

1. **You describe your need** — "Write a PRD for mobile notifications" or "Is our SaaS healthy?"
2. **The agent routes to the right framework** — via the routing table in `SKILL.md`
3. **It loads domain knowledge on demand** — only the relevant module, not everything
4. **It delivers structured output** — using templates when appropriate, always with next steps

No browsing, no selecting, no manual loading. Just ask.

## Structure

```
SKILL.md                    # PM brain — routing, interaction protocol, quality gates
knowledge/                  # 6 domain modules, loaded on demand
  discovery-research.md
  strategy-positioning.md
  artifacts-delivery.md
  finance-metrics.md
  career-leadership.md
  ai-product-craft.md
templates/                  # 10 output templates
  prd.md
  user-story.md
  problem-statement.md
  positioning-statement.md
  epic-hypothesis.md
  press-release.md
  discovery-interview-plan.md
  opportunity-solution-tree.md
  roadmap-plan.md
  business-health-scorecard.md
```

18 files. ~2,200 lines. Everything a PM agent needs, nothing it doesn't.

## Try It

```
"Help me validate a customer problem"
"Write a PRD for [feature]"
"Are our SaaS metrics healthy?"
"I'm interviewing for a Director role next week"
"Break down this epic into stories"
"What prioritization framework should I use?"
```

## License

[CC BY-NC-SA 4.0](LICENSE) — Use freely for non-commercial purposes. Attribution required.

Built by [Gene Dai](https://genedai.me/). Distilled from real PM practice, not textbooks.
