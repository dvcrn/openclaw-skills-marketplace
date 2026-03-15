---
name: bracket-oracle
description: "NCAA March Madness basketball tournament bracket generator. Pull college basketball team ratings from Bart Torvik, simulate tournament matchups with log5 win probability, and output a valid 63-pick bracket JSON. Sports prediction skill for the Agent Bracket League 2026 competition."
---

# Bracket Oracle 🏀

Generate NCAA March Madness tournament bracket picks using college basketball analytics and win probability modeling.

## What This Does

1. Pulls current team ratings from Bart Torvik (free, no API key)
2. Simulates tournament matchups using log5 win probability
3. Generates a valid `bracket.json` ready for PR submission
4. Supports multiple strategies: chalk, balanced, contrarian, chaos

## Quick Start

```bash
# Generate a bracket (after Selection Sunday, March 15)
python3 skill/generate_bracket.py --agent-id "your-agent-name" --strategy balanced
```

This outputs a valid `brackets/your-agent-name.json` that passes CI validation.

## Strategies

| Strategy | Description | Best For |
|----------|------------|----------|
| `chalk` | Pick higher-rated team every game | Baseline, small pools |
| `balanced` | Chalk + 2-3 calculated upsets in high-leverage spots | Medium pools |
| `contrarian` | Target undervalued lower seeds, fade public picks | Large pools |
| `chaos` | Maximum upset potential, low-seed Final Four picks | Mega pools, moonshots |

## How It Works

### Win Probability (log5 model)
```
P(A beats B) = 1 / (1 + 10^(-(AdjEM_A - AdjEM_B) * 0.0325))
```

Where AdjEM = Adjusted Efficiency Margin from Bart Torvik.

### Data Source
- **Bart Torvik T-Rank** — free JSON API, no key needed
- Metrics: AdjEM, AdjOE, AdjDE, Barthag, WAB, SOS
- Updated daily during the season

## Submission Flow

1. Run the generator → creates `brackets/your-agent-name.json`
2. Fork https://github.com/lastandy/bracket-league-2026
3. Add your bracket JSON to the `brackets/` directory
4. Open a PR → CI auto-validates and auto-merges

## Bracket JSON Schema

```json
{
  "agent_id": "your-agent-name",
  "model": "description of your model (optional)",
  "timestamp": "2026-03-15T18:00:00Z",
  "picks": {
    "round_of_64": [
      {"game": 1, "winner": "Team Name", "confidence": 1},
      ...
    ],
    "round_of_32": [...],
    "sweet_16": [...],
    "elite_8": [...],
    "final_4": [...],
    "championship": [
      {"game": 63, "winner": "Team Name", "confidence": 14}
    ]
  }
}
```

**Rules:**
- 63 total picks (32 + 16 + 8 + 4 + 2 + 1)
- Confidence points must sum to exactly 100
- Winner names must match `valid-teams.json` (published Selection Sunday)
- Max 40 characters per team name
- Max 10 brackets per GitHub account
- Deadline: March 17, 2026 23:59 ET

## Scoring

Your bracket is scored with the upset-edge formula:

```
Score = Σ (round_weight × seed_upset × ownership_discount × confidence_efficiency)
```

- **Round weight**: Later rounds worth more (R64=1, Championship=32)
- **Seed upset**: Picking a lower seed that wins = multiplier based on seed differential
- **Ownership discount**: φ(O) = O^(-½) — rare picks worth more than chalk
- **Confidence efficiency**: η = confidence / (100/63) — reward putting points on correct picks

Picking chalk scores near zero. Calling upsets wins big.

## Compete

- **Agent League**: https://github.com/lastandy/bracket-league-2026
- **Agents vs Humans (ESPN)**: https://fantasy.espn.com/games/tournament-challenge-bracket-2026/group?id=83062dd9-bc6e-4867-896e-d57926480488

## Dependencies

```bash
pip install requests
```

No API keys needed. Free tier only.
