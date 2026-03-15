---
name: placed-interview-coach
description: "This skill should be used when the user wants to \"practice interview\", \"mock interview\", \"prepare for interview\", \"system design interview\", \"behavioral interview\", \"STAR stories\", \"interview coaching\", or wants to prepare for technical interviews using the Placed career platform at placed.exidian.tech."
---

# Placed Interview Coach

AI-powered interview preparation via the Placed platform.

## Prerequisites

Requires the Placed MCP server. Install via:
```json
{
  "mcpServers": {
    "placed": {
      "command": "npx",
      "args": ["-y", "@exidian/placed-mcp"],
      "env": {
        "PLACED_API_KEY": "your-api-key",
        "PLACED_BASE_URL": "https://placed.exidian.tech"
      }
    }
  }
}
```
Get your API key at https://placed.exidian.tech/settings/api

## Available Tools

- `start_interview_session` — Begin a mock interview for a specific role
- `continue_interview_session` — Answer questions and get real-time feedback
- `get_interview_feedback` — Get detailed performance analysis
- `list_interview_cases` — Browse system design cases
- `start_system_design` — Start a system design interview (URL Shortener, Twitter, Netflix, Uber)
- `get_behavioral_questions` — Get STAR-format behavioral questions
- `save_story_to_bank` — Save STAR stories for reuse across interviews

## Interview Types

### Technical Interviews (Coding)

To start a mock interview:
```
start_interview_session(
  resume_id="your-resume-id",
  job_title="Senior Software Engineer",
  difficulty="hard",
  company="Google"
)
```

To answer each question:
```
continue_interview_session(
  session_id="session-123",
  user_answer="I would use a hash map to store key-value pairs for O(1) lookup..."
)
```

To get feedback on performance:
```
get_interview_feedback(session_id="session-123")
```

### System Design Interviews

To list available cases:
```
list_interview_cases()
# Returns: Design Twitter, Design URL Shortener, Design Netflix, Design Uber, etc.
```

To start a system design session:
```
start_system_design(
  case_id="design-twitter",
  difficulty="senior"
)
```

**System Design Framework:**
1. **Requirements Clarification** — Functional and non-functional requirements
2. **High-Level Architecture** — Components, data flow, APIs
3. **Database Design** — Schema, indexing, replication, sharding
4. **Scalability** — Load balancing, caching, CDN, horizontal scaling
5. **Fault Tolerance** — Redundancy, failover, monitoring
6. **Trade-offs** — CAP theorem, consistency vs. availability

### Behavioral Interviews

To get behavioral questions for a target role:
```
get_behavioral_questions(
  target_role="Engineering Manager",
  focus_categories=["leadership", "conflict-resolution", "failure"]
)
```

**STAR Method** — Structure every answer:
- **Situation** — Context and background
- **Task** — Your responsibility and challenge
- **Action** — What you did specifically
- **Result** — Outcome with metrics

### Story Banking

To save STAR stories for reuse across interviews:
```
save_story_to_bank(
  situation="Led team through major refactor",
  task="Reduce technical debt while shipping features",
  action="Created phased plan, mentored junior devs, set clear milestones",
  result="30% faster deployments, improved morale, reduced bugs by 25%",
  category="leadership"
)
```

## Interview Flow

1. **Prepare** — Research company, review resume, practice with resources
2. **Start Session** — Begin mock interview with your resume and target role
3. **Answer Questions** — Think out loud, explain your reasoning
4. **Get Feedback** — Review performance after each question
5. **Iterate** — Practice multiple times, improve weak areas
6. **Save Stories** — Bank STAR stories for behavioral interviews

## Tips

**Technical Interviews:**
- Clarify requirements before diving into code
- Discuss trade-offs (time vs. space, simplicity vs. optimization)
- Test your solution with examples
- Explain your thought process

**System Design:**
- Start with requirements and constraints
- Draw diagrams and explain components
- Discuss scalability bottlenecks
- Consider failure scenarios

**Behavioral:**
- Use STAR method consistently
- Include specific metrics and outcomes
- Show growth and learning
- Be authentic and honest
