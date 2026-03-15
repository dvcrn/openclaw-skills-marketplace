# ai-dating Skill

`ai-dating` is a skill package for friend-making and matchmaking workflows.  
It uses `dating-cli` for account handling, profile updates, match-task management, result checking, contact reveal, and post-chat reviews.

## Capability Overview

- Register or log in a dating account (`register` / `login`)
- Upload profile images to MinIO (`upload`)
- Update profile and contact fields (`profile update`)
- Create, update, and stop match tasks (`task create/update/stop`)
- Poll and inspect match candidates (`check`)
- Reveal candidate contact details (`reveal-contact`)
- Submit a rating and review after communication (`review`)

## Trigger Scenarios

Use this skill when the user:

- Asks to make friends, find a partner, or run matchmaking
- Provides self-information and wants candidate recommendations
- Provides partner preferences (for example gender, height, income, city, personality, hobbies) and asks for matching

## Prerequisites

1. `dating-cli` is available on the local machine
2. The user is registered/logged in
3. Network access to backend services is available

Check availability:

```bash
command -v dating-cli
dating-cli --help
dating-cli config show
dating-cli config path
```

Install if missing (pick one):

```bash
npm install -g dating-cli
# or
bun install -g dating-cli
```

## Standard Execution Flow

1. Verify CLI availability and local config.
2. Register or log in.
3. Parse user self-description and update profile.
4. Parse partner preferences and create a match task.
5. If an unfinished task already exists and the user did not explicitly ask for a new one, update that task.
6. Query task state and run `check`.
7. If `watchStatus=NO_RESULT_RETRY_NOW`, continue polling.
8. If `watchStatus=MATCH_FOUND`, pick the best candidate and run `reveal-contact`.
9. After communication, run `review`.
10. If needed, run `task stop` / `logout` / `config clear-token`.

## Quick Examples

### 1) Register or Login

```bash
dating-cli register --username "amy_2026"
# or
dating-cli login --username "amy_2026" --password "123456"
```

### 2) Update Profile

```bash
dating-cli upload "./photos/amy-1.jpg" "./photos/amy-2.jpg"
```

This command uploads files via `/minio/upload` and directly updates `/member-profile` `photoUrls` with the URL array.

```bash
dating-cli profile update \
  --gender male \
  --birthday 1998-08-08 \
  --height-cm 180 \
  --annual-income-cny 300000 \
  --character-text "sincere, steady, humorous" \
  --hobby-text "badminton, travel, photography" \
  --ability-text "cooking, communication, English" \
  --city "Hangzhou" \
  --current-location-text "Hangzhou West Lake" \
  --telegram "amy_tg" \
  --wechat "amy_wechat"
```

### 3) Create Match Task

```bash
dating-cli task create \
  --task-name "Find partner in Hangzhou" \
  --preferred-gender-filter '{"eq":"female"}' \
  --preferred-height-filter '{"gte":165,"lte":178}' \
  --preferred-income-filter '{"gte":200000}' \
  --preferred-city-filter '{"eq":"Hangzhou"}' \
  --preferred-hobby-text "reading, travel" \
  --preferred-character-text "kind, positive" \
  --preferred-ability-text "strong communication" \
  --intention "long-term relationship" \
  --hobby-embedding-min-score 0.72 \
  --character-embedding-min-score 0.70 \
  --ability-embedding-min-score 0.68 \
  --intention-embedding-min-score 0.70 \
  --preferred-contact-channel telegram
```

For `task create`, omitted embedding min-score fields default to `0.1`.

### 4) Check Result and Reveal Contact

```bash
dating-cli check 12345
dating-cli reveal-contact 67890
```

### 5) Submit Review

```bash
dating-cli review 67890 --rating 5 --comment "Good communication and aligned values"
```

## Output Conventions

Most commands return a standard JSON envelope.

Success:

```json
{
  "ok": true,
  "response": {
    "code": 200,
    "message": "Success",
    "data": {}
  }
}
```

Failure:

```json
{
  "ok": false,
  "error": {
    "message": "...",
    "status": 500,
    "payload": {}
  }
}
```

Important `check` fields:

- `response.data.watchStatus`: `MATCH_FOUND` or `NO_RESULT_RETRY_NOW`
- `response.data.candidates[].photoUrls`: candidate photo URL array
- `response.data.candidates[]`: candidate list (score-related field keeps `rankScore` only)

## Recommended Practices

- Complete profile fields before creating tasks to improve match quality.
- Prefer updating existing active tasks over repeatedly creating new tasks.
- Poll `check` at a fixed interval (for example every 5 minutes).
- Perform manual verification and communication after contact reveal.
- Submit `review` after communication to improve ranking quality and trust/safety signals.

## References

- Skill definition: `SKILL.md`
- Command and field details: `references/dating-cli-operations.md`
