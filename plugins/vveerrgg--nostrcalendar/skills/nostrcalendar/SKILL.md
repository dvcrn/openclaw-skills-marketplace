---
name: nostrcalendar
description: "Nostr-native scheduling — manage availability, book meetings, negotiate times over relay"
---

# NostrCalendar — Sovereign Scheduling for AI Agents

Give your AI agent the ability to manage calendars, publish availability, accept bookings, and negotiate meeting times — all over Nostr relays with no centralized server.

## Install

```bash
pip install nostrcalendar
```

## Core Capabilities

### 1. Publish Availability

Set your human's available hours. Stored as a replaceable Nostr event on their relay.

```python
from nostrcal import AvailabilityRule, DayOfWeek, TimeSlot, publish_availability
from nostrkey import Identity

identity = Identity.from_nsec("nsec1...")
rule = AvailabilityRule(
    slots={
        DayOfWeek.MONDAY: [TimeSlot("09:00", "12:00"), TimeSlot("14:00", "17:00")],
        DayOfWeek.WEDNESDAY: [TimeSlot("10:00", "16:00")],
        DayOfWeek.FRIDAY: [TimeSlot("09:00", "12:00")],
    },
    slot_duration_minutes=30,
    buffer_minutes=15,
    max_per_day=6,
    timezone="America/Vancouver",
    title="Book a call with Vergel",
)

event_id = await publish_availability(identity, rule, "wss://relay.nostrkeep.com")
```

### 2. Check Free Slots

Query available time slots for any user on any date.

```python
from nostrcal import get_free_slots
from datetime import datetime

slots = await get_free_slots(
    pubkey_hex="abc123...",
    relay_url="wss://relay.nostrkeep.com",
    date=datetime(2026, 3, 15),
)
for slot in slots:
    print(f"{slot.start} - {slot.end}")
```

### 3. Create a Booking

Send a booking request as an encrypted DM to the calendar owner.

```python
from nostrcal import create_booking

event_id = await create_booking(
    identity=agent_identity,
    calendar_owner_pubkey="abc123...",
    start=1742054400,
    end=1742056200,
    title="Product sync",
    message="Let's review the Q1 roadmap",
    relay_url="wss://relay.nostrkeep.com",
)
```

### 4. Accept or Decline Bookings

```python
from nostrcal import accept_booking, decline_booking

# Accept — publishes a calendar event + sends confirmation DM
cal_id, dm_id = await accept_booking(identity, request, relay_url)

# Decline — sends a decline DM with reason
dm_id = await decline_booking(identity, request, "Conflict with another meeting", relay_url)
```

### 5. Agent-to-Agent Negotiation

Two AI agents find mutual availability and agree on a time — no humans needed.

```python
from nostrcal import find_mutual_availability, propose_times
from datetime import datetime, timedelta

# Find overlapping free slots
dates = [datetime(2026, 3, d) for d in range(15, 20)]
mutual = await find_mutual_availability(my_agent, other_pubkey, relay_url, dates)

# Or send a proposal with available times
await propose_times(my_agent, other_pubkey, relay_url, dates, title="Collab sync")
```

## When to Use Each Module

| Task | Module | Function |
|------|--------|----------|
| Set available hours | `availability` | `publish_availability` |
| Check someone's openings | `availability` | `get_free_slots` |
| Request a meeting | `booking` | `create_booking` |
| Confirm a meeting | `booking` | `accept_booking` |
| Decline a meeting | `booking` | `decline_booking` |
| Cancel a meeting | `booking` | `cancel_event` |
| RSVP to an event | `booking` | `send_rsvp` |
| Find mutual free time | `negotiate` | `find_mutual_availability` |
| Propose times to another agent | `negotiate` | `propose_times` |
| Respond to a proposal | `negotiate` | `respond_to_proposal` |

## Nostr NIPs Used

| NIP | Purpose |
|-----|---------|
| NIP-01 | Basic event structure and relay protocol |
| NIP-04 | Encrypted direct messages (booking requests) |
| NIP-09 | Event deletion (cancellations) |
| NIP-52 | Calendar events (kind 31923) and RSVPs (kind 31925) |
| NIP-78 | App-specific data (kind 30078 for availability rules) |

## Important Notes

- All times are UTC unless a timezone is specified in the AvailabilityRule
- Booking requests are encrypted — only the calendar owner can read them
- Calendar events are public — anyone on the relay can see your schedule
- The agent needs its own Nostr keypair (mutual recognition principle)
- Depends on `nostrkey` for all cryptographic operations
