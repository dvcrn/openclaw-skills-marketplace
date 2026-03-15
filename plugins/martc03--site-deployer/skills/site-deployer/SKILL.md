---
name: site-deployer
description: "Deploy Next.js sites to Netlify with approval gates. Supports soilrichbyjohn.com and Synergy salon."
homepage: https://github.com/martc03/openclaw-ultimate
---

# Site Deployer

Deploy and manage Next.js websites on Netlify from your phone.

## Sites

| Site | Domain | Repo |
|------|--------|------|
| soilrich | soilrichbyjohn.com | ~/soilrich-website |
| synergy | Synergy salon | ~/synergy-website |

## Commands

### `deploy [site]`
Build and deploy a site to Netlify. **Requires explicit user approval before executing.**

```
deploy soilrich
deploy synergy
```

Execution steps:
1. `cd ~/[site]-website && git pull`
2. `npm run build`
3. `netlify deploy --prod`
4. Log result to Notion "Deploy History" database

### `deploy status [site]`
Check the current deployment status on Netlify.

```
deploy status soilrich
```

Runs `netlify status` in the site's repo directory.

### `deploy rollback [site]`
Rollback to the previous deployment. **Requires explicit user approval.**

```
deploy rollback soilrich
```

Uses `netlify rollback` to revert to the previous production deploy.

### `deploy logs [site]`
Show recent deploy logs from Netlify.

```
deploy logs synergy
```

Runs `netlify deploy --json | jq '.[-5:]'` to show the last 5 deploys.

## Approval Gate

All `deploy` and `rollback` commands require the user to confirm before executing. The agent must:
1. Present a summary of what will be deployed (site name, current branch, latest commit)
2. Wait for explicit "yes" or "confirm" response
3. Only then execute the deploy

## Notion Integration

After each deploy, create an entry in the "Deploy History" database:
- Deploy: Short description of what was deployed
- Site: soilrich or synergy
- Status: Success, Failed, or Rolled Back
- Timestamp: Current date/time
- CommitHash: Git commit SHA that was deployed
- Notes: Any relevant details

## Setup

Requires Netlify CLI authenticated:
```bash
npm install -g netlify-cli
netlify login
```
