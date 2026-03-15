# Placed Resume Builder — API Reference

Full reference for all resume builder tools available via the Placed MCP server.

## Authentication

All tools require `PLACED_API_KEY` set in the MCP server environment. Get your key at https://placed.exidian.tech/settings.

---

## create_resume

Create a new resume.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Resume name (e.g., "Senior Engineer Resume") |
| `target_role` | string | no | Target job title for AI optimization hints |
| `use_profile` | boolean | no | Pre-fill from your Placed profile (default: false) |
| `template_id` | string | no | Template to apply on creation |

**Returns:** `{ resume_id, title, created_at, sections_populated }`

**Example:**
```json
{
  "title": "Staff Engineer Resume",
  "target_role": "Staff Software Engineer",
  "use_profile": true,
  "template_id": "modern-clean"
}
```

---

## get_resume

Retrieve a resume with all sections.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID from `list_resumes` or `create_resume` |

**Returns:** Full resume object with all populated sections.

---

## update_resume

Update one or more sections of a resume.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `section` | string | yes | Section name (see list below) |
| `data` | object/array | yes | Section data matching the schema |

**Sections and their data shapes:**

### basics
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0100",
  "headline": "Senior Software Engineer",
  "location": "San Francisco, CA",
  "website": "https://janesmith.dev"
}
```

### summary
```json
{
  "text": "Senior Software Engineer with 7+ years building scalable distributed systems..."
}
```

### experience
```json
[{
  "company": "Acme Corp",
  "title": "Senior Software Engineer",
  "location": "San Francisco, CA",
  "startDate": "2020-01",
  "endDate": "present",
  "bullets": [
    "Led migration of monolith to microservices, reducing deploy time by 60%",
    "Mentored 4 junior engineers, 2 promoted within 12 months"
  ]
}]
```

### education
```json
[{
  "institution": "Stanford University",
  "degree": "B.S. Computer Science",
  "graduationDate": "2017-05",
  "gpa": "3.8",
  "honors": "Magna Cum Laude"
}]
```

### skills
```json
{
  "categories": [
    { "name": "Languages", "skills": ["Python", "Go", "Java", "SQL"] },
    { "name": "Frameworks", "skills": ["Django", "FastAPI", "Spring Boot"] },
    { "name": "Cloud", "skills": ["AWS", "GCP", "Kubernetes"] }
  ]
}
```

### certifications
```json
[{
  "name": "AWS Solutions Architect",
  "issuer": "Amazon Web Services",
  "date": "2023-06",
  "url": "https://aws.amazon.com/certification/"
}]
```

### projects
```json
[{
  "name": "OpenSearch Plugin",
  "description": "Elasticsearch plugin for semantic search with 500+ GitHub stars",
  "url": "https://github.com/janesmith/opensearch-plugin",
  "technologies": ["Python", "Elasticsearch", "Docker"]
}]
```

---

## list_resumes

List all resumes for the authenticated user.

**Parameters:** None

**Returns:** Array of `{ resume_id, title, template_id, updated_at, sections_count }`

---

## get_resume_schema

Get the full JSON schema for all resume sections.

**Parameters:** None

**Returns:** JSON Schema object describing all fields, types, and constraints.

---

## list_resume_templates

Browse all available resume templates.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | no | Filter by category: modern, professional, creative, minimal, academic |

**Returns:** Array of `{ template_id, name, category, ats_friendly, preview_url }`

---

## get_template_preview

Get details and preview for a specific template.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_id` | string | yes | Template ID from `list_resume_templates` |

**Returns:** `{ template_id, name, description, preview_url, ats_score, best_for }`

---

## change_resume_template

Apply a template to a resume. Non-destructive — content is preserved.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `template_id` | string | yes | Template ID to apply |

**Returns:** `{ resume_id, template_id, updated_at }`

---

## get_resume_pdf_url

Generate a PDF download URL. URL expires in 15 minutes.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |

**Returns:** `{ url, expires_at }`

---

## get_resume_docx_url

Generate a DOCX (Word) download URL.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |

**Returns:** `{ url, expires_at }`

---

## export_resume_json

Export resume as structured JSON.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |

**Returns:** Full resume JSON object (same schema as `get_resume`).

---

## export_resume_markdown

Export resume as formatted Markdown text.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |

**Returns:** `{ markdown }` — Formatted Markdown string.

---

## Error Codes

| Code | Meaning |
|------|---------|
| `RESUME_NOT_FOUND` | Resume ID doesn't exist or belongs to another user |
| `TEMPLATE_NOT_FOUND` | Template ID is invalid |
| `INVALID_SECTION` | Section name is not recognized |
| `SCHEMA_VALIDATION_ERROR` | Section data doesn't match expected schema |
| `EXPORT_FAILED` | PDF/DOCX generation failed — retry |
| `RATE_LIMIT_EXCEEDED` | Too many requests — wait and retry |

---

## Rate Limits

| Tier | Requests/min | Exports/day |
|------|-------------|-------------|
| Free | 10 | 5 |
| Pro | 60 | 50 |
| Premium | 300 | unlimited |
