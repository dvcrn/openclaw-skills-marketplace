# Nima Skill Creator

A hybrid skill creation framework combining interactive Chinese-guided workflows with English technical documentation.

## Project Structure

```
nima-skill-creator/
├── SKILL.md                    # Main skill definition (hybrid Chinese+English)
├── PROJECT.md                  # This file - project overview
├── scripts/                    # Initialization and validation tools
│   ├── init_skill.py          # Initialize new skill project
│   ├── validate_skill.py      # Validate skill structure
│   └── package_skill.py       # Package skill for distribution
├── references/                 # Technical specifications and templates
│   ├── best-practices.md      # Naming conventions, patterns, quality checklist
│   ├── workflows.md           # Multi-step process patterns
│   ├── output-patterns.md     # Output format templates
│   └── interaction-guide.md   # Interactive design patterns (Chinese)
├── assets/                     # Templates and examples
│   ├── template-skill/        # Starter kit for new skills
│   └── examples/              # Real-world examples by domain
├── README.md                   # Project overview
└── .gitignore                 # Git ignore rules
```

## Core Features

### 1. Dual-Language Guidance
- **Interactive Phase**: Chinese (老板视角)
- **Technical Phase**: English (技术标准)

### 2. Progressive Disclosure
```
Level 1: Trigger metadata (name + description)
  ↓ (on trigger)
Level 2: SKILL.md body (<5k words)
  ↓ (on demand)
Level 3: Bundled resources (unlimited)
```

### 3. Interactive Workflow
```
Phase 1: 需求挖掘 (Discovery)
  └─ User input → Interactive questions → Technical spec

Phase 2: 架构蓝图 (Blueprint)
  └─ Specification → Directory structure → Resource plan

Phase 3: 实现 (Implementation)
  └─ Blueprint → Code/Docs → Validation → Package

Phase 4: 测试与迭代 (Validation & Iteration)
  └─ Test cases → User feedback → Iterate → Final skill
```

## Workflow

### 阶段 1: 需求挖掘 (Discovery)
```
用户输入 → 交互式提问 → 技术规范输出
```

关键问题 (用中文):
- Claude 应该**输入**什么？
- Claude 应该**输出**什么？
- 用户会**怎么说**来触发 Skill？

### 阶段 2: 架构蓝图 (Blueprint)
```
Specification → Directory structure → Resource plan
```

Output (用英文):
- Directory structure (scripts/, references/, assets/)
- Resource checklist
- Workflow logic

### 阶段 3: 实现 (Implementation)
```
Blueprint → Code/Docs → Validation → Package
```

### 阶段 4: 测试与迭代 (Validation & Iteration)
```
Test cases → User feedback → Iterate → Final skill
```

## Best Practices

### 简洁至上 (Conciseness)
- Claude 已经很Smart → only add non-obvious context
- 每个 token 都要问: "Does Claude really need this?"

### 自由度匹配 (Freedom Matching)
| Freedom Level | Use Case | Example |
|--------------|----------|---------|
| High | Multiple valid approaches | Code review workflow |
| Medium | Preferred pattern, some variation | Configurable scripts |
| Low | Fragile operations | Database migrations |

### 渐进式披露 (Progressive Disclosure)
- SKILL.md body: <500 lines, essentials only
- Detailed content: references/ files
- No deeply nested references: one level deep only
- Long files: include table of contents

## Template

Start with `assets/template-skill/` for new skills.

## Examples

See `assets/examples/` for real-world examples.

## Usage

1. Review this PROJECT.md (中文)
2. Read SKILL.md for the complete workflow (hybrid Chinese+English)
3. Follow the interactive discovery process (Chinese) - see references/interaction-guide.md
4. Review technical specifications (English) - see references/
5. Implement using provided scripts in scripts/
6. Validate and package

## For AI Agents

When this skill is triggered, the AI should:

1. Present the interactive discovery questions (Chinese) - see references/interaction-guide.md
2. Generate the technical blueprint (English)
3. Execute initialization scripts from scripts/
4. Guide implementation with referenced best practices
5. Validate with scripts/validate_skill.py
6. Package with scripts/package_skill.py

## License

MIT License - See LICENSE file for details
