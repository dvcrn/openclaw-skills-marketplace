---
name: skill-auto-evolver
description: "Analyze and improve OpenClaw agent skills by tracking usage, checking skill health, scanning code quality, and generating actionable improvement suggestions. Use when evaluating skill reliability, performance, maintainability, or release readiness."
---

# Skill Auto Evolver

A Python CLI tool for analyzing and improving OpenClaw agent skills.

## Features

- usage monitoring
- skill health scoring
- SKILL.md and code analysis
- automated improvement suggestions
- JSON / Markdown / HTML reporting

## Installation

```bash
clawhub install skill-auto-evolver
```

## Typical Commands

```bash
skill-auto-evolver init
skill-auto-evolver analyze <skill-name>
skill-auto-evolver analyze --all
skill-auto-evolver report <skill-name>
skill-auto-evolver report --all
skill-auto-evolver health <skill-name>
skill-auto-evolver health --all
skill-auto-evolver log <skill-name> <action> --status success --duration 100
skill-auto-evolver feedback <skill-name> 5 --comment "Very helpful"
skill-auto-evolver clear --days 90
skill-auto-evolver log --list
```

## Dependencies

- Python 3.8+
- SQLite3
- PyYAML
- GitPython (optional)
