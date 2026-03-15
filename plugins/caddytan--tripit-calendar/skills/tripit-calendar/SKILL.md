---
name: tripit_calendar
description: "Read upcoming TripIt travel plans from a TripIt iCal feed."
---

# TripIt Calendar

Use this skill when the user asks about:
- next trip
- upcoming trips
- travel itinerary
- TripIt plans
- flights or hotels coming up
- travel this month

## What it needs

This skill requires:
- Python
- environment variable `TRIPIT_ICAL_URL`
- Python packages `requests` and `icalendar`

## Setup

Install the Python packages in the OpenClaw virtual environment:

```bash
source ~/.openclaw/workspace/openclaw_venv/bin/activate
pip install requests icalendar
