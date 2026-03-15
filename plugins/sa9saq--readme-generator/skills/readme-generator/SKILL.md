---
name: readme-generator
description: "Auto-generate comprehensive README.md files by analyzing project structure and configuration."
---

# README Generator

Analyze a project directory and generate a complete, useful README.md.

## Requirements

- File system access to the target project
- No API keys or external services needed

## Instructions

### Step 1: Scan the project

```bash
# Project structure (exclude noise)
find . -maxdepth 3 -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/venv/*' -not -path '*/.venv/*' | head -80

# Package metadata
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || cat Cargo.toml 2>/dev/null || cat go.mod 2>/dev/null

# Available scripts/commands
jq '.scripts' package.json 2>/dev/null

# License detection
ls LICENSE* LICENCE* 2>/dev/null

# Entry points
ls src/index.* src/main.* main.* app.* cli.* 2>/dev/null
```

### Step 2: Read key files (first 50 lines each)
- Main entry point
- Config files (tsconfig, pyproject, etc.)
- Existing README (to preserve intent)

### Step 3: Generate README with this structure

```markdown
# Project Name
Brief description.

## Features
- Key feature list

## Installation
Steps to install (npm install, pip install, etc.)

## Usage
CLI examples and/or programmatic usage with code blocks.

## API Reference (if applicable)
Document exported functions/endpoints.

## Project Structure
Tree view with brief descriptions of key files.

## Development
Clone, install, test, contribute steps.

## License
Detected license type.
```

### Step 4: Save output
- If no README.md exists → save as `README.md`
- If README.md exists → save as `README.generated.md` and let user decide
- Always ask before overwriting an existing README

## Edge Cases

- **Monorepo**: Detect multiple package.json/go.mod files. Generate root README with links to sub-packages.
- **Empty project**: Generate minimal README with project name and setup placeholder.
- **Non-English comments**: Generate README in English regardless of code comments language.
- **Private/internal projects**: Skip "Publishing" sections; focus on development setup.

## Tips

- **Don't fabricate**: Only document what actually exists in the project. Don't invent features.
- **Be practical**: Installation and usage sections are the most valuable — prioritize them.
- **Code examples**: Use actual file names and real commands from the project.
- Adapt section depth to project complexity (small script → short README).
