# OpenClaw Web Gateway

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-web%20ui-black)
![License](https://img.shields.io/badge/license-MIT-green)

A lightweight Flask web gateway for chatting with an OpenClaw agent from a shared browser UI.

This repository is now presented honestly as a **small but functional starter project**:
- shared participant picker
- simple browser chat
- OpenClaw proxy endpoint
- local message log in `memory/messages.jsonl`
- Docker and local run support

It is a good first public repo if you want something clean, understandable, and easy to extend.

## Quick start

### Local

```bash
git clone https://github.com/jeanne0r/openclaw-web-gateway.git
cd openclaw-web-gateway

cp .env.example .env
cp config/participants.example.json config/participants.json

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

./run.sh
```

Open:

```text
http://localhost:5002
```

### Docker

```bash
cp .env.example .env
cp config/participants.example.json config/participants.json
docker compose up --build
```

## Required configuration

Edit `.env` and set at least:
- `OPENCLAW_BASE`
- `OPENCLAW_TOKEN`

Useful optional settings:
- `OPENCLAW_AGENT`
- `OPENCLAW_CHANNEL`
- `OPENCLAW_MODEL`
- `DEFAULT_USER`
- `HOST`
- `PORT`
- `DEBUG`

## Participants

Create:

```text
config/participants.json
```

Example:

```json
[
  {
    "key": "family",
    "display_name": "Family",
    "aliases": ["famille"]
  },
  {
    "key": "romain",
    "display_name": "Romain",
    "aliases": ["rom"]
  }
]
```

## Project layout

```text
app.py                 Flask entry point
config.py              App and environment configuration
memory_store.py        Local JSONL message logging
openclaw_client.py     Minimal OpenClaw HTTP client
prompts.py             Basic system prompt helper
state_manager.py       Simple local state persistence

routes/chat.py         POST /api/chat
routes/state.py        GET /api/bootstrap and /api/health
static/                CSS and JavaScript
templates/             HTML templates
config/                Local participant config
memory/                Local ignored storage
.github/workflows/     GitHub Actions checks
```

## What this repo is and is not

This repo is intentionally small.

It **is**:
- public-friendly
- easy to run
- easy to read
- a decent base for your own Jarvis-style gateway

It is **not yet**:
- a full production gateway
- a complete memory system
- a polished multi-panel dashboard

## Before you push

- verify `.env` is not committed
- verify `config/participants.json` is not committed
- run the app once locally
- send one test message through the UI
- check that GitHub shows the MIT license correctly

## License

MIT
