#!/usr/bin/env python3
"""
Quick validation script for OpenClaw skills - validates SKILL.md structure and frontmatter.

Adapted from Anthropic's Claude Code skill-creator.
Licensed under Apache 2.0.
"""

import sys
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from pathlib import Path


def validate_skill(skill_path):
    """Basic validation of an OpenClaw skill."""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    if HAS_YAML:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in frontmatter: {e}"
    else:
        # Fallback: basic key extraction without yaml module
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                key = line.split(':', 1)[0].strip()
                value = line.split(':', 1)[1].strip()
                frontmatter[key] = value

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if isinstance(description, str):
        description = description.strip()
        if description:
            if '<' in description or '>' in description:
                return False, "Description cannot contain angle brackets (< or >)"
            if len(description) > 1024:
                return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Check body content length
    body = content[match.end():].strip()
    line_count = len(body.split('\n'))
    if line_count > 500:
        return False, f"SKILL.md body is {line_count} lines (recommended max: 500). Consider moving content to references/."

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
