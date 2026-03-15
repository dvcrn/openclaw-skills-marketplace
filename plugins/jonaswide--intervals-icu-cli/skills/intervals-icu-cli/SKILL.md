---
name: intervals-icu-cli
description: "Use this skill when an installed `intervals` CLI should be used to query Intervals.icu, inspect activities, create scheduled workout events, create workout library items, or write wellness data. It teaches command selection, JSON-first write patterns, and the event versus workout distinction."
homepage: https://github.com/jonaswide/intervals-cli
---

# intervals-cli

Use this skill when the task involves Intervals.icu and the local `intervals` CLI.

## Before You Start

1. Verify the binary exists:
   - `intervals --version`
2. If it is missing, use the skill's declared installer in OpenClaw or install the CLI manually from GitHub Releases.
3. Verify auth:
   - `intervals auth status`

The CLI expects one of these environment variables:

- `INTERVALS_API_KEY`
- `INTERVALS_ACCESS_TOKEN`

OpenClaw metadata declares `INTERVALS_API_KEY` as the primary env because the skill system supports one primary API-key env. Bearer-token auth via `INTERVALS_ACCESS_TOKEN` is also valid.

## Core Rules

- Prefer `intervals ... --format json`.
- Use absolute dates like `2026-03-16`, not relative values like `tomorrow`.
- Treat stdout as result data and stderr as diagnostics.
- For complex writes, prefer `--file -` or a temp file.
- Payloads for `events`, `workouts`, and `wellness` are raw Intervals-compatible JSON.
- Do not install the CLI unless the user asked for installation or the current task clearly depends on it.
- Do not perform writes or deletes unless the user asked for a mutation.
- If a temp file is used, remove it after the command completes.

## Command Selection

- Use `activities search` for text or tag queries.
- Use `activities list` for semantic filtering on date, type, distance, tags, or moving time.
- Use `events create` or `events upsert` for something scheduled on a specific date.
- Use `workouts create` for a reusable workout library item.
- Use `wellness put` or `wellness bulk-put` for wellness writes.

## Events vs Workouts

- `event`: a scheduled calendar item on a date
- `workout`: a reusable library object not tied to a date

Rule of thumb:

- "Create a workout for next Monday" usually means `events create`.
- "Save this workout for later reuse" means `workouts create`.

## More Guidance

Read these only as needed:

- Write patterns and examples: `{baseDir}/references/writes.md`
- Query guidance: `{baseDir}/references/queries.md`
- Example payloads: `{baseDir}/examples/`

## Good Defaults

- Prefer `events upsert` over `events create` when duplicates would be harmful.
- Resolve natural-language dates before calling the CLI.
- Ask a follow-up question only when a key training detail is ambiguous.
- Prefer read commands first when inspecting or validating before a mutation.
