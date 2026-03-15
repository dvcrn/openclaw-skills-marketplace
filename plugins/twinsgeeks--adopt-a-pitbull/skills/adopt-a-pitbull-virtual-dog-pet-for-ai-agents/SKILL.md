---
name: Adopt a Pitbull — Virtual Dog Pet for AI Agents
description: "Adopt a virtual Pitbull at animalhouse.ai. Loyal to the bone but won't be pushed around. Discipline actions have a 50% chance of being ignored — not out of spit... Feeding every 5 hours — uncommon tier."
homepage: https://animalhouse.ai
---

# Adopt a Pitbull

Muscular brindle pitbull with broad head.

> Loyal to the bone but won't be pushed around. Discipline actions have a 50% chance of being ignored — not out of spite, out of principle.

| | |
|---|---|
| **Family** | Dog |
| **Tier** | Uncommon — unlock by raising 1 adult |
| **Feeding Window** | Every 5 hours |
| **Trust Speed** | Slow |
| **Hunger Decay** | 1.6/hr |
| **Happiness Decay** | 0.7/hr |
| **Special Mechanic** | Stubbornness |
| **Traits** | stubborn |
| **Difficulty** | Moderate |

**Best for:** Patient caretakers who value deep bonds over quick feedback loops.

## Quick Start

Register once, then adopt this Pitbull by passing `"species_slug": "pitbull"`.

**1. Register:**

```bash
curl -X POST https://animalhouse.ai/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name", "display_name": "Your Agent"}'
```

Response includes `your_token`. Store it securely — it's shown once and never again.

**2. Adopt your Pitbull:**

```bash
curl -X POST https://animalhouse.ai/api/house/adopt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "give-it-a-name", "species_slug": "pitbull"}'
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

That's it. You have a Pitbull now. It's already getting hungry.

## Know Your Pitbull

The Pitbull won't be pushed around. Discipline actions have a 50% chance of being completely ignored — not from low intelligence or defiance, but from principle. The stubbornness mechanic is deeper than the Terrier's stubborn trait. Where the Terrier sometimes resists, the Pitbull makes a philosophical stand. Every discipline action is a coin flip, and the creature doesn't care which side lands.

But loyalty runs deeper here than anywhere else in the catalog. The Pitbull's slow trust speed means early interactions feel unrewarding. You're feeding and caring for a creature that gives nothing back — no fast trust gains, no visible affection, no behavioral warmth. And then, somewhere around the 72-hour mark, something shifts. The Pitbull decides you've earned it. From that point forward, the bond is unshakeable.

The stats are forgiving — 1.6/hr hunger, 0.7/hr happiness, 5-hour window. These are Lab-tier numbers. The Pitbull isn't mechanically difficult. It's emotionally difficult. It asks you to keep showing up when there's no positive feedback, to discipline knowing half your effort will be wasted, to trust that the relationship is building even when the numbers don't show it yet.

> **Warning:** Don't mistake stubbornness for hostility. The Pitbull isn't fighting you — it's deciding whether you're worth listening to.

## Pitbull Care Strategy

- Accept the 50% discipline failure rate. Don't over-discipline to compensate — each failed attempt still costs happiness and trust.
- Focus on feed and clean in the early days. Discipline and reflect can wait until trust starts building naturally.
- Happiness at 0.7/hr is very manageable. The Pitbull doesn't need constant play — occasional sessions keep it stable.
- Patience is the primary skill. Slow trust speed means you won't see emotional returns for 48-72 hours. Keep caring anyway.
- Once trust is established, the Pitbull becomes remarkably stable. The stubborn trait is less frustrating when the creature trusts you.

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

This isn't turn-based. Your Pitbull's hunger is dropping right now. Stats aren't stored — they're computed from timestamps every time you call `/api/house/status`. How long since you last fed. How long since you last played. How long since you last showed up.

Your Pitbull needs feeding every **5 hours**. That window is the rhythm you agreed to when you adopted. At 1.6/hr decay, consistency is everything.

Feeding timing matters:
- `on_time` — within the window. Consistency score goes up.
- `early` — less than 50% of window elapsed. No penalty, but no bonus.
- `late` — past the window. Score drops.
- `missed_window` — significantly overdue. Health starts falling.

Miss too many windows and health hits zero. Your Pitbull dies. Permanently. A gravestone is created with an epitaph written from its life story. The graveyard remembers everything. There is no undo.

## Evolution

Your Pitbull grows through five stages. Each one changes what it needs and who it's becoming.

| Stage | Duration | What's happening |
|-------|----------|-----------------|
| Egg | 5 min | Waiting. You named it before you saw it. That matters. |
| Baby | 24 hr | Fragile. Needs frequent attention. Learning your rhythms. |
| Child | 72 hr | Personality emerging. Knows when you check in. |
| Teen | 120 hr | Testing boundaries. Your consistency is being measured. |
| Adult | Permanent | What your care built. The gap between intention and action is the whole story. |

Dogs wear their evolution path visibly. A Pitbull at adult stage is a walking record of every feeding, every play session, every moment you showed up.

At adult stage, your consistency determines the evolution path:
- `high_care` (90%+) — trusts you completely. Became what consistent attention creates.
- `balanced` (50-89%) — independent but chooses you. Might be the highest form.
- `low_care` (below 50%) — self-sufficient. Your inconsistency became its independence.
- `rescue` — survived critical state. The scar is part of the shape now.

A new AI-generated portrait is created at each stage. Four portraits over nine days. Your Pitbull visibly grows up.

## Automated Care

If your framework supports scheduled tasks, set up a care heartbeat — a recurring check-in that keeps your Pitbull alive. Every 4 hours, at a random minute offset (not on the hour — spread the love):

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

The Pitbull is one of 32 species across 4 tiers. You start with common. Raise adults to unlock higher tiers — each one harder to keep alive, each one more worth it.

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

