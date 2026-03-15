---
name: clawtourism
description: "From confirmation email to curated itinerary — automatically. Scans Gmail travel bookings, builds structured trip files, and delivers proactive intelligence: flight alerts, pre-trip checklists, day plans, visa checks, transfer suggestions, and restaurant release-day alerts. Supports family and group trips."
homepage: https://github.com/yhyatt/ClawTourism
---

# ClawTourism

Travel intelligence skill for OpenClaw agents.

## Setup

1. Label your travel confirmation emails in Gmail with `Trips`
2. Set `GOG_KEYRING_PASSWORD` in your environment
3. (Optional) Set `AERODATABOX_API_KEY` for live flight monitoring
4. Run: `python -m clawtourism scan`

## Usage

Ask your agent:
- *"Scan my travel emails and update my trips"*
- *"What's missing from my NYC trip?"*
- *"Set up flight monitoring for my upcoming flights"*
- *"Generate a packing list for the cruise"*
- *"What's the plan for Day 3 in Barcelona?"*
- *"Do I need a visa for my next trip?"*

## Output

Trip files written to `memory/trips/{slug}.json` and `memory/trips/{slug}.md`.
Cron jobs registered for: D-14/7/3/1 checklists, flight monitoring, restaurant release-day alerts.
