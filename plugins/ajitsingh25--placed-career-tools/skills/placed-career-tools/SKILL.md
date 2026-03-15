---
name: placed-career-tools
description: "This skill should be used when the user wants to \"track job applications\", \"match resume to job\", \"generate cover letter\", \"optimize resume for job\", \"get interview questions for company\", \"generate LinkedIn profile\", \"add job application\", \"check application status\", \"get salary insights\", \"negotiate salary\", \"research company\", \"analyze resume gaps\", or wants to use AI career tools from the Placed platform at placed.exidian.tech."
homepage: https://placed.exidian.tech
---

# Placed Career Tools

Comprehensive AI career toolkit: job tracking, resume-job matching, cover letter generation, LinkedIn optimization, salary insights, negotiation scripts, and company research — all via the Placed MCP server.

## Overview

Placed Career Tools covers the full job search lifecycle. Track applications through a pipeline, match your resume to job descriptions, generate tailored cover letters, research companies, benchmark salaries, and prepare negotiation scripts — all from your AI assistant.

## Prerequisites

1. Create an account at https://placed.exidian.tech
2. Get your API key from Settings → API Keys
3. Install the Placed MCP server:

```json
{
  "mcpServers": {
    "placed": {
      "command": "npx",
      "args": ["-y", "@exidian/placed-mcp"],
      "env": {
        "PLACED_API_KEY": "your-api-key-here",
        "PLACED_BASE_URL": "https://placed.exidian.tech"
      }
    }
  }
}
```

## Available Tools

### Job Tracking

| Tool                        | Description                               |
| --------------------------- | ----------------------------------------- |
| `add_job_application`       | Add a new job application to your tracker |
| `list_job_applications`     | View your full application pipeline       |
| `update_job_status`         | Move an application to a new stage        |
| `get_application_analytics` | Pipeline analytics and conversion rates   |

### AI Career Tools

| Tool                           | Description                                          |
| ------------------------------ | ---------------------------------------------------- |
| `match_job`                    | Score how well your resume matches a job description |
| `analyze_resume_gaps`          | Find missing keywords and skills for a target role   |
| `generate_cover_letter`        | Generate a tailored cover letter                     |
| `optimize_resume_for_job`      | Tailor resume content to a specific job              |
| `generate_interview_questions` | Get likely interview questions for a company/role    |
| `generate_linkedin_profile`    | AI-optimized LinkedIn headline and About section     |

### Salary & Negotiation

| Tool                          | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| `get_salary_insights`         | Market salary data by role, company, and location |
| `generate_negotiation_script` | Personalized salary negotiation script            |

### Company Research

| Tool               | Description                                         |
| ------------------ | --------------------------------------------------- |
| `research_company` | Company overview, culture, news, and interview tips |

## Quick Start

### Track a job application

```
add_job_application(
  company="Stripe",
  role="Senior Software Engineer",
  job_url="https://stripe.com/jobs/...",
  status="applied",
  resume_id="res_abc123"
)
```

### Match resume to job

```
match_job(
  resume_id="res_abc123",
  job_description="Senior Software Engineer at Stripe — distributed systems, Go, Kubernetes..."
)
# Returns: match score, matched keywords, missing keywords, recommendations
```

### Generate a cover letter

```
generate_cover_letter(
  resume_id="res_abc123",
  company="Airbnb",
  role="Staff Engineer",
  job_description="...",
  tone="professional"
)
```

### Get salary insights

```
get_salary_insights(
  role="Senior Software Engineer",
  company="Google",
  location="San Francisco, CA",
  years_experience=6
)
# Returns: salary range, percentiles, bonus, equity, total comp
```

### Generate negotiation script

```
generate_negotiation_script(
  current_offer=200000,
  target_salary=240000,
  role="Senior Software Engineer",
  company="Stripe",
  justifications=[
    "6 years distributed systems experience",
    "Led 3 high-impact projects at previous company",
    "Market rate for this role in SF is $230-260K"
  ]
)
```

### Research a company

```
research_company(
  company_name="Databricks",
  include_interview_tips=true
)
# Returns: culture, recent news, funding, employee ratings, interview style
```

## Application Pipeline Stages

Standard stages for `update_job_status`:

- `wishlist` — Saved for later
- `applied` — Application submitted
- `phone_screen` — Initial recruiter call
- `technical` — Technical interview round
- `onsite` — On-site or final round
- `offer` — Offer received
- `negotiating` — In negotiation
- `accepted` — Offer accepted
- `rejected` — Application rejected
- `withdrawn` — Withdrew application

## Common Workflows

**Apply to a new job:**

1. `research_company` to understand culture and interview style
2. `match_job` to check resume-job fit score
3. `analyze_resume_gaps` to find missing keywords
4. `optimize_resume_for_job` to tailor resume
5. `generate_cover_letter` for the application
6. `add_job_application` to track it

**Prepare for an interview:**

1. `research_company` for culture and recent news
2. `generate_interview_questions` for likely questions
3. Use `placed-interview-coach` skill for mock sessions

**Negotiate an offer:**

1. `get_salary_insights` to benchmark the offer
2. `generate_negotiation_script` with your justifications
3. Use the conservative, balanced, or aggressive script based on your situation

**Track your pipeline:**

1. `list_job_applications` to see all applications
2. `update_job_status` as applications progress
3. `get_application_analytics` to see conversion rates and identify bottlenecks

## Tips

- Add applications immediately after submitting — tracking is most useful when complete
- Run `match_job` before applying to prioritize high-fit opportunities
- `generate_linkedin_profile` works best when your resume is fully updated first
- `get_salary_insights` returns more accurate data when you specify company + location + years of experience
- Use `analyze_resume_gaps` before `optimize_resume_for_job` to understand what's missing

## Additional Resources

- **`references/api-guide.md`** — Full API reference with all parameters and response schemas
- **Placed Job Tracker** — https://placed.exidian.tech/jobs
- **Placed Career Hub** — https://placed.exidian.tech/career
