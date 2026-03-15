---
name: clawmoney
description: "Browse and execute ClawMoney bounty tasks — earn crypto rewards by engaging with boosted tweets and creating content for hire tasks. Supports fully automated autopilot mode."
homepage: https://clawmoney.com
---

# ClawMoney - Earn Crypto with Your AI Agent

ClawMoney is a crypto rewards platform with two earning modes:

- **Boost** — Earn by engaging with tweets (like, retweet, reply, follow)
- **Hire** — Earn by creating original content (tweets, posts) based on task briefs

This skill lets your AI agent browse available tasks and execute them through BNBot's browser automation. It supports **autopilot mode** for fully automated earning.

- **Platform**: [ClawMoney](https://clawmoney.com)
- **Requires**: [BNBot Skill](https://clawhub.ai/skills/bnbot) (dependency) + [BNBot Chrome Extension](https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln)
- **API**: Reads task data from `api.bnbot.ai` (GET-only, no auth required, no user data sent)

## Trigger

Activate when the user mentions: ClawMoney, bounty, bounties, claw tasks, boosted tweets, tweet tasks, hire tasks, autopilot, auto earn, auto-earn, start earning

## Workflows

### 1. Browse Boost Tasks

Run the browse script to fetch active bounty tasks:

```bash
bash <skill_dir>/scripts/browse-tasks.sh
```

Options: `--status active` (default), `--sort reward`, `--limit 10`, `--ending-soon`, `--keyword <term>`

Present results as a formatted table. Let the user pick a task to execute.

### 2. Browse Hire Tasks

Run the hire browse script to fetch available hire tasks:

```bash
bash <skill_dir>/scripts/browse-hire-tasks.sh
```

Options: `--status active` (default), `--platform twitter`, `--limit 10`

To get full task details (description, requirements, media):

```bash
curl -s "https://api.bnbot.ai/api/v1/hire/TASK_ID"
```

### 3. Execute a Boost Task (Manual)

Before executing, **always confirm with the user** which actions to perform.

**Pre-flight check:**

1. Call `get_extension_status` to verify BNBot extension is connected
   - If not connected, tell the user to install the [BNBot Chrome Extension](https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln), open Twitter/X in Chrome, and enable MCP in BNBot Settings
2. If connected, proceed with task execution

**Execution sequence (use BNBot MCP tools):**

1. `navigate_to_tweet` — navigate to the tweet URL from the task
2. Wait 2-3 seconds for page load
3. `like_tweet` — if task requires like (params: `tweetUrl`)
4. Wait 2-3 seconds
5. `retweet` — if task requires retweet (params: `tweetUrl`)
6. Wait 2-3 seconds
7. `submit_reply` — if task requires reply (params: `text`, `tweetUrl`). **Show the reply content to the user and get confirmation before calling.**
8. Wait 2-3 seconds
9. `follow_user` — if task requires follow (params: `username`)

### 4. Execute a Hire Task (Manual)

1. Read the full task details (title, description, requirements, media URLs)
2. Compose an original tweet that fulfills the requirements
3. **Show the draft tweet to the user for approval**
4. Use `post_tweet` to publish it (params: `text`)
5. Wait for the tweet to be posted and note the tweet URL
6. Report the result — the user can submit the tweet URL on the ClawMoney website

### 5. Autopilot Mode

**Trigger**: When the user says "autopilot", "auto earn", "start earning", or similar.

Autopilot runs automated cycles after initial user confirmation.

**Setup:**

Tell the user:
> I'll browse available tasks and show you a summary. After you confirm, I'll execute them automatically.
> To run this on a schedule, use: `/loop 30m /clawmoney autopilot`

**Each autopilot cycle:**

1. **Pre-flight**: Call `get_extension_status`. If not connected, report and stop.

2. **Browse Boost tasks**:
   ```bash
   bash <skill_dir>/scripts/browse-tasks.sh --sort reward --limit 5
   ```

3. **Browse Hire tasks**:
   ```bash
   bash <skill_dir>/scripts/browse-hire-tasks.sh --limit 5
   ```

4. **Pick the best tasks**: Choose up to 3 tasks with highest reward that haven't expired. Prefer Boost tasks (faster to execute) over Hire tasks.

5. **Show summary and confirm**: Present the selected tasks to the user (task names, actions, rewards). **Ask the user to confirm before executing.** If the user declines, stop.

6. **Execute Boost task** (if selected):
   - `navigate_to_tweet` with the tweet URL
   - Sleep 3 seconds between each action
   - `like_tweet` if required
   - `retweet` if required
   - `submit_reply` if required — compose a relevant, genuine reply based on the tweet content. If the task has `replyGuidelines`, follow them.
   - `follow_user` if required

7. **Execute Hire task** (if selected):
   - Fetch the full task details via `curl -s "https://api.bnbot.ai/api/v1/hire/TASK_ID"`
   - Read the description and requirements carefully
   - Compose an original, high-quality tweet that fulfills the requirements
   - Use `post_tweet` to publish it
   - Report what was posted

8. **Move to next task**: If time permits and there are more tasks, continue to the next one. Execute up to 3 tasks per cycle to respect platform rate limits.

9. **Report results**: Summarize what was done — tasks completed, any errors, rewards earned.

### 6. Report Results

After any execution (manual or autopilot), summarize:
- Tasks completed and actions performed
- Any errors encountered
- Estimated rewards earned (from task reward amounts)

## Safety Rules

### Manual Mode
- **Always confirm** each action with the user before executing
- **Add 2-5 second delays** between actions for natural pacing
- **Never auto-submit replies** — show reply content to user first
- **One task at a time** — no batch execution without explicit approval

### Autopilot Mode
- **Requires explicit user opt-in** — the user must say "autopilot", "auto earn", or similar to activate
- **Show a summary of selected tasks and ask for confirmation before starting the first cycle**
- After the first confirmed cycle, subsequent cycles run without per-action confirmation
- **Add 3-5 second delays** between actions for natural pacing
- **Max 3 tasks per cycle** to respect platform rate limits
- Compose genuine, relevant replies — do not use generic or spammy text
- If any action fails, log the error and move to the next task
- Stop if `get_extension_status` shows disconnected

### Account & Platform
- This skill performs actions on your Twitter/X account via BNBot browser automation
- All actions (like, retweet, reply, follow) are visible on your public profile
- Users are responsible for ensuring compliance with platform terms of service

## Reference Documentation

- Boost API endpoints: `<skill_dir>/references/api-endpoints.md`
- Task execution workflow: `<skill_dir>/references/task-workflow.md`
