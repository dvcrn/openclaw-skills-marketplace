---
name: resize-magic
description: "Resize images using ImageMagick (CLI). Entrypoint is a Bash script."
---

## Overview

This skill provides a single executable script `scripts/resize.sh` that the agent (or the `openclaw` CLI) can call to resize an image with ImageMagick.

## Installation (manual)
Copy the folder into your OpenClaw skills directory, e.g.:

```bash
cp -r resize-magic ~/.openclaw/skills/resize-magic

# or install via CLI if available
openclaw skill install ./resize-magic
```