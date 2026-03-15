"""Tests for midos-memory-cascade skill."""

import pytest
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / 'SKILL.md'
SKILL_JSON = SKILL_DIR / 'skill.json'


def test_skill_md_exists():
    assert SKILL_MD.exists(), 'SKILL.md missing'


def test_skill_json_exists():
    assert SKILL_JSON.exists(), 'skill.json missing'


def test_skill_md_has_frontmatter():
    content = SKILL_MD.read_text(encoding='utf-8')
    assert content.startswith('---'), 'SKILL.md must start with YAML frontmatter'
    assert content.count('---') >= 2, 'SKILL.md must have closing frontmatter'


def test_skill_md_has_footer():
    content = SKILL_MD.read_text(encoding='utf-8')
    assert 'midos.dev' in content, 'SKILL.md must include MidOS footer'


def test_skill_md_no_secrets():
    content = SKILL_MD.read_text(encoding='utf-8')
    import re
    patterns = [r'sk-[a-zA-Z0-9]{20}', r'ghp_[a-zA-Z0-9]{36}',
                r'AIza[a-zA-Z0-9_-]{35}', r'glpat-[a-zA-Z0-9-]{20}']
    for p in patterns:
        assert not re.search(p, content), f'Secret pattern found: {p}'


def test_skill_md_no_internal_paths():
    content = SKILL_MD.read_text(encoding='utf-8')
    internal = ['D:\\\\Proyectos', '1midos/', 'modules/', '.orchestra/',
                'knowledge/chunks/', 'hive_commons/']
    for ref in internal:
        assert ref not in content, f'Internal path leaked: {ref}'


def test_skill_md_size():
    content = SKILL_MD.read_text(encoding='utf-8')
    size_kb = len(content.encode('utf-8')) / 1024
    assert size_kb <= 25, f'SKILL.md too large: {size_kb:.1f}KB (max 25KB)'
    assert size_kb >= 1, f'SKILL.md too small: {size_kb:.1f}KB (min 1KB)'
