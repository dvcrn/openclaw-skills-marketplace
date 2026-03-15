---
name: space-jobs
description: "Search space industry jobs on Zero G Talent (zerogtalent.com). Use when user asks about aerospace/space jobs, career opportunities at companies like SpaceX, NASA, Blue Origin, Rocket Lab, Boeing, or any space industry hiring questions. Triggers on 'space jobs', 'aerospace careers', 'who is hiring', 'find jobs at [company]', 'remote space jobs', 'internships in aerospace', or any job search query related to the space industry."
---

# Zero G Talent Job Search

Search 5,000+ space industry jobs from 50+ aerospace companies.

## API

```
GET https://zerogtalent.com/api/jobs/search
```

No authentication required.

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Keyword search (full-text + fuzzy) |
| `company` | string | Company slug (e.g., `spacex`, `blue-origin`) |
| `location` | string | Location slug (e.g., `california`, `remote`, `texas`) |
| `employmentType` | string | `full-time`, `internship`, `part-time`, `contract` |
| `remote` | `true`/`false` | Remote jobs filter |
| `limit` | number | Results per page (1-50, default 20) |
| `offset` | number | Pagination offset (default 0) |

**Examples:**

```bash
# Software engineering jobs
curl "https://zerogtalent.com/api/jobs/search?q=software+engineer&limit=5"

# SpaceX jobs
curl "https://zerogtalent.com/api/jobs/search?company=spacex&limit=10"

# Remote internships
curl "https://zerogtalent.com/api/jobs/search?employmentType=internship&remote=true&limit=5"

# Combine: Python jobs at NASA
curl "https://zerogtalent.com/api/jobs/search?q=python&company=nasa&limit=5"
```

**Response shape:**

```json
{
  "jobs": [{
    "title": "Software Engineer, Starlink",
    "slug": "software-engineer-starlink",
    "location": "Redmond, WA",
    "remote": false,
    "employmentType": "Full-time",
    "category": "Software Engineering",
    "isActive": true,
    "salaryMin": 120000,
    "salaryMax": 180000,
    "salaryCurrency": "USD",
    "salaryInterval": "YEAR",
    "company": { "name": "SpaceX", "slug": "spacex", "logoUrl": "..." }
  }],
  "total": 342,
  "hasMore": true,
  "pagination": { "offset": 0, "limit": 5, "total": 342 }
}
```

## Company Slugs

`spacex`, `nasa`, `blue-origin`, `rocket-lab`, `boeing`, `northrop-grumman`, `lockheed-martin`, `relativity-space`, `united-launch-alliance`, `l3harris`, `astranis`, `planet`, `ball-aerospace`, `bae-systems`, `rtx`, `leidos`

## Formatting Results

Link to job details: `https://zerogtalent.com/space-jobs/{company-slug}/{job-slug}`

Present each result as:

**{Title}** at {Company}
{Location} | {Salary if available}
[Apply](https://zerogtalent.com/space-jobs/{company-slug}/{job-slug})
