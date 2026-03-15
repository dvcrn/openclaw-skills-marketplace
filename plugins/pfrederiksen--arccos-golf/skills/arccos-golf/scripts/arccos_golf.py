#!/usr/bin/env python3
"""
Arccos Golf Analysis Script

Fetches live data from the Arccos Golf API via the arccos library and
generates performance analysis: strokes gained, club distances, scoring
patterns, putting, pace of play, and recent rounds.

Requires: pip install -e /path/to/arccos-api
Credentials: ~/.arccos_creds.json (run `arccos login` once)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_live_data(
    email: Optional[str] = None,
    password: Optional[str] = None,
    rounds_limit: int = 100,
) -> dict[str, Any]:
    """
    Fetch live Arccos data via the arccos library.

    Args:
        email: Arccos account email (uses cached creds if omitted).
        password: Arccos account password (uses cached creds if omitted).
        rounds_limit: Max rounds to fetch for analysis.

    Returns:
        Normalised data dict compatible with ArccosAnalyzer.
    """
    try:
        from arccos import ArccosClient
        from arccos.exceptions import ArccosError
    except ImportError:
        print(
            "Error: arccos library not installed.\n"
            "Install it: pip install -e /path/to/arccos-api",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        client = ArccosClient(email=email, password=password)
    except Exception as e:
        print(f"Error: could not authenticate — {e}", file=sys.stderr)
        print("Run `arccos login` to cache credentials.", file=sys.stderr)
        sys.exit(1)

    data: dict[str, Any] = {"golfer": client.email, "last_fetched": _today()}

    # Rounds
    rounds = client.rounds.list(limit=rounds_limit)
    data["total_rounds"] = len(rounds)

    # Recent rounds with course names
    recent = []
    course_cache: dict[int, str] = {}
    for r in rounds[:10]:
        cid = r.get("courseId")
        if cid and cid not in course_cache:
            try:
                cd = client.courses.get(cid)
                course_cache[cid] = cd.get("courseName") or cd.get("name") or f"Course {cid}"
            except Exception:
                course_cache[cid] = f"Course {cid}"
        course_name = course_cache.get(cid, f"Course {cid}") if cid else "Unknown"
        score = r.get("noOfShots")
        # We don't know par from the round object alone; skip over_par calculation
        recent.append({
            "date":     r.get("startTime", "")[:10],
            "course":   course_name,
            "score":    score,
            "round_id": r.get("roundId"),
            "holes":    r.get("noOfHoles", 18),
        })
    data["recent_rounds"] = recent

    # Total shots (sum across all rounds)
    data["total_shots"] = sum(r.get("noOfShots") or 0 for r in rounds)

    # Handicap
    try:
        hcp = client.handicap.current()
        data["handicap"] = hcp
    except Exception:
        data["handicap"] = {}

    # Club distances
    try:
        clubs_raw = client.clubs.smart_distances()
        clubs = []
        for c in clubs_raw:
            name  = c.get("clubType") or c.get("name") or "?"
            smart = c.get("smartDistance")
            avg   = c.get("averageDistance")
            shots = c.get("totalShots", 0)
            clubs.append({
                "club":           name,
                "avg_distance":   avg or smart or 0,
                "smart_distance": smart,
                "total_shots":    shots,
            })
        # Sort longest first, exclude putter
        clubs = [c for c in clubs if "putt" not in c["club"].lower()]
        clubs.sort(key=lambda x: x["avg_distance"] or 0, reverse=True)
        data["clubs"] = clubs
    except Exception:
        data["clubs"] = []

    # Strokes gained — aggregate last 10 rounds that have data
    round_ids = [r["round_id"] for r in recent[:10] if r.get("round_id")]
    if round_ids:
        try:
            sg_raw = client.stats.strokes_gained(round_ids)
            data["strokes_gained"] = {
                "overall":    sg_raw.get("overallSga"),
                "driving":    sg_raw.get("drivingSga"),
                "approach":   sg_raw.get("approachSga"),
                "short_game": sg_raw.get("shortSga"),
                "putting":    sg_raw.get("puttingSga"),
                "raw":        sg_raw,
            }
        except Exception:
            data["strokes_gained"] = {}
    else:
        data["strokes_gained"] = {}

    # Pace of play
    try:
        pace = client.rounds.pace_of_play(rounds=rounds)
        data["pace_of_play"] = pace
    except Exception:
        data["pace_of_play"] = {}

    return data


def load_json_data(path: str) -> dict[str, Any]:
    """Load data from a cached JSON file (legacy / offline mode)."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

class ArccosAnalyzer:
    """Analyse normalised Arccos data dict."""

    def __init__(self, data: dict[str, Any]):
        self.data = data

    # Summary

    def summary(self) -> dict[str, Any]:
        hcp = self.data.get("handicap", {})
        hcp_index = None
        if isinstance(hcp, dict):
            hcp_index = hcp.get("handicapIndex") or hcp.get("index") or hcp.get("handicap")
        elif isinstance(hcp, (int, float)):
            hcp_index = hcp

        return {
            "golfer":          self.data.get("golfer", "Unknown"),
            "last_updated":    self.data.get("last_fetched", "Unknown"),
            "total_shots":     self.data.get("total_shots", 0),
            "total_rounds":    self.data.get("total_rounds", 0),
            "handicap_index":  hcp_index,
        }

    # Strokes gained

    def strokes_gained(self) -> dict[str, Any]:
        sg = self.data.get("strokes_gained", {})
        cats = {
            "Driving":    sg.get("driving"),
            "Approach":   sg.get("approach"),
            "Short Game": sg.get("short_game"),
            "Putting":    sg.get("putting"),
        }
        strengths   = []
        weaknesses  = []
        priorities  = []

        for name, val in cats.items():
            if val is None:
                continue
            if val > 0:
                strengths.append((name, val))
            elif val < -1.0:
                weaknesses.append((name, val))

        priorities = sorted(weaknesses, key=lambda x: x[1])  # most negative first

        return {
            "overall":    sg.get("overall"),
            "categories": cats,
            "strengths":  strengths,
            "weaknesses": weaknesses,
            "priorities": [n for n, _ in priorities],
        }

    # Clubs

    def clubs(self, club_filter: Optional[str] = None) -> list[dict]:
        clubs = self.data.get("clubs", [])
        if club_filter:
            clubs = [c for c in clubs if club_filter.lower() in c.get("club", "").lower()]
        return clubs

    # Pace of play

    def pace(self) -> dict[str, Any]:
        return self.data.get("pace_of_play", {})

    # Recent rounds

    def recent_rounds(self, limit: int = 5) -> list[dict]:
        return self.data.get("recent_rounds", [])[:limit]

    # Report

    def report(self, fmt: str = "text") -> str | dict:
        if fmt == "json":
            return {
                "summary":        self.summary(),
                "strokes_gained": self.strokes_gained(),
                "clubs":          self.clubs(),
                "pace_of_play":   self.pace(),
                "recent_rounds":  self.recent_rounds(),
            }

        lines = []
        s = self.summary()
        lines += [
            "🏌️  Arccos Golf Performance Report",
            "=" * 42,
            f"Golfer:        {s['golfer']}",
            f"Last updated:  {s['last_updated']}",
            f"Total rounds:  {s['total_rounds']}",
            f"Total shots:   {s['total_shots']:,}",
        ]
        if s["handicap_index"] is not None:
            lines.append(f"Handicap:      {s['handicap_index']}")

        # Strokes gained
        sg = self.strokes_gained()
        lines += ["", "📊 STROKES GAINED (last 10 rounds)", "-" * 34]
        if sg["overall"] is not None:
            lines.append(f"Overall:    {sg['overall']:+.2f}")
        for name, val in sg["categories"].items():
            if val is not None:
                lines.append(f"{name:<12} {val:+.2f}")
        if sg["priorities"]:
            lines.append("\n🎯 Priority areas:")
            for i, p in enumerate(sg["priorities"], 1):
                lines.append(f"  {i}. {p}")

        # Clubs
        clubs = self.clubs()
        if clubs:
            lines += ["", "🏌️  CLUB DISTANCES", "-" * 20]
            for c in clubs[:14]:
                name  = c.get("club", "?")
                avg   = c.get("avg_distance") or 0
                smart = c.get("smart_distance")
                shots = c.get("total_shots", "?")
                dist_str = f"{avg}y avg"
                if smart and smart != avg:
                    dist_str += f"  (smart: {smart}y)"
                lines.append(f"  {name:<20} {dist_str}  ({shots} shots)")

        # Pace of play
        pace = self.pace()
        if pace.get("overall_avg_display"):
            lines += ["", "⏱️  PACE OF PLAY", "-" * 20]
            lines.append(f"Overall avg:  {pace['overall_avg_display']}")
            for c in (pace.get("course_averages") or [])[:5]:
                flag = "🔴" if c["avg_minutes"] > 300 else "🟡" if c["avg_minutes"] > 270 else "🟢"
                lines.append(f"  {flag} {c['avg_display']}  {c['course']}  ({c['rounds']}x)")

        # Recent rounds
        recent = self.recent_rounds()
        if recent:
            lines += ["", "📅 RECENT ROUNDS", "-" * 20]
            for r in recent:
                score = r.get("score", "?")
                lines.append(f"  {r['date']}  {score}  {r['course']}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arccos Golf performance analysis via live API or cached JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Live data (default — uses cached credentials)
  python3 arccos_golf.py

  # Live data with explicit credentials
  python3 arccos_golf.py --email you@example.com --password secret

  # Analyse a cached JSON file (offline)
  python3 arccos_golf.py --file /path/to/arccos-data.json

  # JSON output
  python3 arccos_golf.py --format json

  # Strokes gained only
  python3 arccos_golf.py --strokes-gained

  # Club distances, irons only
  python3 arccos_golf.py --clubs iron
""",
    )
    parser.add_argument("--file",          type=str,    help="Path to cached JSON data file (skips live fetch)")
    parser.add_argument("--email",         type=str,    help="Arccos account email (uses cached creds if omitted)")
    parser.add_argument("--password",      type=str,    help="Arccos account password")
    parser.add_argument("--rounds-limit",  type=int,    default=100, help="Max rounds to fetch (default: 100)")
    parser.add_argument("--format",        choices=["text", "json"], default="text")
    parser.add_argument("--summary",       action="store_true", help="Summary stats only")
    parser.add_argument("--strokes-gained",action="store_true", help="Strokes gained only")
    parser.add_argument("--clubs",         type=str,    help="Club distances (optionally filter: iron, wedge, wood)")
    parser.add_argument("--pace",          action="store_true", help="Pace of play only")
    parser.add_argument("--recent-rounds", type=int,    default=5, help="Number of recent rounds (default: 5)")

    args = parser.parse_args()

    # Load data
    if args.file:
        data = load_json_data(args.file)
    else:
        data = fetch_live_data(
            email=args.email,
            password=args.password,
            rounds_limit=args.rounds_limit,
        )

    analyzer = ArccosAnalyzer(data)

    try:
        if args.summary:
            out = analyzer.summary()
            if args.format == "json":
                print(json.dumps(out, indent=2))
            else:
                s = out
                print(f"Golfer: {s['golfer']}")
                print(f"Shots:  {s['total_shots']:,}  |  Rounds: {s['total_rounds']}")
                if s["handicap_index"] is not None:
                    print(f"Handicap: {s['handicap_index']}")

        elif args.strokes_gained:
            out = analyzer.strokes_gained()
            if args.format == "json":
                print(json.dumps(out, indent=2))
            else:
                if out["overall"] is not None:
                    print(f"Overall: {out['overall']:+.2f}")
                for name, val in out["categories"].items():
                    if val is not None:
                        print(f"{name}: {val:+.2f}")

        elif args.clubs is not None:
            clubs = analyzer.clubs(args.clubs or None)
            if args.format == "json":
                print(json.dumps(clubs, indent=2))
            else:
                for c in clubs:
                    name  = c.get("club", "?")
                    avg   = c.get("avg_distance", 0)
                    shots = c.get("total_shots", "?")
                    print(f"{name:<20} {avg}y  ({shots} shots)")

        elif args.pace:
            pace = analyzer.pace()
            if args.format == "json":
                print(json.dumps(pace, indent=2))
            else:
                if pace.get("overall_avg_display"):
                    print(f"Overall avg: {pace['overall_avg_display']}")
                    for c in (pace.get("course_averages") or []):
                        flag = "🔴" if c["avg_minutes"] > 300 else "🟡" if c["avg_minutes"] > 270 else "🟢"
                        print(f"  {flag} {c['avg_display']}  {c['course']}  ({c['rounds']}x)")
                else:
                    print("No pace data available.")

        else:
            report = analyzer.report(args.format)
            if args.format == "json":
                print(json.dumps(report, indent=2))
            else:
                print(report)

    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
