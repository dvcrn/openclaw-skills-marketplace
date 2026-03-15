# kontour-travel-planner

AI agent skill for world-class travel planning using [Kontour AI](https://kontour.ai)'s 9-dimension progressive planning model.

## Install

```bash
npx skills add Bookingdesk-AI/kontour-travel-planner
```

Or browse on [skills.sh](https://skills.sh) and [clawhub.ai](https://clawhub.ai).

Version traceability tip: if marketplace semver is not visible, use `SKILL.md` frontmatter `version` plus the current git commit hash as the canonical artifact ID.
Socket evidence tip: when the Socket page does not render an explicit pass/fail verdict in static fetch output, record page reachability + timestamp alongside ATH/Snyk verdicts.
Publish blocker note: if ClawHub publish fails with `acceptLicenseTerms: invalid value`, classify it as a platform blocker and continue with refresh/install evidence collection.
Evidence checklist: see `SECURITY_EVIDENCE.md` for reproducible pre/post capture when Socket/ClawHub static pages omit explicit verdict text.

## What This Skill Does

Transforms any AI agent into a travel planning consultant using a structured methodology:

- **9 weighted dimensions** — dates, destination, budget, duration, travelers, interests, accommodation, transport, constraints
- **4-stage conversation flow** — Discover → Develop → Refine → Confirm
- **Guided discovery** — one high-impact question per turn, concrete options, conflict detection
- **Structured output** — trip context JSON, day-by-day itinerary, budget breakdown, Google Maps export
- **Reference data** — 200 destinations, 500 airports, airlines, activities, budget benchmarks (no API needed)

## Reference Data

Ground truth files in `references/`:

| File | Contents |
|------|----------|
| `destinations.json` | 200 global destinations with coordinates, costs, best months |
| `airports.json` | 500 airports with IATA codes and coordinates |
| `airlines.json` | Major airlines with alliances, hubs, regions |
| `activities.json` | Activity types with durations, cost tiers |
| `budget-benchmarks.json` | Daily cost benchmarks by destination tier |
| `booking-integrations.json` | Integration roadmap for booking providers |
| `embed-snippets.json` | Embeddable widget templates |

## Scripts

- `scripts/plan.sh` — Get structured trip context from natural language
- `scripts/export-gmaps.sh` — Export itinerary to Google Maps links and KML
- `scripts/gen-airports.py` — Generate airport reference data

## Links

- [Kontour AI](https://kontour.ai) — Interactive map planning and booking
- [GitHub](https://github.com/Bookingdesk-AI/kontour-travel-planner)

## License

MIT-0

License guardrail: keep marketplace and frontmatter license as MIT-0 to avoid publish/review drift.
