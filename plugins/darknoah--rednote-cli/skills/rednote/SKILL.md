---
name: rednote
description: "Use when the user needs to publish, search, inspect, log into, or otherwise operate Xiaohongshu (RedNote) from the terminal with the `@skills-store/rednote` CLI. When handling `rednote login`, expect the command to return a local QR code image path on success and present that QR code image to the user."
---

# Rednote Commands

Use this skill only for the CLI command surface of `@skills-store/rednote` when the user wants to operate Xiaohongshu from the terminal.

Focus on giving the exact command, the minimal required flags, and the right command order.

## Preferred command style

Prefer global-install examples first:

```bash
npm install -g @skills-store/rednote
bun add -g @skills-store/rednote
rednote <command> [...args]
```

Only mention `npx -y @skills-store/rednote ...` if the user explicitly asks for one-off execution without global installation.

Only show local repo commands if the user is explicitly developing the CLI.

Use `rednote --version` when the user wants to confirm the installed `@skills-store/rednote` version before troubleshooting or upgrading.

For Xiaohongshu operation commands, default to omitting `--instance`. Assume the CLI uses the current or default connected instance unless the user explicitly asks to target a named instance.
If `browser list` shows no custom instance yet, tell the user to create one first with `rednote browser create --name <NAME> ...`. A name is required for creation; prefer a short, stable name such as `seller-main`.

## Core workflow

Use this sequence for most live Xiaohongshu operations:

1. `rednote env`
2. `rednote browser list`; if no custom instance exists, create one with `rednote browser create --name seller-main --browser chrome --port 9222`
3. `rednote browser connect`
4. `rednote login` or `rednote check-login`
5. `rednote status`
6. Operate with `home`, `search`, `get-feed-detail`, `get-profile`, `publish`, or `interact`

If the user needs exact browser subcommands, flags, or examples, open `./references/browser.md`.

If the instance is blocked by a stale profile lock, check `./references/browser.md` for the force reconnect command.

## Common use cases

### Find posts from home feed

Read the current recommendation feed:

```bash
rednote home --format md
rednote home --format json --save ./output/home.jsonl
```

Use `home` when the user wants to browse candidate posts from the personalized feed before choosing one to inspect or comment on.

### Find posts by keyword

Search by keyword:

```bash
rednote search --keyword 护肤
rednote search --keyword 护肤 --format json --save ./output/search.jsonl
```

Use `search` when the user wants candidate notes for a topic instead of the home feed.

### Get one note's detail

Fetch one note by URL:

```bash
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy"
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --format json
```

Use `get-feed-detail` after `home` or `search` when the user wants the title,正文,互动数据,图片/视频, and existing comments before taking an action.


### Interact with one note

Perform one note interaction by URL:

```bash
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --like --collect
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --like --collect --comment "内容写得很清楚，步骤也很实用，感谢分享。"
```

Use `interact` when the user wants one command entrypoint for like, collect, or comment. Combine `--like`, `--collect`, and `--comment TEXT` to perform multiple operations in one command. Use `--comment TEXT` for replies; there is no standalone `comment` command.

### Publish content

Publish content for an authenticated instance.

Video note:

```bash
rednote publish --type video --video ./note.mp4 --title 标题 --content 描述 --tag 穿搭 --tag 日常 --publish
```

Image note:

```bash
rednote publish --type image --image ./1.jpg --image ./2.jpg --title 标题 --content 描述 --tag 探店 --publish
```

Article:

```bash
rednote publish --type article --title 标题 --content $'# 一级标题\n\n正文' --publish
```

Use `publish` when the user wants to post or save drafts from an authenticated browser instance.

## End-to-end examples

### Home → detail → interact comment

Find a post, inspect it, then reply:

```bash
rednote home --format md
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy"
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --comment "谢谢分享，信息整理得很完整，对我很有帮助。"
```

### Home → detail → like or collect

Inspect a post, then like or collect it:

```bash
rednote home --format md
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy"
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --like --collect
```

### Search → detail → interact comment

Start from a keyword, then reply on the detail page:

```bash
rednote search --keyword 低糖早餐 --format md
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --format json
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --comment "这份搭配看起来很实用，食材和步骤都写得很清楚。"
```

### Inspect profile after finding a post

Check the author before engaging:

```bash
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --format json
rednote get-profile --id USER_ID
```

## Command reference

### `browser`

Use `browser list` to inspect default browsers, custom instances, stale locks, and the current `lastConnect` target.

Use `browser create` to create a reusable named browser profile for later account-scoped commands. Creation requires `--name`; if the user has no custom instance yet, tell them to pick a name first and then create it, for example `rednote browser create --name seller-main --browser chrome --port 9222`.

For exact `browser` subcommands, flags, and examples, open `references/browser.md`.

### `version`

```bash
rednote --version
```

Use `--version` when the user wants to check the installed `@skills-store/rednote` version.

### `env`

```bash
rednote env
rednote env --format json
```

Use `env` when the user is debugging installation or local setup.

### `status`

```bash
rednote status
```

Use `status` to confirm whether the instance exists, is running, and appears logged in.

### `check-login`

```bash
rednote check-login
```

Use `check-login` when the user only wants to verify whether the session is still valid.

### `login`

```bash
rednote login
```

Use `login` after `browser connect` if the account is not authenticated yet.
If `login` succeeds and returns `rednote.qrCodePath`, show the QR code image to the user instead of only repeating the path so they can scan it immediately.

### `home`

```bash
rednote home --format md --save
```

Use `home` when the user wants the current home feed and optionally wants to save it.

### `search`

```bash
rednote search --keyword 护肤
rednote search --keyword 护肤 --format json --save ./output/search.jsonl
```

Use `search` when the user wants notes by keyword.

### `get-feed-detail`

```bash
rednote get-feed-detail --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy"
```

Use `get-feed-detail` when the user already has a note URL and wants structured detail data.

### `get-profile`

```bash
rednote get-profile --id USER_ID
```

Use `get-profile` when the user wants author or account profile information.

### `interact`

```bash
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --like --collect
rednote interact --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --like --collect --comment "内容写得很清楚，感谢分享。"
```

Use `interact` when the user wants a unified command for like, collect, or comment. Use `--comment TEXT` for replies.

## JSON success shapes

When the user asks for JSON output, use these success shapes as the stable mental model.

### Common note item shape

`home`, `search`, and `profile.notes` share the normalized `RednotePost` shape:

```json
{
  "id": "string",
  "modelType": "string",
  "xsecToken": "string|null",
  "url": "string",
  "noteCard": {
    "type": "string|null",
    "displayTitle": "string|null",
    "cover": {
      "urlDefault": "string|null",
      "urlPre": "string|null",
      "url": "string|null",
      "fileId": "string|null",
      "width": "number|null",
      "height": "number|null",
      "infoList": [{ "imageScene": "string|null", "url": "string|null" }]
    },
    "user": {
      "userId": "string|null",
      "nickname": "string|null",
      "nickName": "string|null",
      "avatar": "string|null",
      "xsecToken": "string|null"
    },
    "interactInfo": {
      "liked": "boolean",
      "likedCount": "string|null",
      "commentCount": "string|null",
      "collectedCount": "string|null",
      "sharedCount": "string|null"
    },
    "cornerTagInfo": [{ "type": "string|null", "text": "string|null" }],
    "imageList": [{ "width": "number|null", "height": "number|null", "infoList": [{ "imageScene": "string|null", "url": "string|null" }] }],
    "video": { "duration": "number|null" }
  }
}
```

### Feed and profile commands

`home --format json`:

```json
{
  "ok": true,
  "home": {
    "pageUrl": "string",
    "fetchedAt": "string",
    "total": "number",
    "posts": ["RednotePost"],
    "savedPath": "string|undefined"
  }
}
```

`search --format json`:

```json
{
  "ok": true,
  "search": {
    "keyword": "string",
    "pageUrl": "string",
    "fetchedAt": "string",
    "total": "number",
    "posts": ["RednotePost"],
    "savedPath": "string|undefined"
  }
}
```

`get-feed-detail --format json`:

```json
{
  "ok": true,
  "detail": {
    "fetchedAt": "string",
    "total": "number",
    "items": [{
      "url": "string",
      "note": {
        "noteId": "string|null",
        "title": "string|null",
        "desc": "string|null",
        "type": "string|null",
        "interactInfo": {
          "liked": "boolean|null",
          "likedCount": "string|null",
          "commentCount": "string|null",
          "collected": "boolean|null",
          "collectedCount": "string|null",
          "shareCount": "string|null",
          "followed": "boolean|null"
        },
        "tagList": [{ "name": "string|null" }],
        "imageList": [{ "urlDefault": "string|null", "urlPre": "string|null", "width": "number|null", "height": "number|null" }],
        "video": { "url": "string|null", "raw": "unknown" } | null,
        "raw": "unknown"
      },
      "comments": [{
        "id": "string|null",
        "content": "string|null",
        "userId": "string|null",
        "nickname": "string|null",
        "likedCount": "string|null",
        "subCommentCount": "number|null",
        "raw": "unknown"
      }]
    }]
  }
}
```

`get-profile --format json`:

```json
{
  "ok": true,
  "profile": {
    "userId": "string",
    "url": "string",
    "fetchedAt": "string",
    "user": {
      "userId": "string|null",
      "nickname": "string|null",
      "desc": "string|null",
      "avatar": "string|null",
      "ipLocation": "string|null",
      "gender": "string|null",
      "follows": "string|number|null",
      "fans": "string|number|null",
      "interaction": "string|number|null",
      "tags": ["string"],
      "raw": "unknown"
    },
    "notes": ["RednotePost"],
    "raw": {
      "userPageData": "unknown",
      "notes": "unknown"
    }
  }
}
```

## Flag guidance

- `--instance NAME` picks the browser instance for account-scoped commands.
- `--format json` is best for scripting.
- `--format md` is best for direct reading.
- `--save` is useful for `home` and `search` when the user wants saved output.
- `--keyword` is required for `search`.
- `--url` is required for `get-feed-detail` and `interact`.
- `interact` uses `--comment TEXT` for comment content; there is no standalone `comment` command.
- `interact` requires at least one of `--like`, `--collect`, or `--comment TEXT`.
- `--id` is required for `get-profile`.
- `--type`, `--title`, `--content`, `--video`, `--image`, `--tag`, and `--publish` are the main `publish` flags.
- `publish` usually requires a connected and logged-in instance before running; without `--publish`, it saves a draft.

## Response style

When answering users:

- lead with the exact command they should run
- include only the flags needed for that task
- prefer one happy-path example first
- mention `browser connect` and `login` if the command requires an authenticated instance
- if no custom instance exists yet, first tell the user to create one and call out that `--name` is required
- recommend `home` or `search` first when the user still needs to find a post
- recommend `get-feed-detail` before `interact --comment` when the user wants to inspect the post before replying

## Troubleshooting

If a command fails, check these in order:

- the instance name is correct
- the browser instance was created or connected; if no custom instance exists yet, create one first with `rednote browser create --name NAME ...`
- login was completed for that instance
- the profile was not blocked by a stale lock; if it was, run `rednote browser connect --instance NAME --force`
- the user provided the required flag such as `--keyword`, `--url`, `--comment`, `--content`, or `--id`
