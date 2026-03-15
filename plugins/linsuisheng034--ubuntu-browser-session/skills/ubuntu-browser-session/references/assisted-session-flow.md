# Assisted Session Flow

The assisted flow starts a GUI browser stack on Ubuntu Server, exposes it through noVNC, and captures a validated manifest after the user finishes the blocked step.

The standalone runtime layer below it is `scripts/browser-runtime.sh`, which handles:

- headless direct browsing
- GUI browsing on Xvfb for challenge auto-pass attempts
- CDP target discovery
- best-match page target selection by exact URL, then origin, then host
- manifest-based attach and verify operations

`scripts/assisted-session.sh` layers `x11vnc` and `websockify` on top of a GUI runtime when the user must see and operate the same live browser instance.

Current runtime behavior:

- derive scoped `run_dir`, `profile_dir`, and `log_dir` from `origin + session-key`
- auto-pick free CDP ports, X displays, VNC ports, and noVNC ports unless explicitly pinned
- keep the assisted overlay attached to the same live browser instance instead of opening a fresh browser

Expected control flow:

1. Reuse or start the GUI browser runtime on `Xvfb`
2. Classify the current page as challenge, login wall, or usable page
3. Start `x11vnc` and `websockify` without replacing the live browser context
4. Show the user a noVNC URL and a next-action message tailored to the blockage type
5. Re-check the same live browser through CDP
6. Capture a manifest only after challenge and login-wall checks are both clear

Typical commands:

```bash
scripts/assisted-session.sh start --url 'https://target.example' --origin 'https://target.example' --session-key default
scripts/assisted-session.sh status --origin 'https://target.example' --session-key default
scripts/assisted-session.sh capture --origin 'https://target.example' --session-key default --block-reason login-wall
scripts/assisted-session.sh stop --origin 'https://target.example' --session-key default
```
