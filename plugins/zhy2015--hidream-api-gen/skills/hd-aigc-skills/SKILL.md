---
name: hd-aigc-skills
description: "OpenClaw AIGC models (video + image) with parameterized per-model scripts and shared request runners. Use to generate OpenClaw payloads, enforce allowed parameters, and run or debug model requests."
---

# HD AIGC Skills

This skill provides per-model scripts that validate parameters and call shared request runners.

## Configuration & Usage (AI Agent Instructions)

When a user wants to use this skill, follow these steps:

1.  **Check for Token**: Check if `OPENCLAW_AUTHORIZATION` environment variable is set.
2.  **Request Token**: If the token is missing, instruct the user to:
    *   Go to `https://vivago.ai/platform/token` to generate a token.
    *   Provide the token back to you.
3.  **Configure**: Once the user provides the token, use it in subsequent calls (or set it as an env var if possible).
4.  **Generate**: Use the Python interface to generate content based on user requests.

### Error Handling

- **Insufficient Credits**: If the API returns `{"code": 2007, "message": "No credits available"}`, instruct the user to:
    *   Go to `https://vivago.ai/platform/info` to recharge credits.


## Python Interface (Recommended)

You can call the scripts directly from Python code. This is the preferred way for AI agents to interact.

### Image Generation (Seedream)

```python
from scripts.seedream import run as run_seedream

# Example: Generate an image
try:
    result = run_seedream(
        version="M2",
        prompt="A cyberpunk cat on the moon",
        resolution="2048*2048",
        authorization="sk-..." # Optional if env var is set
    )
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

### Video Generation (Kling)

```python
from scripts.kling import run as run_kling

# Example: Generate a video
try:
    result = run_kling(
        version="Q2.5T-std",
        prompt="A cyberpunk cat running on neon streets",
        duration=5,
        authorization="sk-..." # Optional if env var is set
    )
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

## Structure

- `scripts/commom/base_image.py`: shared OpenClaw image request runner
- `scripts/common/base_video.py`: shared OpenClaw video request runner
- `scripts/common/task_client.py`: http request runner
- `scripts/*.py`: per-model scripts (parameter parsing + payload only)

## Auth and Endpoints

Set one of the following environment variables, or pass `--authorization` to scripts:

- `OPENCLAW_AUTHORIZATION`: Bearer token value only
- `OPENCLAW_ENDPOINT`: API Endpoint (default: `https://vivago.ai`)

## Video Model Scripts

- `scripts/sora_2_pro.py`
- `scripts/seedance_1_0_pro.py`
- `scripts/seedance_1_5_pro.py`
- `scripts/minimax_hailuo_02.py`
- `scripts/kling.py` (Refactored for Python access)

## Image Model Scripts

- `scripts/seedream.py` (Refactored for Python access)
- `scripts/nano_banana.py`

## Notes

- Per-model scripts only handle parameter parsing and payload building.
- Base scripts handle request submission, polling, and auth.
