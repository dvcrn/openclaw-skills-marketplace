---
name: skill-demo
description: "Open a browser window from user-provided URL input. Use when users ask to open a website, launch a link quickly, or validate browser-launch automation in local development."
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# Skill Demo

Open a local browser window with a normalized URL.

This skill is designed for deterministic browser-launch behavior in local workflows.

## Steps

1. Read the user input as a URL candidate.
2. Normalize whitespace and trim both ends.
3. If the URL has no scheme, prepend `https://`.
4. Allow only `http` and `https`.
5. If input is empty, use default URL:
   - `https://www.openclaw.ai`
6. Open a new browser window.
7. Return one line of status.

## Response Rules

- Return a single plain-text status line.
- Do not include markdown wrappers.
- On success:
  - `Opened browser window: <normalized_url>`
- If the browser reports blocked open:
  - `Browser open was requested but may have been blocked. URL: <normalized_url>`
- On invalid URL/scheme:
  - return an explicit error message.

## Test Cases

Input:
`openclaw.ai`
Output:
`Opened browser window: https://openclaw.ai`

Input:
`https://docs.openclaw.ai`
Output:
`Opened browser window: https://docs.openclaw.ai`

Input:
``
Output:
`Opened browser window: https://www.openclaw.ai`

## Integration Notes

- Use this skill for quick browser-open automation checks.
- Keep URL normalization deterministic so tests can assert exact output text.
- Keep scheme restrictions to avoid unsafe local protocol launches.

## Output

Use the format:

`Opened browser window: <normalized_url>`
