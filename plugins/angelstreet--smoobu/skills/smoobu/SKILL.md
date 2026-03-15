---
name: smoobu
description: "Interact with Smoobu property management API. Use for checking bookings, availability, managing reservations, and listing apartments/properties. Triggers on rental property management, Airbnb sync, vacation rental bookings, guest management."
---

# Smoobu Property Management

Smoobu is a channel manager for vacation rentals (Airbnb, Booking.com, etc).

## Setup

Requires `SMOOBU_API_KEY` in `~/.openclaw/.env`:
```
SMOOBU_API_KEY=your_api_key_here
```

Find your API key in Smoobu: Settings → Developers

## Quick Reference

### API Base
`https://login.smoobu.com`

### Authentication
Header: `Api-Key: {SMOOBU_API_KEY}`

### Rate Limit
1000 requests/minute

## Common Operations

### List Properties
```bash
curl -s "https://login.smoobu.com/api/apartments" \
  -H "Api-Key: $SMOOBU_API_KEY" | jq
```

### Get Bookings
```bash
# All bookings
curl -s "https://login.smoobu.com/api/reservations" \
  -H "Api-Key: $SMOOBU_API_KEY" | jq

# Filter by dates
curl -s "https://login.smoobu.com/api/reservations?from=2026-02-01&to=2026-02-28" \
  -H "Api-Key: $SMOOBU_API_KEY" | jq

# Filter by apartment
curl -s "https://login.smoobu.com/api/reservations?apartmentId=123" \
  -H "Api-Key: $SMOOBU_API_KEY" | jq
```

### Check Availability
```bash
curl -s -X POST "https://login.smoobu.com/booking/checkApartmentAvailability" \
  -H "Api-Key: $SMOOBU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arrivalDate": "2026-03-01",
    "departureDate": "2026-03-05",
    "apartments": [123, 456]
  }' | jq
```

### Create Booking
```bash
curl -s -X POST "https://login.smoobu.com/api/reservations" \
  -H "Api-Key: $SMOOBU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arrivalDate": "2026-03-01",
    "departureDate": "2026-03-05",
    "apartmentId": 123,
    "channelId": 70,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "adults": 2
  }' | jq
```

### Update Booking
```bash
curl -s -X PUT "https://login.smoobu.com/api/reservations/{id}" \
  -H "Api-Key: $SMOOBU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arrivalTime": "15:00",
    "departureTime": "11:00",
    "notice": "Late checkout requested"
  }' | jq
```

### Get User Profile
```bash
curl -s "https://login.smoobu.com/api/me" \
  -H "Api-Key: $SMOOBU_API_KEY" | jq
```

## Helper Script

Use `scripts/smoobu.py` for common operations:

```bash
# List apartments
python3 scripts/smoobu.py apartments

# List bookings (optional date range)
python3 scripts/smoobu.py bookings
python3 scripts/smoobu.py bookings --from 2026-02-01 --to 2026-02-28

# Check availability
python3 scripts/smoobu.py availability --arrival 2026-03-01 --departure 2026-03-05

# Get user info
python3 scripts/smoobu.py me
```

## API Response Examples

### Booking Object
```json
{
  "id": 291,
  "type": "reservation",
  "arrival": "2026-02-10",
  "departure": "2026-02-12",
  "apartment": {"id": 123, "name": "Beach House"},
  "channel": {"id": 465614, "name": "Booking.com"},
  "guest-name": "John Doe",
  "price": 250.00,
  "adults": 2,
  "children": 0
}
```

### Apartment Object
```json
{
  "id": 123,
  "name": "Beach House",
  "location": {"city": "Nice", "country": "France"}
}
```

## Error Handling

| Status | Meaning |
|--------|---------|
| 401 | Invalid API key |
| 400 | Validation error (check response body) |
| 429 | Rate limit exceeded |

## Docs

Full API: https://docs.smoobu.com
