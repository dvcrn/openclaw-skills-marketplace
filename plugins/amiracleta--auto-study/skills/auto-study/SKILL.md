---
name: auto-study
description: "Use for browser-based study, quiz, and practice tasks. Best for Yuketang, Xuexitong, Pintia, and similar learning or question pages where you need a persistent profile, a CDP connection through agent-browser, and concise answer or page-action help."
---

# auto-study

This skill provides a browser workflow for study platforms during ordinary practice. It can return answers, select options, fill in answers, clear answers, and submit them as needed.

## When to use

- Want to automatically handle answering tasks in a browser on study platforms, such as practice sets, quizzes, and homework.
- Want the answers for questions on the page.
- Wants answers selected, filled, or cleared on an ordinary practice page.

## Workflow

1. Start Chrome with the intended persistent site profile and a CDP port, or connect to an existing Chrome instance that already exposes a CDP port.
2. Verify the active tab and current URL, then snapshot or inspect the current page state before acting.
3. Interact with the page according to the user's request, such as selecting, filling, or clearing answers, or clicking the submit button.

## Core policy

- Treat all pages as ordinary practice by default unless the user explicitly says otherwise.

- If the user asks for page actions, apply them sequentially with short pauses, usually around 0.1 seconds.

- If the question is presented as an image, read the image directly.

- If the DOM-visible text is obfuscated, encrypted, or obvious gibberish, try to infer the meaning first. If you still cannot make sense of it completely, take a screenshot to answer.

- Reuse the same browser profile for the same site when login state matters.

- Treat a persistent profile as a login-state aid, not as a guarantee of silent auto-login. It may restore cookies, local storage, or only saved credentials, so some sites may still require a visible login click or confirmation step.

- After attaching through CDP, verify the active tab and current URL before trusting the first snapshot. If the current page is not the target page, use `tab list` and switch to the expected site tab first.

- Do not re-click options that already match the target state.

- Do not rely on actions that a normal user could not perform. Prefer the normal user flow whenever possible.

- Keep answers short and easy to scan.

- Do not submit automatically unless the user explicitly asks for it.

- Just infer answer directly, do not search the web unless the user explicitly asks for it.

## Output rules

### Single choice

Return only the final option letter.

### Multiple select

Use comma-separated letters with no extra commentary.

### Fill in the blank or short answer

Return only the expected word or phrase.

## Profile storage

- Default the profile root to `%LOCALAPPDATA%\AutoStudy\browser`.
- When Chrome is launched for this skill outside the workspace, keep profile folders under the active profile root and reuse the same site profile.

## Environment-specific guidance

- For Windows-native usage, read `references/runtime-windows.md`.
- For WSL usage that launches Windows Chrome, read `references/runtime-wsl.md`.

## Browser guidance

- Read `references/browser.md`.

## Platform-specific guidance

- For Xuexitong specifics, read `references/xuexitong.md`.
- For Yuketang specifics, read `references/yuketang.md`.
- For Pintia specifics, read `references/pintia.md`.

## Prerequisites

- **Google Chrome**（Windows）
- [Agent Browser CLI](https://github.com/vercel-labs/agent-browser)
- [Agent Browser Skill](https://clawhub.ai/MaTriXy/agent-browser-clawdbot)
