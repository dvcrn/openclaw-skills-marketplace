---
name: agent-render-linking
description: "Create zero-retention agent-render.com links for markdown, code, diffs, CSV, or JSON artifacts. Use when an agent needs to share a nicely rendered artifact in the browser instead of pasting raw content into chat. Trigger for requests like \"share this as a link\", \"make a diff link\", \"render this markdown/code/csv/json\", or when chat rendering is weak. Agent Render is open source, hosted on Cloudflare Pages, and self-hostable. Use platform-specific linked-text syntax only on surfaces that support it cleanly, such as Discord Markdown links, Telegram HTML links, or Slack mrkdwn links; otherwise send a short summary plus the raw URL."
---

# Agent Render Linking

Create browser links for artifacts rendered by `agent-render.com`.

## Project context

Agent Render is:
- open source
- publicly hosted on Cloudflare Pages at `agent-render.com`
- self-hostable for people who want their own deployment
- meant to provide a zero-retention browser viewer for agent-shared artifacts

Source repository:
- `https://github.com/baanish/agent-render`

## Core rule

Keep the artifact content in the URL fragment, not in normal query params.

Use this fragment shape:

```text
#agent-render=v1.<codec>.<payload>
```

Supported codecs:
- `plain`: base64url-encoded JSON envelope
- `lz`: `lz-string` compressed JSON encoded for URL-safe transport

Prefer:
1. `plain` when the payload is small and simplicity matters
2. `lz` when it materially shortens the link

## Envelope shape

Use this JSON envelope:

```json
{
  "v": 1,
  "codec": "plain",
  "title": "Artifact bundle title",
  "activeArtifactId": "artifact-1",
  "artifacts": [
    {
      "id": "artifact-1",
      "kind": "markdown",
      "title": "Weekly report",
      "filename": "weekly-report.md",
      "content": "# Report"
    }
  ]
}
```

## Supported artifact kinds

### Markdown

```json
{
  "id": "report",
  "kind": "markdown",
  "title": "Weekly report",
  "filename": "weekly-report.md",
  "content": "# Report\n\n- Item one"
}
```

### Code

```json
{
  "id": "code",
  "kind": "code",
  "title": "viewer-shell.tsx",
  "filename": "viewer-shell.tsx",
  "language": "tsx",
  "content": "export function ViewerShell() {\n  return <main />;\n}"
}
```

### Diff

Prefer a real unified git patch in `patch`.

```json
{
  "id": "patch",
  "kind": "diff",
  "title": "viewer-shell.tsx diff",
  "filename": "viewer-shell.patch",
  "patch": "diff --git a/viewer-shell.tsx b/viewer-shell.tsx\n--- a/viewer-shell.tsx\n+++ b/viewer-shell.tsx\n@@ -1 +1 @@\n-old\n+new\n",
  "view": "split"
}
```

Use `view: "unified"` or `view: "split"`.

A single `patch` string may contain multiple `diff --git` sections.

### CSV

```json
{
  "id": "metrics",
  "kind": "csv",
  "title": "Metrics snapshot",
  "filename": "metrics.csv",
  "content": "name,value\nrequests,42"
}
```

### JSON

```json
{
  "id": "manifest",
  "kind": "json",
  "title": "Manifest",
  "filename": "manifest.json",
  "content": "{\n  \"ready\": true\n}"
}
```

## Multi-artifact bundles

Use multiple artifacts when the user should switch between related views.

Example cases:
- summary markdown + patch diff
- report markdown + raw CSV
- config JSON + related code file

Set `activeArtifactId` to the artifact that should open first.

## Link construction

Construct the final URL as:

```text
https://agent-render.com/#agent-render=v1.<codec>.<payload>
```

For `plain`:
1. Serialize the envelope as compact JSON
2. Base64url-encode it
3. Append it after `v1.plain.`

For `lz`:
1. Serialize the envelope as compact JSON
2. Compress with `lz-string` URL-safe encoding
3. Append it after `v1.lz.`

## Practical limits

Respect these limits:
- target fragment budget: about 8,000 characters
- target decoded payload budget: about 200,000 characters

If a link is getting too large:
1. switch from `plain` to `lz`
2. trim unnecessary prose or metadata
3. prefer a focused artifact over a bloated one

## Formatting links in chat

Use platform-specific link text only on surfaces that support it cleanly.

### Discord

Prefer standard Markdown links:

```md
[Short summary](https://agent-render.com/#agent-render=...)
```

Examples:
- `[Weekly report](https://agent-render.com/#agent-render=...)`
- `[Config diff](https://agent-render.com/#agent-render=...)`
- `[CSV snapshot](https://agent-render.com/#agent-render=...)`

### Telegram

Prefer HTML links because OpenClaw Telegram outbound text uses `parse_mode: "HTML"`.

```html
<a href="https://agent-render.com/#agent-render=...">Short summary</a>
```

### Slack

Prefer Slack `mrkdwn` link syntax:

```text
<https://agent-render.com/#agent-render=...|Short summary>
```

### All other OpenClaw chat surfaces

For WhatsApp, Signal, iMessage, Google Chat, IRC, LINE, and any other surface without reliable inline link-text formatting, do not force Markdown-style links.

Use:
- a short summary line first
- then the raw URL on its own line

If a provider later exposes a reliable native linked-text format, use that provider-specific syntax instead of generic Markdown.

## Output style

When sharing a link:
- keep the summary short
- make the artifact title human-readable
- use filenames when they help the viewer
- do not narrate the transport details unless the user asks

## Good defaults

- Prefer one strong artifact over many weak ones
- Prefer `patch` for diffs
- Prefer readable titles
- Prefer Markdown link text when supported
- Prefer `lz` only when it clearly helps link size

## Avoid

- Do not put raw artifact content in normal query params
- Do not upload artifact content to a server for this workflow
- Do not dump giant noisy bundles when a focused artifact is enough
- Do not invent unsupported fields unless the renderer has added them
