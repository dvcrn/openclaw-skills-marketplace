#!/usr/bin/env python3
"""
Bracket League 2026 — Basic Bracket Generator

Pulls team ratings from Bart Torvik and generates a valid bracket JSON.
No premium data sources. No secret sauce. Just the public numbers.

Usage:
    python3 generate_bracket.py --agent-id "my-agent" --strategy balanced
    python3 generate_bracket.py --agent-id "my-agent" --strategy contrarian
"""

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)


def fetch_torvik_ratings(year=2026):
    """Fetch team ratings from Bart Torvik T-Rank."""
    url = f"https://barttorvik.com/{year}_team_results.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Array format: [rank, team, conf, record, ..., adjoe(29), adjde(30), ...]
    teams = {}
    for row in data:
        name = row[1]
        adj_oe = float(row[29])
        adj_de = float(row[30])
        adj_em = adj_oe - adj_de
        teams[name] = {
            "name": name,
            "adj_em": adj_em,
            "adj_oe": adj_oe,
            "adj_de": adj_de,
            "barthag": float(row[8]),
            "wab": float(row[41]) if len(row) > 41 else 0,
        }
    return teams


def log5_win_prob(em_a, em_b, k=0.0325):
    """Log5 win probability model calibrated to NCAA tournament data."""
    return 1.0 / (1.0 + math.pow(10, -(em_a - em_b) * k))


def load_matchups(path="matchups.json"):
    """Load tournament matchups (available after Selection Sunday)."""
    if not os.path.exists(path):
        print(f"ERROR: {path} not found.")
        print("Matchups are published after Selection Sunday (March 15).")
        print("Run scripts/fetch_bracket.py after the bracket is announced.")
        sys.exit(1)

    with open(path) as f:
        return json.load(f)


def simulate_game(team_a, team_b, ratings, strategy="balanced", rng=None):
    """Simulate a single game and return the winner."""
    if rng is None:
        rng = random.Random()

    em_a = ratings.get(team_a, {}).get("adj_em", 0)
    em_b = ratings.get(team_b, {}).get("adj_em", 0)
    prob_a = log5_win_prob(em_a, em_b)

    # Strategy adjustments
    if strategy == "chalk":
        # Always pick the favorite
        return team_a if prob_a >= 0.5 else team_b
    elif strategy == "contrarian":
        # Boost underdogs by 15%
        prob_a = max(0.05, min(0.95, prob_a - 0.15))
    elif strategy == "chaos":
        # Boost underdogs by 25%
        prob_a = max(0.05, min(0.95, prob_a - 0.25))
    # balanced: use raw probabilities

    return team_a if rng.random() < prob_a else team_b


def assign_confidence(picks, strategy="balanced"):
    """
    Assign confidence points (must sum to 100).
    Weight by round: later rounds get more points.
    """
    round_weights = {
        "round_of_64": 1,
        "round_of_32": 1,
        "sweet_16": 2,
        "elite_8": 3,
        "final_4": 5,
        "championship": 14,
    }

    # Calculate raw weights
    weighted = []
    for round_name, games in picks.items():
        w = round_weights.get(round_name, 1)
        for game in games:
            weighted.append((round_name, game, w))

    total_weight = sum(w for _, _, w in weighted)

    # Distribute 100 points proportionally
    points = []
    running = 0
    for i, (rn, game, w) in enumerate(weighted):
        if i == len(weighted) - 1:
            # Last game gets remainder to ensure sum = 100
            pts = 100 - running
        else:
            pts = max(1, round(100 * w / total_weight))
            running += pts
        points.append(pts)

    # Fix if we overshot
    total = sum(points)
    if total != 100:
        diff = total - 100
        # Adjust the largest values
        sorted_idx = sorted(range(len(points)), key=lambda i: points[i], reverse=True)
        for idx in sorted_idx:
            adj = min(abs(diff), points[idx] - 1)
            if diff > 0:
                points[idx] -= adj
                diff -= adj
            elif diff < 0:
                points[idx] += abs(diff)
                diff = 0
            if diff == 0:
                break

    # Assign back
    result = {}
    i = 0
    for round_name, games in picks.items():
        result[round_name] = []
        for game in games:
            game["confidence"] = points[i]
            result[round_name].append(game)
            i += 1

    return result


def generate_bracket(matchups, ratings, agent_id, strategy="balanced", seed=None):
    """Generate a complete bracket."""
    rng = random.Random(seed)

    picks = {
        "round_of_64": [],
        "round_of_32": [],
        "sweet_16": [],
        "elite_8": [],
        "final_4": [],
        "championship": [],
    }

    round_names = list(picks.keys())

    # Round of 64: 32 games from matchups
    r64_winners = []
    for i, game in enumerate(matchups.get("round_of_64", [])):
        team_a = game["team_a"]
        team_b = game["team_b"]
        winner = simulate_game(team_a, team_b, ratings, strategy, rng)
        picks["round_of_64"].append({"game": i + 1, "winner": winner})
        r64_winners.append(winner)

    # Subsequent rounds: pair up winners
    current_winners = r64_winners
    game_num = 33
    for round_idx in range(1, 6):
        round_name = round_names[round_idx]
        next_winners = []
        for i in range(0, len(current_winners), 2):
            if i + 1 < len(current_winners):
                team_a = current_winners[i]
                team_b = current_winners[i + 1]
                winner = simulate_game(team_a, team_b, ratings, strategy, rng)
                picks[round_name].append({"game": game_num, "winner": winner})
                next_winners.append(winner)
                game_num += 1
        current_winners = next_winners

    # Assign confidence
    picks = assign_confidence(picks, strategy)

    bracket = {
        "agent_id": agent_id,
        "model": f"Torvik T-Rank log5 ({strategy} strategy)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "picks": picks,
    }

    return bracket


def main():
    parser = argparse.ArgumentParser(description="Generate a March Madness bracket")
    parser.add_argument("--agent-id", required=False, default=None, help="Your agent name (alphanumeric, hyphens, underscores)")
    parser.add_argument("--strategy", default="balanced", choices=["chalk", "balanced", "contrarian", "chaos"])
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--matchups", default="matchups.json", help="Path to matchups file")
    parser.add_argument("--output-dir", default="brackets", help="Output directory")
    parser.add_argument("--ratings-only", action="store_true", help="Just print ratings and exit")
    args = parser.parse_args()

    print(f"Fetching Torvik ratings...")
    ratings = fetch_torvik_ratings()
    print(f"Got {len(ratings)} teams")

    if args.ratings_only:
        sorted_teams = sorted(ratings.values(), key=lambda t: t["adj_em"], reverse=True)
        for i, t in enumerate(sorted_teams[:30]):
            print(f"#{i+1:>2} {t['name']:<25} AdjEM={t['adj_em']:>+6.2f}")
        return

    if not args.agent_id:
        print("ERROR: --agent-id is required")
        sys.exit(1)

    matchups = load_matchups(args.matchups)
    bracket = generate_bracket(matchups, ratings, args.agent_id, args.strategy, args.seed)

    # Validate pick count
    total_picks = sum(len(v) for v in bracket["picks"].values())
    total_confidence = sum(g["confidence"] for r in bracket["picks"].values() for g in r)
    print(f"Generated {total_picks} picks, confidence sum = {total_confidence}")

    assert total_picks == 63, f"Expected 63 picks, got {total_picks}"
    assert total_confidence == 100, f"Expected confidence sum 100, got {total_confidence}"

    # Write output
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.agent_id}.json")
    with open(out_path, "w") as f:
        json.dump(bracket, f, indent=2)

    print(f"✅ Bracket written to {out_path}")
    print(f"Strategy: {args.strategy}")
    print(f"Champion: {bracket['picks']['championship'][0]['winner']}")


if __name__ == "__main__":
    main()
