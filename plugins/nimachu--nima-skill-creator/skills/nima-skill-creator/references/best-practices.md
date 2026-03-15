# Best Practices for Skill Creation

## 命名规范 (Naming Conventions)

### Skill Name
- ✅ **Use**: lowercase letters, digits, hyphens only
- ✅ **Recommended**: verb-noun format (e.g., `processing-pdfs`)
- ✅ **Maximum**: 64 characters

### Bad Examples
- ❌ `MySkill` (camelCase)
- ❌ `skill_name` (snake_case)
- ❌ `skill!` (special characters)
- ❌ `helper`, `utils`, `tools` (too vague)

### Good Examples
- ✅ `processing-pdfs`
- ✅ `analyzing-spreadsheets`
- ✅ `nima-skill-creator`

## Description 编写指南 (Description Writing Guide)

### 原则 (Principles)
1. **第三人称** (Third person)
   - ✅ "Process Excel files"
   - ❌ "I help you process Excel files"

2. **包含触发场景** (Include trigger scenarios)
   - ❌ "Handle PDF files"
   - ✅ "Extract text and tables from PDF files. Trigger when user mentions PDF, forms, document extraction"

3. **完整描述** (Complete description)
   - ✅ "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when working with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

## 简洁原则 (Conciseness Principles)

### Question Each Element
Ask: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

### Pre-assume Intelligence
- Claude 已经很Smart → only add non-obvious context
-不要解释基本概念 →除非 for very specific workflows

### Prefer Examples Over Explanations
- ✅ Short code example
- ❌ Long paragraph explaining code

## 自由度匹配 (Freedom Matching)

### 高自由度 (High Freedom)
- **Use**: Multiple valid approaches, context-dependent decisions
- **Example**: Code review workflow

### 中等自由度 (Medium Freedom)
- **Use**: Preferred pattern with some variation, configurable behavior
- **Example**: Scripts with parameters

### 低自由度 (Low Freedom)
- **Use**: Fragile operations, consistency critical, specific sequence required
- **Example**: Database migrations

## 渐进式披露 (Progressive Disclosure)

### 三级加载系统 (Three-Level Loading)

```
Level 1: Metadata (name + description)
  → Always in context (~100 words)

Level 2: SKILL.md Body
  → When skill triggers (<5k words)

Level 3: Bundled Resources
  → As needed by Claude (unlimited)
```

### 模板 (Patterns)

#### Pattern 1: High-level guide with references
```markdown
# PDF Processing

## Quick start
Extract text with pdfplumber:
[code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
```

#### Pattern 2: Domain-specific organization
```
bigquery-skill/
├── SKILL.md (overview)
└── references/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

#### Pattern 3: Conditional details
```markdown
# DOCX Processing

## Creating documents
Use docx-js for new documents.

## Editing documents
For simple edits, modify XML directly.

**For tracked changes**: See [REDLINING.md]
**For OOXML details**: See [OOXML.md]
```

## 反模式 (Anti-Patterns)

### ❌ 复杂性伪装为不确定性 (Confusing complexity with uncertainty)
- Wrong: "可能需要...也可能是..."
- Right: "Use X because Y, but switch to Z when A"

### ❌ apsulation 信息 (Not encapsulating information)
- Wrong: Repeat same explanation in multiple places
- Right: Single source of truth in references/

### ❌ 嵌套过深 (Too deep nesting)
- Wrong: SKILL.md → ref1.md → ref2.md → ref3.md
- Right: SKILL.md → ref1.md, SKILL.md → ref2.md

### ❌ 冗余文件 (Redundant files)
- Wrong: SKILL.md + README.md + QUICK_REFERENCE.md
- Right: SKILL.md only (no auxiliary documentation)

### ❌ 技术术语过度 (Overusing technical jargon)
- Wrong: "REST API vs GraphQL"
- Right: "方案A: 直接读取文件 / 方案B: 连接在线服务"

## 质量检查清单 (Quality Checklist)

### 功能完整性 (Functionality)
- [ ] Skill triggers correctly
- [ ] Output matches expected format
- [ ] Handles edge cases

### 技术标准 (Technical Standards)
- [ ] YAML frontmatter valid
- [ ] Name follows naming conventions
- [ ] Description includes triggers
- [ ] Directory structure complete

### 可维护性 (Maintainability)
- [ ] No duplication
- [ ] One source of truth
- [ ] Clear references
- [ ] No deeply nested files

### 用户友好 (User-Friendly)
- [ ] Chinese descriptions for non-technical users
- [ ] English for technical standards
- [ ] Clear examples
- [ ] Error messages helpful
