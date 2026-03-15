# Commands Reference

Use this file when the user needs command variants, install details, or a broader command catalog than the main skill should carry.

## Install

Prefer `uv`:

```bash
uv tool install xhs-cli
uv tool upgrade xhs-cli
```

Fallback:

```bash
pipx install xhs-cli
pipx upgrade xhs-cli
```

Source checkout for development:

```bash
git clone https://github.com/jackwener/xhs-cli.git
cd xhs-cli
uv sync
```

## Auth

Default flow:

```bash
xhs status
xhs login
xhs whoami --json
```

Other auth variants:

```bash
xhs login --qrcode
xhs login --cookie "a1=...; web_session=..."
xhs logout
```

Prefer `xhs login` over manual cookie input.

## Search and Read

```bash
xhs search "coffee"
xhs search "coffee" --json

xhs read NOTE_ID
xhs read NOTE_ID --comments
xhs read NOTE_ID --xsec-token TOKEN
xhs read NOTE_ID --comments --json
```

`xsec_token` is auto-cached after successful search/feed flows, so manual `--xsec-token` is usually a fallback.

## User and Account

```bash
xhs whoami
xhs whoami --json

xhs user USER_ID
xhs user USER_ID --json

xhs user-posts USER_ID
xhs user-posts USER_ID --json

xhs followers USER_ID --json
xhs following USER_ID --json
```

Use `whoami --json` to discover the current account's internal `userId`.

## Feed, Topics, and Favorites

```bash
xhs feed
xhs feed --json

xhs topics "travel"
xhs topics "travel" --json

xhs favorites
xhs favorites --max 10
xhs favorites --json
```

## Interaction

```bash
xhs like NOTE_ID
xhs like NOTE_ID --undo

xhs favorite NOTE_ID
xhs favorite NOTE_ID --undo

xhs comment NOTE_ID "Helpful post."
xhs delete NOTE_ID
```

Run `xhs status` before write operations.

## Publish

```bash
xhs post "Title" --image ./cover.jpg --content "Body text"
xhs post "Title" --image ./a.jpg --image ./b.jpg --content "Body text"
xhs post "Title" --image ./cover.jpg --content "Body text" --json
```

## JSON-Oriented Patterns

```bash
xhs search "coffee" --json
xhs read NOTE_ID --comments --json
xhs whoami --json
xhs favorites --json
```

Prefer JSON output when the result will be parsed or reused.

## Troubleshooting

- If `xhs` is missing, install it with `uv tool install xhs-cli`.
- If auth fails, run `xhs login` again.
- If saved auth looks stale, confirm with `xhs status` and `xhs whoami --json`.
- If a note action fails because of token resolution, refresh context with `xhs search ...` or supply `--xsec-token`.

## Upstream

- Repo: `https://github.com/jackwener/xhs-cli`
- Package: `https://pypi.org/project/xhs-cli/`
