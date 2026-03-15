# Placed Career Tools — API Reference

Full reference for all career tools available via the Placed MCP server.

## Authentication

All tools require `PLACED_API_KEY` set in the MCP server environment.

---

## add_job_application

Add a new job application to your tracker.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company` | string | yes | Company name |
| `role` | string | yes | Job title |
| `job_url` | string | no | URL to the job posting |
| `status` | string | no | Initial status (default: `applied`) |
| `resume_id` | string | no | Resume used for this application |
| `notes` | string | no | Personal notes |
| `applied_date` | string | no | ISO date (default: today) |
| `salary_expectation` | integer | no | Your target salary |

**Returns:** `{ application_id, company, role, status, created_at }`

---

## list_job_applications

View your application pipeline.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | no | Filter by status |
| `company` | string | no | Filter by company name |
| `limit` | integer | no | Max results (default: 50) |
| `sort` | string | no | `applied_date`, `updated_at`, `company` |

**Returns:** Array of application objects with full details.

---

## update_job_status

Move an application to a new stage.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `application_id` | string | yes | Application ID |
| `status` | string | yes | New status |
| `notes` | string | no | Notes about the status change |
| `next_step` | string | no | What happens next |
| `next_step_date` | string | no | Date of next step |

**Returns:** Updated application object.

---

## get_application_analytics

Get pipeline analytics and conversion rates.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date_range` | string | no | `7d`, `30d`, `90d`, `all` (default: `30d`) |

**Returns:**
```json
{
  "total_applications": 24,
  "by_status": { "applied": 10, "phone_screen": 6, "technical": 4, "offer": 2 },
  "conversion_rates": {
    "applied_to_phone_screen": 0.42,
    "phone_screen_to_technical": 0.67,
    "technical_to_offer": 0.50
  },
  "avg_days_to_response": 8,
  "top_companies": ["Google", "Stripe", "Airbnb"]
}
```

---

## match_job

Score how well your resume matches a job description.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `job_description` | string | yes | Full job description text |
| `job_title` | string | no | Job title for context |
| `company` | string | no | Company name for context |

**Returns:**
```json
{
  "match_score": 78,
  "matched_keywords": ["distributed systems", "Go", "Kubernetes", "microservices"],
  "missing_keywords": ["Kafka", "gRPC", "service mesh"],
  "matched_requirements": ["5+ years experience", "system design", "team leadership"],
  "missing_requirements": ["ML experience", "Rust"],
  "recommendation": "Strong match. Add Kafka and gRPC to skills section."
}
```

---

## analyze_resume_gaps

Find missing keywords and skills for a target role.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `job_description` | string | yes | Job description text |
| `include_suggestions` | boolean | no | Include how to address gaps (default: true) |

**Returns:** `{ critical_gaps, nice_to_have_gaps, keyword_gaps, suggestions }`

---

## generate_cover_letter

Generate a tailored cover letter.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `company` | string | yes | Company name |
| `role` | string | yes | Job title |
| `job_description` | string | yes | Job description text |
| `tone` | string | no | `professional`, `conversational`, `enthusiastic` (default: `professional`) |
| `length` | string | no | `short` (200w), `medium` (350w), `long` (500w) (default: `medium`) |
| `highlight_achievements` | array | no | Specific achievements to emphasize |

**Returns:** `{ cover_letter, word_count, key_points_addressed }`

---

## optimize_resume_for_job

Tailor resume content to a specific job description.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `job_description` | string | yes | Job description text |
| `apply_changes` | boolean | no | Auto-apply changes to resume (default: false) |

**Returns:** `{ suggested_changes, keyword_additions, reordered_bullets, new_summary }`

If `apply_changes=true`, creates a new tailored resume copy.

---

## generate_interview_questions

Get likely interview questions for a company and role.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company` | string | yes | Company name |
| `role` | string | yes | Job title |
| `interview_type` | string | no | `technical`, `behavioral`, `system_design`, `all` (default: `all`) |
| `count` | integer | no | Number of questions (default: 15) |

**Returns:** Array of `{ question, type, difficulty, what_they_look_for, tips }`

---

## generate_linkedin_profile

Generate an AI-optimized LinkedIn headline and About section.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_id` | string | yes | Resume ID |
| `target_role` | string | no | Target role to optimize for |
| `tone` | string | no | `professional`, `personal`, `thought-leader` (default: `professional`) |

**Returns:** `{ headline, about_section, skills_to_add, keywords }`

---

## get_salary_insights

Get market salary data.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | yes | Job title |
| `location` | string | yes | City or region |
| `company` | string | no | Specific company |
| `years_experience` | integer | no | Years of experience |
| `include_equity` | boolean | no | Include equity data (default: true) |

**Returns:**
```json
{
  "base_salary": {
    "p25": 180000, "p50": 210000, "p75": 240000, "p90": 280000
  },
  "bonus_pct": { "typical": 15, "max": 30 },
  "equity_annual": { "p50": 80000, "p75": 150000 },
  "total_comp_p50": 290000,
  "data_points": 847,
  "last_updated": "2025-01"
}
```

---

## generate_negotiation_script

Generate a personalized salary negotiation script.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `current_offer` | integer | yes | Current offer amount |
| `target_salary` | integer | yes | Target salary |
| `role` | string | yes | Job title |
| `company` | string | yes | Company name |
| `justifications` | array | yes | List of justification points |
| `style` | string | no | `conservative`, `balanced`, `aggressive` (default: `balanced`) |

**Returns:** `{ script, email_template, talking_points, counter_offer_range }`

---

## research_company

Get comprehensive company information.

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | yes | Company name |
| `include_interview_tips` | boolean | no | Include interview style tips (default: false) |
| `include_salary_data` | boolean | no | Include salary benchmarks (default: false) |

**Returns:** `{ overview, culture, recent_news, ratings, funding, interview_style, red_flags }`

---

## Error Codes

| Code | Meaning |
|------|---------|
| `APPLICATION_NOT_FOUND` | Application ID invalid |
| `RESUME_NOT_FOUND` | Resume ID invalid |
| `INVALID_STATUS` | Status value not recognized |
| `JOB_DESCRIPTION_TOO_SHORT` | Job description must be at least 100 characters |
| `COMPANY_NOT_FOUND` | Company not in database — try a different name |
| `INSUFFICIENT_DATA` | Not enough salary data for this role/location combination |
