# 📚 OpenClaw Book Review Skill

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3.2-blue.svg)
![OpenClaw](https://img.shields.io/badge/openclaw-2026.3.0-orange.svg)

**Turn every reading insight into thoughtful reflection**

[Features](#-features) • [Quick Start](#-quick-start) • [Usage Examples](#-usage-examples) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

## 🎯 Overview

The Book Review Skill is an OpenClaw plugin that expands short reading insights into in-depth, personalized reviews. It searches your personal notes library for relevant content references and generates thoughtful expanded reflections.

### Core Value
- **Deepen Thinking**: Transform fragmented insights into systematic reflections
- **Knowledge Connection**: Automatically link your existing notes to build a knowledge network
- **Personalization**: Generate customized reviews based on your reading history and note content
- **Efficiency**: Get in-depth reading feedback quickly, saving整理时间

## ✨ Features

### Core Features
- ✅ **Smart Parsing**: Automatically analyze the theme, sentiment, and keywords of reading insights
- ✅ **Note Search**: Intelligently search your note library for related content
- ✅ **AI Generation**: Generate in-depth expanded reviews based on DeepSeek API
- ✅ **Personalized References**: Reference your note content for personalized feedback
- ✅ **Multi-format Output**: Support Markdown, plain text, and HTML formats

### Advanced Features
- 🔄 **Batch Processing**: Support processing multiple reading insights at once
- ⚙️ **Flexible Configuration**: Configurable note paths, AI models, output formats, etc.
- 🛡️ **Error Recovery**: Robust error handling and fallback mechanisms
- 📊 **Statistics**: Processing statistics and performance monitoring

### Integration Support
- 🧠 **OpenClaw Integration**: Seamlessly integrated as an OpenClaw Skill
- 📝 **Note Tools**: Support Obsidian, Logseq, and plain Markdown files
- 🔌 **Extension API**: Provide API interfaces for other applications

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# Install dependencies
npm install

# Build the project
npm run build

# Install to OpenClaw
npm link
```

### Configuration

1. **Set environment variables**:
```bash
# DeepSeek API key
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

#### Command Line
```bash
# Basic usage
book-review "《活着》让我明白了生命的坚韧"

# Specify output format
book-review "insight content" --format html

# Specify language and style
book-review "Reading insight" --language en --style academic
```

#### In OpenClaw
```bash
# In OpenClaw session
/book-review 《百年孤独》展现了家族命运的轮回
```

#### Programmatic Usage
```typescript
import { main } from './src/index';

const result = await main("《小王子》让我懂得了纯真的珍贵");
console.log(result.content);
```

## 📖 Usage Examples

### Example 1: Chinese Reading Insight
**Input:**
```
《活着》让我明白了生命的坚韧
```

**Output:**
```markdown
## 📚 Book Review

**Original Insight:** 《活着》让我明白了生命的坚韧

**Expanded Review:**
As Yu Hua describes in "To Live": "People exist for the sake of living itself, not for anything beyond living," your insight deeply captures the novel's core theme. From your notes, I see you recorded: "Although Fugu's life was full of suffering, he always maintained his persistence in life," which aligns highly with Yu Hua's creative intent.

This contemplation on the essence of life is why "To Live" can touch countless readers. The resilience of life is not only reflected in the will to survive, but also in the continuous pursuit of life's meaning.

**Related References:**
- **"To Live" Reading Notes:** "Through Fugu's life, Yu Hua showcases the survival state of ordinary people in the historical tide..."
- **Life Philosophy Reflections:** "The value of life lies not in its length, but in how we face life's challenges..."

**Suggestions:**
- Further read works related to existentialist philosophy to deepen understanding of life's meaning
- Try connecting this reading experience with your personal experiences to write deeper reflections
- Add this review to your reading notes as part of reading reflection

---
*Confidence: 87.5%*
*Generated at: 2026-03-07 20:15:30*
```

### Example 2: English Reading Insight
**Input:**
```
To Kill a Mockingbird teaches about courage and justice
```

**Output:**
```markdown
## 📚 Reading Insight Review

**Original Insight:** To Kill a Mockingbird teaches about courage and justice

**Expanded Review:**
Harper Lee's "To Kill a Mockingbird" masterfully explores themes of courage and justice through the eyes of young Scout Finch. As noted in your reading journal: "Atticus Finch's defense of Tom Robinson demonstrates moral courage in the face of social prejudice."

The novel teaches us that true courage isn't the absence of fear, but the willingness to do what's right despite fear. Justice, as portrayed in the book, is often imperfect but worth pursuing nonetheless.

**Related References:**
- **To Kill a Mockingbird Notes:** "The mockingbird symbolizes innocence - it's a sin to kill something that does no harm..."
- **Social Justice Reflections:** "Literature can be a powerful tool for understanding and promoting social justice..."

**Suggestions:**
- Compare with other works about social justice, such as "The Help" or "12 Angry Men"
- Reflect on how these themes relate to contemporary social issues
- Consider writing an essay connecting the novel's themes to real-world examples

---
*Confidence: 82.3%*
*Generated at: 2026-03-07 20:20:15*
```

## 🏗️ Architecture

### System Architecture
```
┌─────────────────────────────────────────────┐
│              User Interface Layer           │
│  • CLI Command Line Interface               │
│  • OpenClaw Skill Integration               │
│  • Web API Interface                        │
└─────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────┐
│              Skill Core Layer               │
│  • Configuration Management                 │
│  • Error Handling                           │
│  • Performance Monitoring                   │
└─────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────┐
│             Processing Engine Layer         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Parser  │ │ Search  │ │ Generate│       │
│  │ Module  │ │ Module  │ │ Module  │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│          │         │         │              │
│          └─────────┴─────────┘              │
│                   │                         │
│            ┌─────────────┐                  │
│            │Output Format│                  │
│            └─────────────┘                  │
└─────────────────────────────────────────────┘
```

### Core Modules

#### 1. Parser Module (`InsightParser`)
- Natural language processing to extract themes, sentiment, keywords
- Chinese and English language detection
- Text complexity assessment
- Chinese processing based on jieba segmentation

#### 2. Search Module (`NoteSearcher`)
- Multi-format note file support (Markdown, TXT)
- Smart indexing and fast search (Lunr.js)
- Relevance scoring and sorting
- Incremental index updates

#### 3. Generation Module (`ReviewGenerator`)
- DeepSeek API integration
- Context-aware generation
- Personalized reference integration
- Template fallback

#### 4. Output Module (`OutputFormatter`)
- Multi-format output (Markdown, Plain, HTML)
- Responsive design
- Metadata embedding
- Social media optimization

### Tech Stack
- **Runtime**: Node.js 18+
- **Language**: TypeScript 5.3
- **AI Integration**: DeepSeek API
- **Search Engine**: Lunr.js
- **File Processing**: fs-extra, glob
- **Testing**: Jest
- **Build Tools**: esbuild, TypeScript Compiler

## ⚙️ Configuration

### Configuration File
Create `config/local.json` for local configuration:
```json
{
  "processing": {
    "maxInputLength": 500,
    "defaultLanguage": "auto",
    "defaultStyle": "professional",
    "defaultLength": "medium"
  },
  "search": {
    "notePaths": [
      "~/Documents/Notes",
      "~/Obsidian",
      "~/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents"
    ],
    "indexUpdateInterval": 3600,
    "maxResults": 5,
    "minRelevanceScore": 0.3
  },
  "generation": {
    "aiProvider": "deepseek",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "maxTokens": 1000,
    "enableCache": true
  },
  "output": {
    "defaultFormat": "markdown",
    "includeReferences": true,
    "includeSuggestions": true,
    "enableCopyToClipboard": true
  }
}
```

### Environment Variables
```bash
# Required
DEEPSEEK_API_KEY=sk-your-api-key

# Optional
BOOK_REVIEW_NOTE_PATHS=~/Notes,~/Obsidian
BOOK_REVIEW_AI_MODEL=deepseek-chat
BOOK_REVIEW_TEMPERATURE=0.7
BOOK_REVIEW_LOG_LEVEL=info
BOOK_REVIEW_CACHE_DIR=~/.cache/book-review
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
npm test

# Run specific test
npm test -- parser

# With coverage report
npm test -- --coverage

# Watch mode
npm run test:watch
```

### Test Coverage
- ✅ Unit Tests: All core modules
- ✅ Integration Tests: End-to-end flows
- ✅ Error Handling: Edge cases and exceptions
- ✅ Performance Tests: Response time and resource usage

## 🤝 Contributing

### Development Setup
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# 2. Install dependencies
npm install

# 3. Development mode
npm run dev

# 4. Run tests
npm test
```

### Code Standards
- Use TypeScript strict mode
- Follow ESLint rules
- Use Prettier for code formatting
- Write complete type definitions
- Add JSDoc comments

### Commit Conventions
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Test related
- `chore`: Build process or auxiliary tool changes

### Release Process
1. Update `CHANGELOG.md`
2. Update version number (`package.json`)
3. Run tests to ensure everything works
4. Commit changes and create Git tag
5. Push to GitHub
6. Create Release

## 📄 License

This project is open sourced under the MIT License. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Technical Dependencies
- [OpenClaw](https://openclaw.ai) - Powerful AI assistant platform
- [DeepSeek](https://www.deepseek.com) - Excellent AI model service
- [Lunr.js](https://lunrjs.com) - Lightweight full-text search engine
- [Node.js](https://nodejs.org) - JavaScript runtime

### Inspiration
- Personal Knowledge Management (PKM) community
- Digital Garden movement
- Reading and writing enthusiasts

### Contributors
<a href="https://github.com/yourusername/openclaw-skill-book-review/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/openclaw-skill-book-review" />
</a>

## 📞 Support & Feedback

### Issue Reporting
- [GitHub Issues](https://github.com/yourusername/openclaw-skill-book-review/issues)
- Submit bug reports or feature requests

### Discussion
- [GitHub Discussions](https://github.com/yourusername/openclaw-skill-book-review/discussions)
- Share usage experience or make suggestions

### Documentation
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Tutorial](docs/tutorial.md)

---

<div align="center">

**Make every moment of reading resonate, give every thought depth**

⭐ If this project helps you, please give us a Star!

</div>