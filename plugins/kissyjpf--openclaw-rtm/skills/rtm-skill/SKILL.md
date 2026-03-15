---
name: rtm-skill
description: "Remember The Milk skill for OpenClaw"
---

# Remember The Milk (RTM) Skill for OpenClaw

This skill integrates [Remember The Milk](https://www.rememberthemilk.com/) with OpenClaw, allowing you to manage your daily tasks directly from the command line.

## Setup and Authorization

Before you can use the commands to manage your tasks, you need to authorize the skill with your Remember The Milk account.

1.  **Start Authorization:**
    ```bash
    rtm auth
    ```
    This command will provide you with an authorization URL. Open this URL in your web browser and authorize the application.

2.  **Save Token:**
    After authorizing in the browser, run the following command with the `frob` provided.
    ```bash
    rtm token <frob>
    ```
    This will save your authentication token locally (`~/.rtm-token.json`) so you only need to do this once.

## Available Commands

Once authorized, you can use the following commands to interact with your tasks.

### List Tasks

List all your incomplete tasks:

```bash
rtm list
```

This will fetch and display your incomplete tasks along with their short IDs, lists (categories), priorities, due dates, tags, and notes. The short ID corresponds to the task's index in the list, which is used for completing or deleting tasks.

### Add a Task

Create a new task:

```bash
rtm add <task name>
```

Example: `rtm add Buy groceries`

### Complete a Task

Mark a specific task as completed using its short ID (obtainable via `rtm list`):

```bash
rtm complete <id>
```

Example: `rtm complete 1`

*(Note: You must run `rtm list` before running this command so the short IDs are cached.)*

### Delete a Task

Delete a specific task using its short ID:

```bash
rtm delete <id>
```

Example: `rtm delete 2`

*(Note: You must run `rtm list` before running this command so the short IDs are cached.)*
