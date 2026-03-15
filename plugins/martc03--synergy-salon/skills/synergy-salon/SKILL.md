---
name: synergy-salon
description: "Manage Synergy salon — appointments, clients, social media, promotions, and website. Notion-powered scheduling and CRM."
homepage: https://github.com/martc03/openclaw-ultimate
---

# Synergy Salon — Operations

Manage Synergy salon from your phone. Book appointments, manage clients, create social media content, and update the website.

## Commands

### `salon schedule [day]`
Show appointments for a specific day. Defaults to today.

```
salon schedule today
salon schedule tomorrow
salon schedule friday
salon schedule march 15
```

Reads from: Notion "Salon Appointments" database, filtered by date.

### `salon book [client] [service] [time]`
Book a new appointment. Creates entry in Notion with Status="Confirmed".

```
salon book Sarah Jones haircut 2pm Thursday
salon book Mike Chen color 10am March 15
```

If the client doesn't exist in Salon Clients, creates a new client entry and asks for phone/email.

Services: Haircut, Color, Style, Blowout, Nails, Facial, Wax

### `salon reschedule [client] [new-time]`
Reschedule an existing appointment. Updates the Notion entry.

```
salon reschedule Sarah Jones 4pm Friday
```

Finds the client's next upcoming appointment and updates it.

### `salon cancel [client]`
Cancel an appointment. Sets Status="Cancelled" in Notion.

```
salon cancel Sarah Jones
```

### `salon remind`
List clients with appointments today or tomorrow who haven't been reminded.

```
salon remind
```

Shows client names, services, times, and phone numbers. Marks "ReminderSent" checkbox after confirming reminders were sent.

### `salon promo [type]`
Generate a social media promotional post. Saves draft to Notion "Salon Promos" database.

```
salon promo valentines special
salon promo new client discount 20% off first visit
salon promo summer hair trends
salon promo holiday gift cards
```

Generates platform-appropriate content with relevant hashtags.

### `salon post [content]`
Create and schedule a social media post. Saves to Notion "Salon Promos" database.

```
salon post Instagram: Summer vibes start with the perfect cut! Book today.
salon post Facebook: New balayage service now available - starting at $150
```

### `salon site update [page] [content]`
Update the Synergy salon website content.

```
salon site update services Add balayage starting at $150
salon site update hours Update Saturday hours to 9am-5pm
salon site update gallery Add new portfolio images
```

Modifies files in `~/synergy-website/`, commits, and offers to deploy.

### `salon site deploy`
Deploy the website. **Requires approval.** Delegates to `site-deployer` skill.

```
salon site deploy
```

### `salon clients [search]`
Search client database in Notion.

```
salon clients Sarah
salon clients all
salon clients recent
```

Returns: Name, phone, email, preferences, last visit, total visits.

### `salon revenue [period]`
Financial summary for the salon.

```
salon revenue this week
salon revenue march
salon revenue this year
```

Reads from: Notion "Financial Tracking" database filtered to Synergy source.

## Notion Databases

- **Salon Appointments** — Booking management with service types and status
- **Salon Clients** — Client CRM with contact info and preferences
- **Salon Promos** — Social media content calendar
- **Financial Tracking** — Revenue tracking (filtered to Synergy source)
