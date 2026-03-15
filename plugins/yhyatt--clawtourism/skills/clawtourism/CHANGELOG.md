# Changelog

## [0.1.0] - 2026-03-03

### Added
- Email scanner (Gmail label:Trips, forwarded email traversal, RTL Hebrew)
- PDF ticket/voucher parser
- Trip assembler — flights, hotels, restaurants, cruises → unified Trip model
- Gap detector — missing return flights, accommodation, documents, kids considerations
- Markdown + JSON trip renderer
- Pre-trip checklists: D-14, D-7, D-3, D-1 cron specs
- Flight monitor: D-1 alert + day-of polling via AeroDataBox
- Restaurant release-day alerts (Resy 28-day, OpenTable 30-day)
- Known senders: El Al, Wizz Air, Blue Bird, Amsalem, MSC, Booking.com, Airbnb, Club Med

### Coming in 0.2.0
- Weather integration (Open-Meteo) in D-3/D-1 alerts
- Packing list generator (weather + kids + trip-type aware)
- Day planner (morning/afternoon/evening for every trip day)
- Transfer suggestions (airport/pier → hotel)
- Visa check (Israeli passport requirements by destination)
