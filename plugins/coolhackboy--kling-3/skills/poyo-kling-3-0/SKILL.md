---
name: poyo-kling-3-0
description: "Kling 3.0 video generation on PoYo / poyo.ai via `https://api.poyo.ai/api/generate/submit`; use for `kling-3.0/standard`, `kling-3.0/pro`, single-shot, multi-shot, `multi_prompt`, `kling_elements`, and sound-enabled output."
---

# PoYo Kling 3.0 Multi-Shot Video Generation

Use this skill for Kling 3.0 jobs on PoYo. It covers single-shot and multi-shot video generation, element-referenced prompting, and sound-enabled output.

## Use When

- The user explicitly asks for `Kling 3.0`, `kling-3.0/standard`, or `kling-3.0/pro`.
- The task needs multi-shot storytelling or structured multi-prompt input.
- The workflow depends on `kling_elements`, reference frames, or sound control.

## Model Selection

- `kling-3.0/standard`: standard-quality entry point.
- `kling-3.0/pro`: higher-quality variant for users who explicitly want pro output.

## Key Inputs

- `sound`, `multi_shots`, and `duration` drive the main workflow.
- `prompt` is for single-shot; `multi_prompt` is for multi-shot.
- `image_urls` is for start/end frames and is also required when `kling_elements` is used.
- `aspect_ratio` supports `1:1`, `16:9`, `9:16`.

## Execution

- Read `references/api.md` for endpoint details, model ids, key fields, example payloads, and polling notes.
- Use `scripts/submit_kling_3_0.sh` to submit a raw JSON payload from the shell.
- If the user only needs a curl example, adapt the example from `references/api.md` instead of rewriting from scratch.
- After submission, report the `task_id` clearly so follow-up polling is easy.

## Output expectations

When helping with this model family, include:
- chosen model id
- final payload or a concise parameter summary
- whether reference images are involved
- returned `task_id` if a request was actually submitted
- next step: poll status or wait for webhook
