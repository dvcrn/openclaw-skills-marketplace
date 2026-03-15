# AnyGen Suite (All-in-One)

[中文](./README_zh.md)

> All-in-one AI content generation skill for [OpenClaw](https://github.com/openclaw/openclaw) / Claude Code / Cursor

A **unified skill** that combines all AnyGen content generation capabilities in a single package. One installation, all features.

> 💡 **Prefer modular installation?** Check out [anygen-skills](https://github.com/AnyGenIO/anygen-skills) for individual, task-specific skills.

## Features

| Operation | Description | File Download |
|-----------|-------------|--------------|
| `slide` | Generate PPT/Slides | Yes (.pptx) |
| `doc` | Generate Documents | Yes (.docx) |
| `smart_draw` | Diagram generation (professional / hand-drawn) | Yes (.png) |
| `storybook` | Create storybooks | Yes (.pptx) |
| `data_analysis` | Data analysis & visualization | Online only |
| `deep_research` | Long-form research reports | Online only |
| `website` | Website development | Online only |
| `finance` | Financial research / earnings analysis | Online only |
| `ai-designer` | Design Images | Online only |

## Quick Start

1. **Install**:
   ```bash
   # OpenClaw
   git clone https://github.com/AnyGenIO/anygen-suite-skill.git ~/.openclaw/skills/anygen-suite

   # Claude Code
   git clone https://github.com/AnyGenIO/anygen-suite-skill.git ~/.claude/skills/anygen-suite
   ```

2. **Get API Key** from [AnyGen](https://www.anygen.io/home?auto_create_openclaw_key=1)

3. **Configure API Key**:
   ```bash
   python3 scripts/anygen.py config set api_key "sk-xxx"
   ```

4. **Use dialogue mode** (recommended — multi-turn requirement analysis):
   ```bash
   # Start requirement analysis
   python3 scripts/anygen.py prepare \
     --message "I need a presentation about AI applications" \
     --save ./conversation.json

   # Continue conversation with answers
   python3 scripts/anygen.py prepare \
     --input ./conversation.json \
     --message "Focus on enterprise use cases, 10 slides" \
     --save ./conversation.json

   # When status=ready, create the task
   python3 scripts/anygen.py create \
     --operation slide \
     --prompt "<prompt from suggested_task_params>"
   ```

5. **Quick mode** (skip dialogue, create directly):
   ```bash
   python3 scripts/anygen.py create \
     --operation slide \
     --prompt "A presentation about AI applications"
   ```

6. **Monitor and download**:
   ```bash
   # Poll until completion
   python3 scripts/anygen.py poll --task-id task_xxx

   # Download file
   python3 scripts/anygen.py download --task-id task_xxx --output ./output/

   # Download thumbnail only
   python3 scripts/anygen.py thumbnail --task-id task_xxx --output ./output/
   ```

## Commands

| Command | Description |
|---------|-------------|
| `prepare` | Multi-turn requirement analysis before creating a task |
| `create` | Create a generation task |
| `upload` | Upload a reference file and get a file_token |
| `poll` | Poll task status until completion (blocking) |
| `status` | Query task status once (non-blocking) |
| `download` | Download generated file |
| `thumbnail` | Download thumbnail preview image |
| `run` | Full workflow: create → poll → download |
| `config` | Manage API Key configuration |

## Parameters (create)

| Parameter | Short | Description |
|-----------|-------|-------------|
| --operation | -o | Operation type: slide, doc, smart_draw, storybook, data_analysis, website, finance, deep_research |
| --prompt | -p | Content description |
| --language | -l | Language: zh-CN or en-US |
| --slide-count | -c | Number of PPT pages |
| --template | -t | Slide template |
| --ratio | -r | Slide ratio: 16:9 or 4:3 |
| --style | -s | Style preference |
| --file-token | | File token from upload (repeatable) |
| --export-format | -f | Export format (slide/storybook: pptx/image/thumbnail, doc: docx/image/thumbnail, smart_draw: drawio/excalidraw) |

## Related Projects

- **[anygen-skills](https://github.com/AnyGenIO/anygen-skills)** — Modular skills collection (install individual skills as needed)

## More Details

See [SKILL.md](./SKILL.md) for complete documentation.

## License

MIT
