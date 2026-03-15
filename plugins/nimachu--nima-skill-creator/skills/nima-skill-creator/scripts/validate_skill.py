# Validation Script for Nima Skill Creator

This script validates skill projects before packaging.

## Usage

```bash
python validate_skill.py <path/to/skill-folder>
```

## Validation Rules

### Required Files
- ✅ SKILL.md exists
- ✅ YAML frontmatter valid
- ✅ name field present
- ✅ description field present

### Naming Conventions
- ✅ name: lowercase-hyphen-case
- ✅ name: <64 characters
- ✅ No special characters except hyphen

### Description Requirements
- ✅ Contains functionality description
- ✅ Contains trigger scenarios

### Directory Structure
- ✅ scripts/ (if exists)
- ✅ references/ (if exists)
- ✅ assets/ (if exists)

## Example

```bash
python validate_skill.py /path/to/skill-folder
```
