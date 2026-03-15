---
name: nima-skill-creator
description: "Hybrid skill creation framework combining interactive Chinese-guided workflows with English technical documentation. Use when users want to create, update, or improve Claude skills with guided requirement discovery and standardized implementation."
---

# Nima Skill Creator

## Overview

A professional skill creation framework that bridges the gap between user需求 discovery and technical implementation.

## Core Features

### 1. 双语引导 (Dual-Language Guidance)
- **交互阶段**: 中文引导用户需求挖掘
- **技术阶段**: 英文标准文档和最佳实践

### 2. 渐进式披露 (Progressive Disclosure)
```
Level 1: Trigger metadata (name + description)
  ↓ (on trigger)
Level 2: SKILL.md body (<5k words)
  ↓ (on demand)
Level 3: Bundled resources (unlimited)
```

## Workflow

### 阶段 1: 需求挖掘 (Discovery)
```
用户输入 → 交互式提问 → 技术规范输出
```

关键问题:
- Claude 应该**输入**什么？
- Claude 应该**输出**什么？
- 用户会**怎么说**来触发 Skill？

### 阶段 2: 架构蓝图 (Blueprint)
```
规范 → 目录结构 → 资源规划
```

输出:
- 目录结构 (scripts/, references/, assets/)
- 资源清单
- 工作流逻辑

### 阶段 3: 实现 (Implementation)
```
蓝图 → 代码/文档 → 验证 → 打包
```

## 技术标准 (Technical Specifications)

### 目录结构
```
skill-name/
├── SKILL.md              # Required (frontmatter + body)
├── scripts/              # Optional (executable code)
├── references/           # Optional (loaded on demand)
└── assets/               # Optional (output resources)
```

### SKILL.md 格式
```yaml
---
name: skill-name-here         # lowercase-hyphen-case, <64 chars
description: <1024 chars>     # Trigger scenarios + functionality
---
```

### 命名规范
- ✅ `processing-pdfs`, `analyzing-spreadsheets`
- ❌ `helper`, `utils`, `tools`

## Here are 3 example Skill usage scenarios:

### Scenario 1: PDF Processing Skill
**Trigger**: "Help me extract text and tables from PDFs"
**Workflow**:
1. Discover: Input (PDF files), Output (extracted text/tables)
2. Blueprint: `scripts/extract_pdf.py`, `references/pdf-libraries.md`
3. Implement: Create script + reference docs

### Scenario 2: Image Editor Skill
**Trigger**: "Edit images for my presentations"
**Workflow**:
1. Discover: Input (image files), Output (edited images)
2. Blueprint: `scripts/edit_image.py`, `assets/templates/`
3. Implement: Create editing script + templates

### Scenario 3: API Integration Skill
**Trigger**: "Connect Claude to my Notion workspace"
**Workflow**:
1. Discover: Input (Notion API data), Output (structured results)
2. Blueprint: `scripts/notion_api.py`, `references/notion-schema.md`
3. Implement: Create API client + schema docs

## Best Practices

### 简洁至上 (Conciseness)
- Claude 已经很聪明 → only add non-obvious context
- 每个 token 都要问: "Does Claude really need this?"

### 自由度匹配 (Freedom Matching)
| Freedom Level | Use Case | Example |
|--------------|----------|---------|
| High | Multiple valid approaches | Code review workflow |
| Medium | Preferred pattern, some variation | Configurable scripts |
| Low | Fragile operations, consistency critical | Database migrations |

### 渐进式披露 (Progressive Disclosure)
- SKILL.md body: <500 lines, essentials only
- Detailed content: references/ files
- No deeply nested references: one level deep only
- Long files: include table of contents

## Validation Rules

### Required
- ✅ SKILL.md exists with valid YAML frontmatter
- ✅ name: lowercase-hyphen-case, <64 characters
- ✅ description: includes functionality + trigger scenarios

### Recommended
- 📝 scripts/ for executable code
- 📚 references/ for detailed documentation
- 🎨 assets/ for reusable templates

### Avoid
- ❌ README.md, INSTALLATION_GUIDE.md, etc.
- ❌ Deeply nested references
- ❌ Duplicate information across files

## For Implementation

See `references/` for detailed technical guides:
- `best-practices.md` - Naming, patterns, quality checklist
- `workflows.md` - Multi-step process templates
- `output-patterns.md` - Output format templates
- `interaction-guide.md` - Interactive design patterns (Chinese)

## For Agents

When this skill is triggered, the AI should:

1. Present the interactive discovery questions (Chinese) - see `references/interaction-guide.md`
2. Generate the technical blueprint (English)
3. Execute initialization scripts from `scripts/`
4. Guide implementation with referenced best practices
5. Validate with `scripts/validate_skill.py`
6. Package with `scripts/package_skill.py`
