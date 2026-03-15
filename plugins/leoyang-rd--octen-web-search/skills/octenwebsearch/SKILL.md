---
name: OctenWebSearch
description: "An end-to-end Web Search API specifically for AI agents. Returns the most relevant, real-time, and high-fidelity information available on the internet."
homepage: https://octen.ai
---

# Octen Web Search

An end-to-end Web Search API specifically for AI agents. Returns the most relevant, real-time, and high-fidelity information available on the internet.

## Search

```bash
bash {baseDir}/scripts/search.sh "here is your query"
bash {baseDir}/scripts/search.sh "here is your query" -n 10
bash {baseDir}/scripts/search.sh "here is your query" --start_time "2026-01-01T00:00:00Z"
bash {baseDir}/scripts/search.sh "here is your query" --end_time "2026-01-31T23:59:59Z"
```

## Options

- `-n <count>`: Optional. Number of results (min: 1, max: 20, if not provided, default to 5)
- `--start_time <time>`: Optional. Start time for filtering results (ISO 8601 format, e.g., "2026-01-01T00:00:00Z").
- `--end_time <time>`: Optional. End time for filtering results (ISO 8601 format, e.g., "2026-01-31T23:59:59Z"). If start_time and end_time are both provided, end_time must be greater than start_time.

## Notes
- Needs `OCTEN_API_KEY` in the environment variables, get it from https://octen.ai, then set it like this: `export OCTEN_API_KEY=your-api-key`
- Use `--start_time` and `--end_time` if you want to filter results by time published. For example, to search for news published in January 2026, you can use `--start_time "2026-01-01T00:00:00Z" --end_time "2026-01-31T23:59:59Z"`.
