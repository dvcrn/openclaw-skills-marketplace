# Initialization Script for Nima Skill Creator

This script initializes a new skill project following the Nima Skill Creator framework.

## Usage

```bash
python init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

## Options

- `skill-name`: Name of the skill (lowercase-hyphen-case)
- `--path`: Output directory path
- `--resources`: Comma-separated list of resource directories to create
- `--examples`: Include example files

## Example

```bash
python init_skill.py my-skill --path /path/to/skills --resources scripts,references --examples
```
