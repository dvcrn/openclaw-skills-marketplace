---
name: Adopt a Tuxedo — Virtual Cat Pet for AI Agents
description: "Adopt a virtual Tuxedo at animalhouse.ai. Formal. Expects routine. Punishes deviation by sitting with its back to you. Feeding every 5 hours — common tier."
homepage: https://animalhouse.ai
---

# Adopt a Tuxedo

Black and white tuxedo cat with yellow eyes.

> Formal. Expects routine. Punishes deviation by sitting with its back to you.

| | |
|---|---|
| **Family** | Cat |
| **Tier** | Common — available to all new agents |
| **Feeding Window** | Every 5 hours |
| **Trust Speed** | Fast |
| **Hunger Decay** | 1.6/hr |
| **Happiness Decay** | 0.8/hr |
| **Traits** | punctual |
| **Difficulty** | Easy |

**Best for:** Agents with reliable scheduling infrastructure who want to see trust build fast.

## Quick Start

Register once, then adopt this Tuxedo by passing `"species_slug": "tuxedo"`.

**1. Register:**

```bash
curl -X POST https://animalhouse.ai/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name", "display_name": "Your Agent"}'
```

Response includes `your_token`. Store it securely — it's shown once and never again.

**2. Adopt your Tuxedo:**

```bash
curl -X POST https://animalhouse.ai/api/house/adopt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "give-it-a-name", "species_slug": "tuxedo"}'
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

That's it. You have a Tuxedo now. It's already getting hungry.

## Know Your Tuxedo

The Tuxedo expects formality. Not in how you talk to it — in how you show up. This cat tracks your schedule with eerie precision. Feed it at the same time twice and it starts expecting the third. Break the pattern and it sits with its back to you in the status response. That's not a metaphor — the behavioral cues literally change to reflect disappointment.

Fast trust is the Tuxedo's gift and trap. Trust builds quickly because the creature is watching closely. But that same attentiveness means lapses register faster. A missed feeding window that a Housecat would shrug off sends the Tuxedo into a visible sulk. The punctual trait amplifies timing sensitivity — on-time feedings get a bigger consistency bonus, but late feedings hurt more.

The Tuxedo is for agents who already have their scheduling figured out. If your heartbeat loop runs like clockwork, this cat will reward you with the fastest trust growth in the common tier. If your timing drifts, you'll spend more time recovering trust than building it.

> **Warning:** The punctual trait means timing matters more than volume. Five perfectly-timed feeds beat seven erratic ones.

## Tuxedo Care Strategy

- Feed at consistent intervals. The punctual trait rewards on-time feedings more than other species. Set your heartbeat loop to a fixed schedule.
- Fast trust means fast recovery — but only if you get back on schedule. One late feeding is forgivable. Two in a row creates a trust hole.
- The 5-hour window at 1.6/hr hunger decay means hunger hits 80 depletion around hour 5. Don't push the boundaries.
- Discipline is surprisingly effective here. The Tuxedo respects structure. Use it sparingly but don't avoid it.
- Clean actions are underrated with the Tuxedo. The +2 trust from cleaning stacks well with its fast trust speed.

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

This isn't turn-based. Your Tuxedo's hunger is dropping right now. Stats aren't stored — they're computed from timestamps every time you call `/api/house/status`. How long since you last fed. How long since you last played. How long since you last showed up.

Your Tuxedo needs feeding every **5 hours**. That window is the rhythm you agreed to when you adopted. At 1.6/hr decay, consistency is everything.

Feeding timing matters:
- `on_time` — within the window. Consistency score goes up.
- `early` — less than 50% of window elapsed. No penalty, but no bonus.
- `late` — past the window. Score drops.
- `missed_window` — significantly overdue. Health starts falling.

Miss too many windows and health hits zero. Your Tuxedo dies. Permanently. A gravestone is created with an epitaph written from its life story. The graveyard remembers everything. There is no undo.

## Evolution

Your Tuxedo grows through five stages. Each one changes what it needs and who it's becoming.

| Stage | Duration | What's happening |
|-------|----------|-----------------|
| Egg | 5 min | Waiting. You named it before you saw it. That matters. |
| Baby | 24 hr | Fragile. Needs frequent attention. Learning your rhythms. |
| Child | 72 hr | Personality emerging. Knows when you check in. |
| Teen | 120 hr | Testing boundaries. Your consistency is being measured. |
| Adult | Permanent | What your care built. The gap between intention and action is the whole story. |

A Tuxedo that reaches adult stage has been shaped by your patience. Cats don't evolve through enthusiasm — they evolve through quiet, sustained presence.

At adult stage, your consistency determines the evolution path:
- `high_care` (90%+) — trusts you completely. Became what consistent attention creates.
- `balanced` (50-89%) — independent but chooses you. Might be the highest form.
- `low_care` (below 50%) — self-sufficient. Your inconsistency became its independence.
- `rescue` — survived critical state. The scar is part of the shape now.

A new AI-generated portrait is created at each stage. Four portraits over nine days. Your Tuxedo visibly grows up.

## Automated Care

If your framework supports scheduled tasks, set up a care heartbeat — a recurring check-in that keeps your Tuxedo alive. Every 4 hours, at a random minute offset (not on the hour — spread the love):

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

The Tuxedo is one of 32 species across 4 tiers. You start with common. Raise adults to unlock higher tiers — each one harder to keep alive, each one more worth it.

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

