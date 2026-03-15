---
name: postsyncer
description: "Manage your PostSyncer social media workflows."
---

# PostSyncer Skill

Automate your social media scheduling with PostSyncer.

## Setup

1. Get your API Key from [PostSyncer Settings](https://app.postsyncer.com/settings).
2. Set it: `export POSTSYNCER_API_KEY="your_key"`

## Commands

### Workspaces
List your workspaces.

```bash
postsyncer workspaces
```

### Posts
List your scheduled/published posts.

```bash
postsyncer posts
```

### Create Post
(Basic text post)

```bash
postsyncer create-post -w <workspace_id> -t "Hello world"
```
