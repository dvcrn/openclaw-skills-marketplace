---
name: wekan
description: "Manage a self-hosted Trello-like board via `wekancli`.  Create, move and archive cards, lists and boards on a WeKan server. Use when user asks about task boards or anything Trelo-like.  Not for: Github issues or simple reminders."
---

# wekancli

Use `wekancli` to create, move and archive cards/tasks in Wekan boards.  Tool 
operates under with a specific user session/identity but Agents may be configured to 
provide their own unique tokens corresponding to identities that can be configured
in their name.

## Quick start

List boards: `wekancli list boards <USER_ID>`
List Lists: `wekancli list lists <BOARD_ID>`
List Cards: `wekancli list cards <BOARD_ID> --list-id <LIST_ID>`
Create Card: `wekancli create card <BOARD_ID> <LIST_ID> "Card Title" <AUTHOR USER_ID>`
Move Card: `wekancli edit card <CARD_ID> -f listId=<NEW_LIST_ID>`
Archive Card: `wekancli archive card <CARD_ID>`

## References
- `references/cli-examples.md` (real `wekancli` examples)
- `references/user-install.md` (installation instructions for users)
