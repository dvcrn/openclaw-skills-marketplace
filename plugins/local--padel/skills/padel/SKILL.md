---
name: padel
description: "Check padel court availability and manage bookings via the padel CLI."
---

# Padel Booking Skill

## CLI

```bash
padel  # On PATH (moltbot plugin bundle)
```

## Venues

Use the configured venue list in order of preference. If no venues are configured, ask for a venue name or location.

## Commands

### Check next booking
```bash
padel bookings list 2>&1 | head -3
```

### Search availability
```bash
padel search --venues VENUE1,VENUE2 --date YYYY-MM-DD --time 09:00-12:00
```

## Response guidelines

- Keep responses concise.
- Use 🎾 emoji.
- End with a call to action.

## Authorization

Only the authorized booker can confirm bookings. If the requester is not authorized, ask the authorized user to confirm.
