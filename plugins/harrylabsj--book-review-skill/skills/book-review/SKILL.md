---
name: book-review
description: "Expand reading insights into in-depth reviews using local templates only. SAFE VERSION: No external API calls, no filesystem access, no secrets required."
---

# Book Review Skill (Safe Version)

Expand reading insights into in-depth reviews using **local templates only**.

## 🔒 Security Features

- **No External API Calls**: All processing happens locally, no data sent to external services
- **No Filesystem Access**: Does not read or write to your filesystem
- **No Secrets Required**: No API keys, tokens, or credentials needed
- **Privacy First**: Your reading insights never leave your local environment

## Features

- 📖 **Insight Expansion**: Expand short reading notes into in-depth book reviews
- 🔒 **Local Processing**: All templates processed locally with no external dependencies
- 📋 **Multiple Formats**: Brief, detailed, and comprehensive review options
- 💡 **Related Concepts**: Get suggested related learning concepts

## Commands

- `/book-review [insight]` - Generate a detailed book review
- `/book-review-brief [insight]` - Generate a brief review
- `/book-review-related [insight]` - Get related concepts for the insight

## Usage Examples

```
/book-review Today I read about deliberate practice and found it very inspiring
/book-review-brief The importance of spaced repetition in learning
/book-review-related How to build effective learning habits
```

## Technical Details

- **TypeScript** implementation
- **OpenClaw SDK** integration
- **Pure Local Processing**: No network calls, no file I/O
- **Version**: 1.0.4 (Safe Release)

## Safety Assurance

This skill has been specifically designed to address ClawHub security concerns:
1. ✅ **No External Dependencies**: Removed all external API calls
2. ✅ **No Filesystem Access**: No reading of local notes or files
3. ✅ **No Secrets**: No environment variables or API keys required
4. ✅ **Transparent Processing**: All logic visible in source code

## Installation

```bash
clawhub install book-review-skill
```

## Requirements

- Node.js >= 18.0.0
- OpenClaw >= 2026.3.0