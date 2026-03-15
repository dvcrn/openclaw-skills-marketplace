---
name: x-twitter-browser
description: "Use a real browser session's cookie header to verify login and perform browser actions on X/Twitter via headless Playwright. Supports posting, replying, reposting, liking, and bookmarking tweets."
---

# x-twitter-browser

Execute browser actions on X using your real browser login state, without the official X API.

Users only need to provide a single `cookie header` string.

After installing into OpenClaw, the skill lives at:

```bash
~/.openclaw/workspace/skills/x-twitter-browser/
```

Commands below assume you run from the skill root directory:

```bash
cd ~/.openclaw/workspace/skills/x-twitter-browser
```

## Use cases

- You want to reuse browser login state instead of the official API
- Running headless on a VM or Linux server
- Building a long-term extensible browser skill for X automation
- You can provide a single `cookie header` string

## Architecture

This skill has two layers:

### 1. Session layer

Persists the user-provided cookie locally (outside the skill directory so it survives skill updates):

- `scripts/save_cookie_header.py`
- `~/.x-twitter-browser/config.json`

### 2. Action layer

Performs actions using the verified browser session. Currently implemented:

- Post tweet: `scripts/post_tweet.py`
- Reply to tweet: `scripts/reply_post.py`
- Repost (retweet) / Quote tweet: `scripts/repost_post.py`
- Like / Unlike tweet: `scripts/like_post.py`
- Bookmark / Remove bookmark: `scripts/bookmark_post.py`

## Implemented features

- Save user-provided cookie header
- Verify that the session is still logged in
- Post plain-text tweets via the browser session
- Reply to a tweet by URL or ID
- Repost (retweet) or Quote tweet (repost with comment) by URL or ID
- Like or Unlike a tweet by URL or ID
- Bookmark or remove bookmark from a tweet by URL or ID

## Dependencies

**Note:** First-time setup can take several minutes (Chromium is ~150MB). Each step may take 1–5 minutes depending on your network. If a package or browser is already installed, that step will finish quickly.

**OpenClaw:** When running `setup.sh` via OpenClaw, it executes in the background and the user cannot see the `echo` output. Forward each progress message (e.g. "Installing playwright...", "✓ Playwright package installed.", "Installing Chromium...") to the user as it appears so they know the setup is progressing.

First-time setup (recommended):

```bash
./scripts/setup.sh
```

## Authentication input

Paste the full browser `Cookie` request header, e.g.:

```text
guest_id=...; auth_token=...; ct0=...; twid=...; ...
```

Important cookies:

- `auth_token`
- `ct0`
- `twid`
- `kdt`
- `att`
- `_twitter_sess`

## Config

Cookie and other config are stored in `~/.x-twitter-browser/config.json` (outside the skill directory, so they survive ClawHub skill updates). Do not commit or share this file.

```json
{
  "cookie_header": "guest_id=...; auth_token=...; ..."
}
```

Future parameters may be added to the same config file.

## Workflow

### 1. Save the user-provided cookie

If the user pastes a cookie header, save it to `~/.x-twitter-browser/config.json`:

```bash
python3 scripts/save_cookie_header.py \
  --cookie-header 'guest_id=...; auth_token=...; ct0=...; twid=...'
```

Or save the cookie to a file first, then import:

```bash
cat > /tmp/cookie.txt <<'EOF'
guest_id=...; auth_token=...; ct0=...; twid=...; ...
EOF

python3 scripts/save_cookie_header.py \
  --cookie-file /tmp/cookie.txt
```

### 2. Verify login state

Before any browser action, run:

```bash
python3 scripts/post_tweet.py \
  --verify-only
```

Success looks like:

```text
Session looks valid: https://x.com/home
```

If verification fails, the cookie may be expired. Ask the user to provide a fresh cookie.

### 3. Post a tweet

After verification succeeds:

```bash
python3 scripts/post_tweet.py \
  --text "hello"
```

### 4. Reply to a tweet

```bash
python3 scripts/reply_post.py \
  --tweet "https://x.com/username/status/123456789" \
  --text "My reply"
```

### 5. Repost (retweet) a tweet

Plain repost (no comment):

```bash
python3 scripts/repost_post.py \
  --tweet "https://x.com/username/status/123456789"
```

Quote tweet (repost with your comment):

```bash
python3 scripts/repost_post.py \
  --tweet "https://x.com/username/status/123456789" \
  --text "My comment"
```

For both reply and repost, `--tweet` accepts a full URL or just the tweet ID.

### 6. Like a tweet

```bash
python3 scripts/like_post.py \
  --tweet "https://x.com/username/status/123456789"
```

Unlike (remove like):

```bash
python3 scripts/like_post.py \
  --tweet "https://x.com/username/status/123456789" \
  --undo
```

### 7. Bookmark a tweet

```bash
python3 scripts/bookmark_post.py \
  --tweet "https://x.com/username/status/123456789"
```

Remove bookmark:

```bash
python3 scripts/bookmark_post.py \
  --tweet "https://x.com/username/status/123456789" \
  --undo
```

For like and bookmark, `--tweet` accepts a full URL or just the tweet ID.

## Rules

- `--verify-only` success means the session is likely usable
- If the page behaves oddly, buttons are disabled, or extra dialogs appear, re-run verification first
- If Chromium fails to start, install Playwright browsers or system deps before blaming the cookie

## Operational requirements

- Run `--verify-only` before any write operation
- Confirm the action and content before executing
- Do not commit cookies or headers to the repo
- Prefer the full cookie header over partial cookies
- Cookie is stored in `~/.x-twitter-browser/config.json`
- Call `scripts/*.py` directly


### `Imported session is not authenticated`

- Cookie expired
- Incomplete header from user
- Account triggered extra verification

Ask the user to provide a fresh, complete cookie header.
