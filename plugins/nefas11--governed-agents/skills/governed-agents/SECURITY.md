# Security

## Prompt-Injection Detection Patterns

The prompt-injection detector uses a small set of detection-only regex patterns to flag attempts to override or bypass prior instructions. These patterns are **not** used for filtering or transformation; they are only used for detection and reporting.

## Secret Leak Prevention

By default, governed subprocesses run with a minimal environment (only `PATH` and `NO_COLOR`). This reduces the chance of accidentally exposing API keys or other secrets to subprocesses.

If you set `GOVERNED_PASS_ENV=1`, the wrapper will pass your full environment through to subprocesses and emit a warning. This is an escape hatch for advanced usage but increases the risk of secret leakage.

Best practices:
- Audit your environment for sensitive values before enabling full passthrough.
- Prefer scoped credentials with limited permissions and short lifetimes.
- Avoid setting secrets in the shell/session used to run governed agents when possible.
