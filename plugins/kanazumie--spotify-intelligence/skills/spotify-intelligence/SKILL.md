---
name: spotify-intelligence
description: "Spotify intelligence skill with Python runners for auth, playback control, recommendations, feedback loop, governance, and explainable playlist decisions."
---

# Spotify Intelligence (ClawHub Edition)

This edition is ClawHub-validator compatible (text + python-focused).  
The full local Windows edition may include additional PowerShell wrappers.

## Required env
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- optional `SPOTIFY_REDIRECT_URI`

## Core Python entrypoints
- Auth token exchange: `scripts/auth/oauth_auth.py`
- Playback control: `scripts/playback/playback_control.py`
- Recommendations: `scripts/recommend/recommend-now.py`
- Recommendation helper: `scripts/recommend/recommend_commands.py`
- Derived features: `scripts/decision/rebuild-derived-features.py`

## Key capabilities
- Playback (play/pause/next/previous/volume/device/queue)
- Song search with own-playlist preference + global fallback
- Recommendation modes: `passend`, `mood-shift`, `explore`
- Feedback-aware scoring (like/dislike/skip/keep)
- Governance and decision logging (DB-backed)

## References
- `references/read-layer.md`
- `references/playback-control.md`
- `references/recommendation-layer.md`
- `references/feedback-loop.md`
- `references/governance-cost.md`
- `references/status-handover-2026-02-24.md`
