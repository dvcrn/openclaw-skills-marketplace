# Aerobase API Reference

Base URL: `https://aerobase.app/api`

## Authentication

All API requests require `AEROBASE_API_KEY` header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Flights
- `POST /api/v1/flights/score` - Score a flight for jetlag
- `POST /api/v1/flights/search` - Search flights with scoring
- `POST /api/v1/flights/compare` - Compare multiple flights

### Awards
- `POST /api/v1/awards/search` - Search award availability across 24+ programs
- `GET /api/transfer-bonuses` - Current transfer partner bonuses

### Lounges
- `GET /api/v1/lounges` - Search airport lounges
- `GET /api/airports/{code}/lounges` - Lounges at specific airport

### Hotels
- `GET /api/v1/hotels` - Search hotels
- `GET /api/dayuse?airport={code}` - Day-use hotels for layovers
- `GET /api/hotels/near-airport/{code}` - Airport-adjacent hotels

### Activities
- `GET /api/v1/tours` - Viator tours and activities

### Deals
- `GET /api/v1/deals` - Flight deals with filters

### Wallet
- `GET /api/v1/credit-cards` - Credit card transfer partners
- `GET /api/v1/loyalty/balances` - Gmail-scanned loyalty balances (Premium)

### Recovery
- `POST /api/v1/recovery/plan` - Generate jetlag recovery plan (Premium)

### Boarding Passes
- `POST /api/v1/boarding-passes` - Store boarding pass
- `GET /api/v1/boarding-passes?upcoming=true` - List upcoming passes

## Rate Limits

- Free tier: 5 API calls/day
- Premium: Unlimited

## Errors

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Daily limit exceeded"
  }
}
```

## Full OpenAPI Spec

See: https://aerobase.app/api/v1/openapi
