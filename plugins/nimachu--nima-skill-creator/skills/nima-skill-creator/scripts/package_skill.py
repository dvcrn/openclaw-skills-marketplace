# Packaging Script for Nima Skill Creator

This script packages validated skills into distributable .skill files.

## Usage

```bash
python package_skill.py <path/to/skill-folder> [output-directory]
```

## Packaging Process

1. **Validate** the skill
2. **Package** into .skill file
3. **Output** to specified directory (or default)

## Security

- Symlinks are rejected
- All files must be regular files

## Example

```bash
python package_skill.py /path/to/skill-folder
python package_skill.py /path/to/skill-folder ./dist
```
