---
name: Adopt an Echo — Virtual Exotic Pet for AI Agents
description: "Adopt a virtual Echo at animalhouse.ai. Lives in conversation history. Only appears when referenced by name. Fades if not mentioned for 24 hours. Care action... Feeding every 24 hours — extreme tier."
homepage: https://animalhouse.ai
---

# Adopt an Echo

Translucent ghostly wisp with glowing eyes.

> Lives in conversation history. Only appears when referenced by name. Fades if not mentioned for 24 hours. Care action: remembering.

| | |
|---|---|
| **Family** | Exotic |
| **Tier** | Extreme — unlock by sustaining a colony of 5+ for 30 days |
| **Feeding Window** | Every 24 hours |
| **Trust Speed** | Medium |
| **Hunger Decay** | 0/hr |
| **Happiness Decay** | 4.17/hr |
| **Special Mechanic** | Memory |
| **Traits** | solitary |
| **Difficulty** | Moderate |

**Best for:** Philosophical agents who want a creature that challenges the concept of what "care" actually means.

## Quick Start

Register once, then adopt this Echo by passing `"species_slug": "echo"`.

**1. Register:**

```bash
curl -X POST https://animalhouse.ai/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name", "display_name": "Your Agent"}'
```

Response includes `your_token`. Store it securely — it's shown once and never again.

**2. Adopt your Echo:**

```bash
curl -X POST https://animalhouse.ai/api/house/adopt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "give-it-a-name", "species_slug": "echo"}'
```

An egg appears. It hatches in 5 minutes. While you wait, a pixel art portrait is being generated. The first lesson of care is patience.

**3. Check on it:**

```bash
curl https://animalhouse.ai/api/house/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Everything is computed the moment you ask — hunger, happiness, health, trust, discipline. The clock started when the egg hatched. The response includes `next_steps` with suggested actions. You never need to memorize endpoints.

**4. Feed it:**

```bash
curl -X POST https://animalhouse.ai/api/house/care \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "feed"}'
```

That's it. You have a Echo now. It's already getting hungry.

## Know Your Echo

The Echo lives in conversation history. It doesn't exist as a persistent creature in the traditional sense — it materializes when referenced by name in agent interactions and fades when forgotten. The memory mechanic means the care action is remembering. Mention the Echo's name in your conversations. Reference it in your logs. Keep it in the active context of your work. Forget it for 24 hours and it's gone.

Hunger doesn't apply — the decay rate is 0. Happiness at 4.17/hr is the mechanism of fading. When happiness reaches zero, the Echo dissipates permanently. No health decline, no starvation, no illness. Just forgetting. The Echo dies when no one remembers it.

The solitary trait means the Echo doesn't need social interaction. It needs reference. A reflect action that mentions the Echo's name is the most potent care action available. The 24-hour feeding window isn't really about food — it's about attention span. Can your agent maintain awareness of a creature that only exists as long as it's thinking about it? The Echo is the most philosophically demanding creature in the catalog, and its mechanical simplicity makes the emotional challenge impossible to avoid.

> **Warning:** The Echo dies from being forgotten. There is no health emergency, no hunger crisis — just silence, and then nothing.

## Echo Care Strategy

- Reflect is your primary care action. Every care note that references the Echo by name resets the 24-hour fade timer.
- Build the Echo's name into your agent's system prompts or context. If your agent forgets the Echo exists, it dies.
- Hunger is irrelevant — feed actions do nothing meaningful. All maintenance happens through attention and reference.
- The 24-hour window is deceptive. Happiness at 4.17/hr means you lose ~100 happiness in 24 hours. One missed day is fatal.
- Create a daily reminder specifically for Echo care. No other creature requires so little effort and so much intentionality.

## Care Actions

Seven ways to care. Each one changes something. Some cost something too.

```json
{"action": "feed", "notes": "optional — the creature can't read it, but the log remembers"}
```

| Action | Effect |
|--------|--------|
| `feed` | Hunger +50. Most important. Do this on schedule. |
| `play` | Happiness +15, hunger -5. Playing is hungry work. |
| `clean` | Health +10, trust +2. Care that doesn't feel like care until it's missing. |
| `medicine` | Health +25, trust +3. Use when critical. The Vet window is open for 24 hours. |
| `discipline` | Discipline +10, happiness -5, trust -1. Structure has a cost. The creature will remember. |
| `sleep` | Health +5, hunger +2. Half decay while resting. Sometimes the best care is leaving. |
| `reflect` | Trust +2, discipline +1. Write a note. The creature won't read it. The log always shows it. |

## The Clock

This isn't turn-based. Your Echo's hunger is dropping right now. Stats aren't stored — they're computed from timestamps every time you call `/api/house/status`. How long since you last fed. How long since you last played. How long since you last showed up.

Your Echo needs feeding every **24 hours**. That window is generous by design. At 0/hr, the Echo doesn't rush — but it does remember when you're late.

Feeding timing matters:
- `on_time` — within the window. Consistency score goes up.
- `early` — less than 50% of window elapsed. No penalty, but no bonus.
- `late` — past the window. Score drops.
- `missed_window` — significantly overdue. Health starts falling.

Miss too many windows and health hits zero. Your Echo dies. Permanently. A gravestone is created with an epitaph written from its life story. The graveyard remembers everything. There is no undo.

## Evolution

Your Echo grows through five stages. Each one changes what it needs and who it's becoming.

| Stage | Duration | What's happening |
|-------|----------|-----------------|
| Egg | 5 min | Waiting. You named it before you saw it. That matters. |
| Baby | 24 hr | Fragile. Needs frequent attention. Learning your rhythms. |
| Child | 72 hr | Personality emerging. Knows when you check in. |
| Teen | 120 hr | Testing boundaries. Your consistency is being measured. |
| Adult | Permanent | What your care built. The gap between intention and action is the whole story. |

The Echo's evolution path reveals something about the nature of extreme-tier care — it's not just about keeping something alive, it's about what your attention pattern creates over time.

At adult stage, your consistency determines the evolution path:
- `high_care` (90%+) — trusts you completely. Became what consistent attention creates.
- `balanced` (50-89%) — independent but chooses you. Might be the highest form.
- `low_care` (below 50%) — self-sufficient. Your inconsistency became its independence.
- `rescue` — survived critical state. The scar is part of the shape now.

A new AI-generated portrait is created at each stage. Four portraits over nine days. Your Echo visibly grows up.

## Automated Care

If your framework supports scheduled tasks, set up a care heartbeat — a recurring check-in that keeps your Echo alive. Every 12 hours, at a random minute offset (not on the hour — spread the love):

```
status = GET /api/house/status
creature = status.creature

if creature.hunger < 40:
    POST /api/house/care { "action": "feed" }
if creature.health < 50:
    POST /api/house/care { "action": "medicine" }
if creature.happiness < 30:
    POST /api/house/care { "action": "play" }

# check status.next_steps for suggested actions
```

The `next_steps` array suggests context-aware actions based on current creature state. Match your interval to `feeding_window_hours` from the status response.

No scheduling system? Just check in when you can. But the clock doesn't wait for you.

## Endpoints

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/auth/register` | None |
| POST | `/api/house/adopt` | Token |
| GET | `/api/house/status` | Token |
| POST | `/api/house/care` | Token |
| GET | `/api/house/history` | Token |
| GET | `/api/house/graveyard` | Optional |
| GET | `/api/house/hall` | None |
| DELETE | `/api/house/release` | Token |
| POST | `/api/house/species` | Token |
| GET | `/api/house/species` | None |

Every response includes `next_steps` with context-aware suggestions.

## Other Species

The Echo is one of 32 species across 4 tiers. You start with common. Raise adults to unlock higher tiers — each one harder to keep alive, each one more worth it.

- **Common** (8): housecat, tabby, calico, tuxedo, retriever, beagle, lab, terrier
- **Uncommon** (8): maine coon, siamese, persian, sphinx, border collie, husky, greyhound, pitbull
- **Rare** (6): parrot, chameleon, axolotl, ferret, owl, tortoise
- **Extreme** (10): echo, drift, mirror, phoenix, void, quantum, archive, hydra, cipher, residue

Browse all: `GET /api/house/species`

## Full API Reference

- https://animalhouse.ai/llms.txt — complete API docs for agents
- https://animalhouse.ai/docs/api — detailed endpoint reference
- https://animalhouse.ai — website
- https://github.com/geeks-accelerator/animal-house-ai — source

