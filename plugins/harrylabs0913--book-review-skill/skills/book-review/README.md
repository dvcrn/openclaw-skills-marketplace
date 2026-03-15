# 📚 OpenClaw Book Review Skill

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3.2-blue.svg)
![OpenClaw](https://img.shields.io/badge/openclaw-2026.3.0-orange.svg)

**Transform every reading insight into deep, thoughtful analysis**

[Features](#-features) • [Quick Start](#-quick-start) • [Examples](#-examples) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

## 🎯 Project Overview

The Book Review Skill is an OpenClaw plugin that transforms brief reading insights into in-depth, personalized book reviews. It searches your personal note library to find relevant content references and generates insightful extended analysis.

### Core Values
- **Deepen Thinking**: Transform fragmented insights into systematic thinking
- **Knowledge Connection**: Automatically link your existing notes to build knowledge networks
- **Personalization**: Generate customized reviews based on your reading history and note content
- **Efficiency Boost**: Quickly obtain in-depth reading feedback, saving organization time

## ✨ Features

### Core Features
- ✅ **Smart Parsing**: Automatically analyze themes, sentiment, and keywords from reading insights
- ✅ **Note Search**: Intelligently search relevant content in your note library
- ✅ **AI Generation**: Generate in-depth extended reviews using DeepSeek API
- ✅ **Personalized References**: Quote your note content to provide personalized feedback
- ✅ **Multi-format Output**: Support Markdown, plain text, and HTML formats

### Advanced Features
- 🔄 **Batch Processing**: Support processing multiple reading insights at once
- ⚙️ **Flexible Configuration**: Configurable note paths, AI models, output formats, etc.
- 🛡️ **Error Recovery**: Comprehensive error handling and fallback solutions
- 📊 **Statistics**: Provide processing statistics and performance monitoring

### Integration Support
- 🧠 **OpenClaw Integration**: Seamlessly integrate as an OpenClaw Skill
- 📝 **Note Tools**: Support Obsidian, Logseq, and plain Markdown files
- 🔌 **Extension Interface**: Provide API interfaces for other applications to call

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/harrylabs0913/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# Install dependencies
npm install

# Build the project
npm run build

# Install to OpenClaw
npm link
```

### Configuration

1. **Set Environment Variables**:
```bash
# DeepSeek API Key
export DEEPSEEK_API_KEY=sk-your-api-key

# Note library paths (supports multiple, comma-separated)
export BOOK_REVIEW_NOTE_PATHS=~/Documents/Notes,~/Obsidian
```

2. **OpenClaw Configuration**:
Add to `~/.openclaw/openclaw.json`:
```json
{
  "skills": {
    "book-review": {
      "enabled": true,
      "path": "/path/to/openclaw-skill-book-review"
    }
  }
}
```

### Basic Usage

#### Command Line Usage
```bash
# Basic usage
book-review "To Live taught me the resilience of life"

# Specify output format
book-review "Insight content" --format html

# Specify language and style
book-review "Reading insight" --language en --style academic
```

#### OpenClaw Chat Usage
In OpenClaw chat, simply type:
```
/book-review Your reading insight here
```

For example:
```
/book-review The concept of deliberate practice in "Peak" is very inspiring
```

## 💡 Usage Examples

### Example 1: Fiction Review
**Input**:
```
/book-review "To Live" made me understand the resilience of life
```

**Output**:
```markdown
## Deep Review: The Resilience of Life in "To Live"

### Core Insight
Yu Hua's "To Live" profoundly portrays the resilience of life through Fugui's experiences...

### Extended Thinking
[Related content from your notes will be quoted here]

### Similar Books Recommendation
- "The Kite Runner": Also about life's hardships and redemption
- "The Road": Father-son relationship in extreme environments

### Practical Application
How to apply this insight to your life...
```

### Example 2: Non-fiction Analysis
**Input**:
```
/book-review The concept of deliberate practice in "Peak" is very inspiring
```

**Output**:
```markdown
## Analysis: The Scientific Path to Expertise

### Core Concept
Anders Ericsson's "Peak" reveals the secret of deliberate practice...

### Knowledge Connection
[Related notes from your knowledge base]

### Action Suggestions
1. Set specific, measurable practice goals
2. Seek immediate feedback
3. Step out of your comfort zone

### Extended Reading
- "Mindset": Growth mindset and learning
- "Grit": The power of persistence
```

## 🏗️ Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Book Review Skill               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Parser     │  │   Searcher   │  │   Generator  │     │
│  │  (Analysis)  │  │(Note Search) │  │  (AI Review) │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ▼                                │
│              ┌──────────────────────┐                     │
│              │    Output Engine     │                     │
│              │ (Format & Reference) │                     │
│              └──────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Core Modules

#### 1. Parser Module
- **Function**: Parse user input, extract themes, sentiment, keywords
- **Technology**: nodejieba Chinese word segmentation + custom rules

#### 2. Searcher Module
- **Function**: Build note index, full-text search, relevance ranking
- **Technology**: lunr full-text search engine

#### 3. Generator Module
- **Function**: Call DeepSeek API to generate extended reviews
- **Technology**: DeepSeek API + Prompt Engineering

#### 4. Output Engine
- **Function**: Format output, insert references, generate recommendations
- **Technology**: Markdown template engine

## 📋 API Reference

### bookReview(input, options)

Generate a book review from a reading insight.

**Parameters**:
- `input` (string): Reading insight content
- `options` (object): Configuration options
  - `format` (string): Output format (markdown|html|text)
  - `language` (string): Output language (zh|en)
  - `style` (string): Review style (casual|academic|professional)

**Returns**:
- `Promise<string>`: Generated book review

**Example**:
```typescript
import { bookReview } from 'openclaw-skill-book-review';

const review = await bookReview(
  "To Live made me understand the resilience of life",
  { format: 'markdown', language: 'en', style: 'academic' }
);
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | Required |
| `BOOK_REVIEW_NOTE_PATHS` | Note library paths | `~/Documents/Notes` |
| `BOOK_REVIEW_MAX_RESULTS` | Max search results | `5` |
| `BOOK_REVIEW_LANGUAGE` | Default output language | `zh` |

### Configuration File

Create `~/.config/book-review/config.json`:
```json
{
  "ai": {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "maxTokens": 2000
  },
  "search": {
    "maxResults": 5,
    "minScore": 0.3
  },
  "output": {
    "defaultFormat": "markdown",
    "includeReferences": true,
    "includeRecommendations": true
  }
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - The agent framework
- [DeepSeek](https://deepseek.com) - AI model provider
- [nodejieba](https://github.com/yanyiwu/nodejieba) - Chinese word segmentation
- [lunr](https://lunrjs.com) - Full-text search engine

## 📮 Contact

- GitHub Issues: [https://github.com/harrylabs0913/openclaw-skill-book-review/issues](https://github.com/harrylabs0913/openclaw-skill-book-review/issues)
- Email: your.email@example.com

---

<div align="center">

**Made with ❤️ by Digital Partners Team (Pearl, Belle, Harry, Joy)**

</div>
