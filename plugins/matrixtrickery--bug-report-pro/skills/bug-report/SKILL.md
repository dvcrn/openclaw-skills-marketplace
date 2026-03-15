---
name: bug-report
description: "Generate structured, actionable bug reports from rough descriptions — with reproduction steps, expected vs actual behavior, severity classification, and suggested investigation areas."
---

# Bug Report

Turn "it's broken" into a proper bug report. Structured, actionable, developer-ready.

## What It Does

Takes a rough bug description and generates:
- **Title** (concise, searchable)
- **Reproduction steps** (numbered, specific)
- **Expected vs actual behavior**
- **Severity and priority** classification
- **Environment details** template
- **Suggested investigation areas**
- **Related patterns** (common causes for this type of bug)

## Usage

### From description:
```
bug-report "login page crashes when I use special characters in password"
```

### With context:
```
bug-report "API returns 500 on large file uploads" --component "upload-service" --env "production" --frequency "always"
```

### Options:
- `--component` — affected component/service
- `--env` — environment where it occurs: `production`, `staging`, `development`, `local`
- `--frequency` — `always`, `intermittent`, `once`, `unknown`
- `--user-impact` — `blocking`, `major`, `minor`, `cosmetic`
- `--format` — `markdown` (default), `json`, `github` (GitHub issue template)
- `--template` — `standard` (default), `jira`, `linear`, `github`

## Generation Rules

### Title:
- Under 80 characters
- Pattern: `[Component] Short description of the defect`
- Include the failing action and the symptom
- Good: "Login page crashes with special characters in password field"
- Bad: "Bug in login" or "Page doesn't work"

### Reproduction Steps:
1. Start with preconditions (logged in/out, specific data state)
2. Number each step
3. Be specific ("Click the Submit button" not "Submit the form")
4. Include exact input data where relevant
5. End with the step that triggers the bug

### Severity Classification:

| Severity | Criteria | Examples |
|----------|----------|---------|
| **Critical** | System crash, data loss, security vulnerability, no workaround | App crashes on launch, data corruption, auth bypass |
| **High** | Major feature broken, significant user impact, workaround exists but painful | Can't upload files (core feature), slow response (>30s) |
| **Medium** | Feature partially broken, workaround available, moderate impact | Sort order wrong, pagination off by one |
| **Low** | Minor inconvenience, cosmetic, rarely encountered | Typo in error message, alignment issue, tooltip wrong |

### Priority (separate from severity):

| Priority | When to Fix |
|----------|------------|
| P0 | Immediately (production down, security breach) |
| P1 | This sprint / within 48 hours |
| P2 | Next sprint / within 2 weeks |
| P3 | Backlog / when convenient |

### Investigation Suggestions:
Based on the bug type, suggest where to look:

| Bug Pattern | Investigation Areas |
|-------------|-------------------|
| Crash on input | Input validation, character encoding, buffer limits |
| 500 error | Server logs, exception handler, request payload size |
| Intermittent failure | Race conditions, caching, timeouts, connection pooling |
| Wrong data | Query logic, data transformation, timezone handling |
| UI glitch | CSS specificity, viewport handling, browser compatibility |
| Performance | Database queries, N+1 problems, memory leaks, missing indexes |
| Auth issues | Token expiry, session handling, CORS, cookie domain |

### Output (Markdown):

```markdown
# [Upload Service] API returns 500 on large file uploads

**Severity:** High | **Priority:** P1 | **Component:** upload-service
**Environment:** Production | **Frequency:** Always
**Reported:** 2026-03-09

## Description
The file upload API endpoint returns HTTP 500 when uploading files larger than approximately 10MB. Smaller files upload successfully.

## Steps to Reproduce
1. Log into the application with any valid account
2. Navigate to the Upload section
3. Select a file larger than 10MB (tested with 15MB PNG and 25MB PDF)
4. Click "Upload"
5. Observe HTTP 500 response

## Expected Behavior
File uploads successfully and appears in the user's file list.

## Actual Behavior
Server returns HTTP 500 Internal Server Error. No file is saved. No meaningful error message returned to the client.

## Environment
- Browser: Chrome 122 / Firefox 123
- OS: Windows 11, macOS 14
- API Version: v2.3.1
- Server: Production (us-east-1)

## Investigation Suggestions
- Check server logs for the specific exception/stack trace
- Verify upload size limits in nginx/reverse proxy config
- Check application-level file size validation
- Review multipart parsing library for memory limits
- Check disk space on upload volume
- Test with different file types to isolate (is it size or content type?)

## Related Patterns
Large file upload failures commonly caused by:
- Reverse proxy body size limits (nginx: `client_max_body_size`)
- Application framework limits (Express: `bodyParser.json({limit})`)
- Memory exhaustion during multipart parsing
- Request timeout before upload completes
```

### GitHub Issue Template Output (--template github):
Outputs with GitHub-compatible labels and formatting ready for `gh issue create`.
