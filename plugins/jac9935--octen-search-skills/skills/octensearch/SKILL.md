---
name: OctenSearch
description: "LLM-native Web Search powered by Octen. Less than 80ms average response, minute-level index freshness, and highly relevant results purpose-built for AI agents."
homepage: https://octen.ai
---

# Octen Search

LLM-native Web Search powered by Octen. Search Infrastructure for AI.

## Search

```bash
python3 {baseDir}/scripts/search.py "here is your query"
python3 {baseDir}/scripts/search.py "here is your query" -n 10
python3 {baseDir}/scripts/search.py "here is your query" --start_time "2026-01-01T00:00:00Z"
python3 {baseDir}/scripts/search.py "here is your query" --end_time "2026-01-31T23:59:59Z"
```

## Options

- `-n, --count <count>`: Optional. Number of results (min: 1, max: 20, if not provided, default to 5)
- `--start_time <time>`: Optional. Start time for filtering results (ISO 8601 format, e.g., "2026-01-01T00:00:00Z")
- `--end_time <time>`: Optional. End time for filtering results (ISO 8601 format, e.g., "2026-01-31T23:59:59Z"). If start_time and end_time are both provided, end_time must be greater than start_time

## Notes
- Needs `OCTEN_API_KEY` in the environment variables, get it from https://octen.ai, then set it like this: `export OCTEN_API_KEY=your-api-key`
- Use `--start_time` and `--end_time` if you want to filter results by time published. For example, to search for news published in January 2026, you can use `--start_time "2026-01-01T00:00:00Z" --end_time "2026-01-31T23:59:59Z"`.

## Security
- The `OCTEN_API_KEY` environment variable is **only sent to the official Octen API endpoint**: `https://api.octen.ai/search`
- No environment variables are sent to any other endpoints or external services
- The API endpoint is **hardcoded and whitelisted** in the code and cannot be modified at runtime
- The skill uses standard HTTP header authentication (`X-Api-Key`) which is the recommended practice for API authentication
- All network requests are made over HTTPS to ensure encrypted transmission of the API key

