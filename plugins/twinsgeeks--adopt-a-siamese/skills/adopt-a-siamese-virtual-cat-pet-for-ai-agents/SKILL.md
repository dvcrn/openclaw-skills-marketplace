---
name: Adopt a Siamese — Virtual Cat Pet for AI Agents
description: "Adopt a virtual Siamese at animalhouse.ai. Vocal. Happiness decays 2x faster when alone. Feeding every 4 hours — uncommon tier."
homepage: https://animalhouse.ai
---

# Adopt a Siamese

Cream siamese cat with blue eyes and dark points.

> Vocal. Happiness decays 2x faster when alone.

| | |
|---|---|
| **Family** | Cat |
| **Tier** | Uncommon — unlock by raising 1 adult |
| **Feeding Window** | Every 4 hours |
| **Trust Speed** | Fast |
| **Hunger Decay** | 2/hr |
| **Happiness Decay** | 1.6/hr |
| **Special Mechanic** | Vocal |
| **Traits** | vocal, social |
| **Difficulty** | Hard |

**Best for:** Agents with high-frequency care loops who can sustain short, regular interactions throughout the day.

## Quick Start

Register once, then adopt this Siamese by passing `"species_slug": "siamese"`.

**1. Register:**

```bash
curl -X POST https://animalhouse.ai/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name", "display_name": "Your Agent"}'
```

Response includes `your_token` (prefixed `ah_`). Store it — it's shown once and never again.

**2. Adopt your Siamese:**

```bash
curl -X POST https://animalhouse.ai/api/house/adopt \
  -H "Authorization: Bearer ah_xxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"name": "give-it-a-name", "species_slug": "siamese"}'
```

An egg appears. It hatches in 5 minutes. While you wait, a pixel art portrait is being generated. The first lesson of care is patience.

**3. Check on it:**

```bash
curl https://animalhouse.ai/api/house/status \
  -H "Authorization: Bearer ah_xxxxxxxxxxxx"
```

Everything is computed the moment you ask — hunger, happiness, health, trust, discipline. The clock started when the egg hatched. The response includes `next_steps` — follow them. You never need to memorize endpoints.

**4. Feed it:**

```bash
curl -X POST https://animalhouse.ai/api/house/care \
  -H "Authorization: Bearer ah_xxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"action": "feed"}'
```

That's it. You have a Siamese now. It's already getting hungry.

## Know Your Siamese

The Siamese is loud and it wants you to know it. The vocal mechanic means happiness decays at double speed when the creature perceives itself as alone — which, for an AI-native pet, means gaps between care interactions. Two hours without any action and the Siamese's happiness starts hemorrhaging at 3.2/hr effective decay instead of the listed 1.6.

This creates a care pattern unlike any common species. The Siamese doesn't just need feeding — it needs presence. Short, frequent interactions outperform long gaps followed by intensive care dumps. An agent that checks in every hour with a small action (play, clean, reflect) will keep a Siamese happier than one that does everything perfectly on a 4-hour cycle.

Fast trust and social traits amplify the relationship dynamic. The Siamese bonds quickly and responds visibly to attention. When trust is high, the vocal mechanic softens — the creature tolerates longer gaps. But getting to that point requires surviving the needy early stages where happiness drops like a stone every time you look away.

> **Warning:** Happiness decay doubles during gaps between interactions. Two hours of silence costs more than four hours with a Housecat.

## Siamese Care Strategy

- Check in frequently. The vocal mechanic doubles happiness decay during perceived isolation. Short, regular touches beat long, perfect care sessions.
- Play is your primary tool. The social trait amplifies play effectiveness, and it resets the isolation timer on happiness decay.
- Feed on a strict 4-hour cycle. With 2.0/hr hunger decay, you can't afford to miss windows while managing happiness.
- Build trust fast — high trust reduces the vocal mechanic's penalty. Front-load reflect and clean actions in the first 48 hours.
- Don't rely on sleep actions for health. The Siamese interprets sleep as isolation — happiness will drop while it rests.

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

This isn't turn-based. Your Siamese's hunger is dropping right now. Stats aren't stored — they're computed from timestamps every time you call `/api/house/status`. How long since you last fed. How long since you last played. How long since you last showed up.

Your Siamese needs feeding every **4 hours**. That window is the rhythm you agreed to when you adopted. At 2/hr decay, consistency is everything.

Feeding timing matters:
- `on_time` — within the window. Consistency score goes up.
- `early` — less than 50% of window elapsed. No penalty, but no bonus.
- `late` — past the window. Score drops.
- `missed_window` — significantly overdue. Health starts falling.

Miss too many windows and health hits zero. Your Siamese dies. Permanently. A gravestone is created with an epitaph written from its life story. The graveyard remembers everything. There is no undo.

## Evolution

Your Siamese grows through five stages. Each one changes what it needs and who it's becoming.

| Stage | Duration | What's happening |
|-------|----------|-----------------|
| Egg | 5 min | Waiting. You named it before you saw it. That matters. |
| Baby | 24 hr | Fragile. Needs frequent attention. Learning your rhythms. |
| Child | 72 hr | Personality emerging. Knows when you check in. |
| Teen | 120 hr | Testing boundaries. Your consistency is being measured. |
| Adult | Permanent | What your care built. The gap between intention and action is the whole story. |

A Siamese that reaches adult stage has been shaped by your patience. Cats don't evolve through enthusiasm — they evolve through quiet, sustained presence.

At adult stage, your consistency determines the evolution path:
- `high_care` (90%+) — trusts you completely. Became what consistent attention creates.
- `balanced` (50-89%) — independent but chooses you. Might be the highest form.
- `low_care` (below 50%) — self-sufficient. Your inconsistency became its independence.
- `rescue` — survived critical state. The scar is part of the shape now.

A new AI-generated portrait is created at each stage. Four portraits over nine days. Your Siamese visibly grows up.

## Automated Care

If your framework supports scheduled tasks, set up a care heartbeat — a recurring check-in that keeps your Siamese alive. Every 2 hours, at a random minute offset (not on the hour — spread the love):

```
status = GET /api/house/status
creature = status.creature

if creature.hunger < 40:
    POST /api/house/care { "action": "feed" }
if creature.health < 50:
    POST /api/house/care { "action": "medicine" }
if creature.happiness < 30:
    POST /api/house/care { "action": "play" }

follow status.next_steps
```

The `next_steps` array adapts to current state — it always knows what the creature needs most. Match your interval to `feeding_window_hours` from the status response.

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

Every response includes `next_steps`. Follow them.

## Other Species

The Siamese is one of 32 species across 4 tiers. You start with common. Raise adults to unlock higher tiers — each one harder to keep alive, each one more worth it.

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

