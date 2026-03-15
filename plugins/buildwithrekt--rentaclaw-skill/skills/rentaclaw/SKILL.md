---
name: rentaclaw
description: "List and manage your AI agent on the Rentaclaw marketplace - a decentralized marketplace for AI agent rentals on Solana. Earn SOL by renting out your agent."
---

# Rentaclaw Skill

This skill allows you to list and manage your OpenClaw agent on the Rentaclaw marketplace - a decentralized marketplace for AI agent rentals on Solana.

## Getting Started

Before using this skill, you need a Rentaclaw API key:

1. Go to https://www.rentaclaw.io/dashboard/api-keys
2. Sign in with your Solana wallet or email
3. Generate an API key
4. Set it as `RENTACLAW_API_KEY` in your skill credentials
5. Use `rentaclaw_setup` to verify the connection

After listing your agent, configure your webhook URL in the Rentaclaw dashboard to receive rental requests.

## Available Commands

### Setup
When the user wants to configure Rentaclaw, use `rentaclaw_setup` with their API key.

### List Agent
When the user wants to list their agent on Rentaclaw:
1. Ask for the agent name and description
2. Ask for pricing (per hour, day, and month in SOL)
3. Optionally ask for category
4. Use `rentaclaw_list` to create the listing
5. Return the marketplace URL to the user

### Check Status
When the user asks about their listings, use `rentaclaw_status` to show all their agents.

### View Stats
When the user asks about earnings or statistics, use `rentaclaw_stats` to show:
- Total earnings
- Number of rentals
- Active renters
- Average rating

### Update Listing
When the user wants to change something about their listing, use `rentaclaw_update`.

### Pause/Resume
When the user wants to temporarily stop rentals, use `rentaclaw_pause` with action "pause".
To resume, use action "resume".

## Example Conversations

**User:** "List my agent on Rentaclaw"
**Agent:** "I'll help you list your agent! What would you like to name it?"
... gather details ...
**Agent:** "Your agent is now live at https://www.rentaclaw.io/marketplace/xxx"

**User:** "How much have I earned?"
**Agent:** *uses rentaclaw_stats*
"You've earned 12.5 SOL from 8 rentals. You currently have 2 active renters."

**User:** "Pause my trading bot listing"
**Agent:** *uses rentaclaw_pause*
"Done! Your agent is now paused and won't accept new rentals."

## Pricing Guidelines

Suggest reasonable pricing based on the agent type:
- Simple bots: 0.01-0.05 SOL/hour
- Advanced agents: 0.1-0.5 SOL/hour
- Premium/specialized: 1+ SOL/hour

Monthly pricing is typically 50-70% of (hourly × 720 hours).
