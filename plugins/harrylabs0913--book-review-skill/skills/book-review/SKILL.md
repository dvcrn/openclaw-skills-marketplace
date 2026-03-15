---
name: book-review
description: "Expand reading insights into in-depth reviews with personalized references from your notes. Usage: In chat, type /book-review [reading insight], and AI will search your notes for relevant references to generate a thoughtful book review."
---

# Book Review Skill

Expand reading insights into in-depth reviews with personalized references from your notes.

## Features

- 📖 **Insight Expansion**: Expand short reading notes into in-depth book reviews
- 🔍 **Smart References**: Search your note library for related passages to reference
- 🎯 **Personalized Recommendations**: Recommend related books based on user's reading history
- 💡 **Deep Analysis**: Comprehensive analysis combining multiple knowledge points

## Usage

In chat, type:
```
/book-review [your reading insight]
```

For example:
```
/book-review Today I read about deliberate practice and found it very inspiring
```

## Tech Stack

- TypeScript
- nodejieba (Chinese word segmentation)
- lunr (full-text search)
- DeepSeek AI

## Dependencies

- Node.js >= 18.0.0
- OpenClaw >= 2026.3.0
