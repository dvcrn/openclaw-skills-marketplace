#!/bin/bash
# Build with Public (bwp) - Simplified helper for codewithriver
# Usage: bwp <action> [options]

set -e

PROJECT_ROOT="/home/claw/codewithriver"
ACTION="${1:-help}"

show_help() {
    echo "Build with Public (bwp) - Technical Content Creation"
    echo ""
    echo "Usage:"
    echo "  bwp init                   # Initialize project with README.md"
    echo "  bwp article <title>        # Create new article"
    echo "  bwp course <name>          # Create new course outline"
    echo "  bwp theory <name>          # Create new theory/framework"
    echo "  bwp persona <name>         # Create new writing persona"
    echo "  bwp list                   # List all content"
    echo "  bwp commit [message]       # Commit changes to Git"
    echo "  bwp link <file>            # Generate shareable link"
    echo "  bwp status                 # Show project status"
    echo ""
    echo "Examples:"
    echo "  bwp init"
    echo "  bwp article \"AI Trends 2026\""
    echo "  bwp course \"OpenClaw Bootcamp\""
    echo "  bwp theory \"Writing Framework\""
    echo "  bwp persona \"Tech Expert\""
    echo "  bwp commit \"Add new article\""
    echo "  bwp link articles/bwp-2026-03-13-ai-trends-v1.md"
}

# Get today's date
get_date() {
    date +"%Y-%m-%d"
}

# Convert title to slug
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'
}

create_article() {
    local title="${1:-Untitled}"
    local slug=$(slugify "$title")
    local filename="bwp-$(get_date)-${slug}-v1.md"
    local filepath="$PROJECT_ROOT/articles/$filename"
    
    cat > "$filepath" << EOF
---
title: $title
date: $(get_date)
version: v1
---

# $title

## Introduction

Write your introduction here...

## Main Content

### Section 1

Content...

### Section 2

Content...

## Conclusion

Summary...

---

*Created with bwp on $(get_date)*
EOF
    
    echo "✅ Created: articles/$filename"
    echo "📝 Edit: $filepath"
}

create_course() {
    local name="${1:-New Course}"
    local slug=$(slugify "$name")
    local dir="$PROJECT_ROOT/courses/bwp-$slug"
    local filename="bwp-$(get_date)-${slug}-syllabus-v1.md"
    
    mkdir -p "$dir"
    
    cat > "$dir/syllabus-v1.md" << EOF
---
course: $name
date: $(get_date)
version: v1
---

# $name - Course Syllabus

## Overview

Brief description of the course...

## Learning Objectives

- Objective 1
- Objective 2
- Objective 3

## Course Outline

### Week 1: Foundation
- Topic 1
- Topic 2

### Week 2: Practice
- Topic 3
- Topic 4

### Week 3: Advanced
- Topic 5
- Topic 6

## Prerequisites

- Requirement 1
- Requirement 2

## Resources

- Resource 1
- Resource 2

---

*Created with bwp on $(get_date)*
EOF
    
    echo "✅ Created: courses/bwp-$slug/syllabus-v1.md"
    echo "📝 Edit: $dir/syllabus-v1.md"
}

create_theory() {
    local name="${1:-Framework}"
    local slug=$(slugify "$name")
    local filename="bwp-${slug}-v1.md"
    local filepath="$PROJECT_ROOT/theory/$filename"
    
    cat > "$filepath" << EOF
---
title: $name
date: $(get_date)
version: v1
---

# $name

## Core Principles

1. **Principle 1**: Description...
2. **Principle 2**: Description...
3. **Principle 3**: Description...

## Framework

### Step 1: Analysis

How to analyze...

### Step 2: Design

How to design...

### Step 3: Implementation

How to implement...

## Examples

### Example 1

Description...

### Example 2

Description...

## Best Practices

- Practice 1
- Practice 2
- Practice 3

---

*Created with bwp on $(get_date)*
EOF
    
    echo "✅ Created: theory/$filename"
    echo "📝 Edit: $filepath"
}

create_persona() {
    local name="${1:-Writer}"
    local slug=$(slugify "$name")
    local filename="bwp-${slug}-style-v1.md"
    local filepath="$PROJECT_ROOT/persona/$filename"
    
    cat > "$filepath" << EOF
---
persona: $name
date: $(get_date)
version: v1
---

# $name - Writing Style

## Voice

### Tone

- Professional yet approachable
- Direct and clear
- Occasional humor

### Language

- Simple over complex
- Specific over vague
- Active over passive

## Characteristics

### Strengths

1. **Strength 1**: Description...
2. **Strength 2**: Description...

### Weaknesses to Avoid

1. **Weakness 1**: Description...
2. **Weakness 2**: Description...

## Writing Guidelines

### Do's

- ✅ Guideline 1
- ✅ Guideline 2

### Don'ts

- ❌ Guideline 1
- ❌ Guideline 2

## Sample Phrases

### Openings

- "Direct conclusion..."
- "Here's a pitfall to watch..."

### Transitions

- "Essentially..."
- "From another angle..."

### Closings

- "Remember this principle..."
- "In practice..."

---

*Created with bwp on $(get_date)*
EOF
    
    echo "✅ Created: persona/$filename"
    echo "📝 Edit: $filepath"
}

init_project() {
    echo "🚀 Initializing Build with Public project..."
    echo ""
    
    # Create directory structure
    mkdir -p "$PROJECT_ROOT"/{articles,courses,theory,persona,images}
    
    # Create README.md
    cat > "$PROJECT_ROOT/README.md" << 'READMEEOF'
# codewithriver - Build with Public

技术内容创作与分享平台

---

## 📁 目录结构

```
codewithriver/
├── articles/      # 📄 技术文章和博客
├── courses/       # 📚 课程大纲和教程
├── theory/        # 📖 理论框架和方法论
├── persona/       # 🎭 写作人设和风格
├── images/        # 🖼️ 文章图片
├── server.py      # 🌐 Web 服务器
├── .env           # ⚙️ 环境配置
└── README.md      # 📋 本文件
```

---

## 📂 各目录详细说明

### 📄 articles/
**用途**：存放所有技术文章、博客、短文

**命名规范**：
```
bwp-YYYY-MM-DD-{topic}-v{version}.md
```

**示例**：
- `bwp-2026-03-13-ai-trends-v1.md`
- `bwp-2026-03-13-vibe-coding-v1.1.md`

**版本规则**：
- `v1`, `v1.1`, `v1.2`... - 小迭代
- `v2`, `v3`... - 大改版
- `-wechat`, `-xiaohongshu` - 平台适配版

---

### 📚 courses/
**用途**：存放课程大纲、教程、训练营资料

**结构**：
```
courses/
├── bwp-course-name/
│   ├── bwp-YYYY-MM-DD-course-name-syllabus-v1.md
│   └── ...
└── ...
```

**示例**：
- `courses/bwp-openclaw-bootcamp/`
- `courses/bwp-python-fundamentals/`

---

### 📖 theory/
**用途**：存放方法论、框架、最佳实践指南

**命名规范**：
```
bwp-{framework-name}-v{version}.md
```

**示例**：
- `bwp-writing-framework-v1.md`
- `bwp-content-strategy-v1.md`

**内容类型**：
- 写作方法论
- 技术框架
- 工作流程指南

---

### 🎭 persona/
**用途**：存放写作人设、风格定义、语言特征

**命名规范**：
```
bwp-{persona-name}-style-v{version}.md
```

**示例**：
- `bwp-tech-expert-style-v1.md`
- `bwp-mentor-voice-v1.md`

**内容类型**：
- 人设定义
- 语言风格指南
- 常用短语/句式
- 写作规范

---

### 🖼️ images/
**用途**：存放文章配图、图表、截图

**使用方式**：
- 在 Markdown 中引用：`![描述](images/filename.png)`
- 建议命名与对应文章相关

---

## 🚀 快速开始

### 创建新文章
```bash
bwp article "文章标题"
```

### 创建课程大纲
```bash
bwp course "课程名称"
```

### 创建理论框架
```bash
bwp theory "框架名称"
```

### 定义写作风格
```bash
bwp persona "人设名称"
```

### 查看项目状态
```bash
bwp status
```

### 生成分享链接
```bash
bwp link articles/bwp-2026-03-13-xxx-v1.md
```

---

## ⚙️ 环境配置

`.env` 文件配置：

```bash
# 服务器端口
PORT=12000

# 自定义域名（用于生成分享链接）
CUSTOM_DOMAIN=your-domain.com

# 访问认证
AUTH_USERNAME=user
AUTH_PASSWORD=your_password
```

---

## 🔧 常用命令

| 命令 | 说明 |
|:-----|:-----|
| `bwp list` | 列出所有内容 |
| `bwp commit "消息"` | 提交到 Git |
| `bwp link <文件>` | 生成分享链接 |
| `bwp status` | 查看项目状态 |

---

## 📝 工作流程

1. **创建内容** → 使用 `bwp` 命令创建文件
2. **编辑完善** → 使用你喜欢的编辑器修改
3. **提交保存** → `bwp commit "描述"`
4. **分享链接** → `bwp link <文件路径>`

---

## 🔒 安全说明

- 所有内容默认保存到 `/home/claw/codewithriver`
- Git 版本控制自动记录所有变更
- 通过 Web 服务器可安全分享内容

---

*Build with Public - 简化创作，专注内容 🚀*
READMEEOF
    
    echo "✅ Directory structure created"
    echo "✅ README.md created"
    echo ""
    echo "📁 Project structure:"
    echo "  articles/  - Technical articles and blog posts"
    echo "  courses/   - Course outlines and tutorials"
    echo "  theory/    - Frameworks and methodologies"
    echo "  persona/   - Writing personas and styles"
    echo "  images/    - Article images and diagrams"
    echo ""
    echo "Next steps:"
    echo "  1. Edit $PROJECT_ROOT/.env to configure your settings"
    echo "  2. Run 'bwp article \"Your First Article\"' to create content"
    echo "  3. Start server: cd $PROJECT_ROOT && python server.py"
}

list_content() {
    echo "📁 Content in codewithriver:"
    echo ""
    
    echo "📄 Articles ($(ls $PROJECT_ROOT/articles/*.md 2>/dev/null | wc -l)):"
    ls $PROJECT_ROOT/articles/*.md 2>/dev/null | xargs -n1 basename | head -10
    echo ""
    
    echo "📚 Courses ($(ls $PROJECT_ROOT/courses/ 2>/dev/null | wc -l)):"
    ls $PROJECT_ROOT/courses/ 2>/dev/null | head -10
    echo ""
    
    echo "📖 Theory ($(ls $PROJECT_ROOT/theory/*.md 2>/dev/null | wc -l)):"
    ls $PROJECT_ROOT/theory/*.md 2>/dev/null | xargs -n1 basename | head -10
    echo ""
    
    echo "🎭 Persona ($(ls $PROJECT_ROOT/persona/*.md 2>/dev/null | wc -l)):"
    ls $PROJECT_ROOT/persona/*.md 2>/dev/null | xargs -n1 basename | head -10
}

git_commit() {
    cd "$PROJECT_ROOT"
    
    local message="${1:-Update content}"
    
    git add -A
    
    if ! git diff --cached --quiet; then
        git commit -m "content: $message ($(get_date))"
        echo "✅ Committed: $message"
    else
        echo "ℹ️  No changes to commit"
    fi
}

generate_link() {
    local file="${1:-}"
    
    if [ -z "$file" ]; then
        echo "Usage: bwp link <filepath>"
        echo "Example: bwp link articles/bwp-2026-03-13-ai-trends-v1.md"
        return 1
    fi
    
    # Read server config from .env
    local port=$(grep PORT "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "12000")
    local custom_domain=$(grep CUSTOM_DOMAIN "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2 | tr -d '"')
    
    # Use CUSTOM_DOMAIN if set, otherwise fallback to localhost
    local hostname="${custom_domain:-localhost}"
    
    echo "🔗 Shareable Link:"
    echo "   http://${hostname}:${port}/${file}"
    echo ""
    echo "👤 Access credentials configured in .env"
    echo "   (Check $PROJECT_ROOT/.env for AUTH_USERNAME and AUTH_PASSWORD)"
}

show_status() {
    cd "$PROJECT_ROOT"
    
    echo "📊 Build with Public - Status"
    echo ""
    echo "📁 Project: codewithriver"
    echo "📍 Location: $PROJECT_ROOT"
    echo ""
    
    echo "📝 Recent commits:"
    git log --oneline -5 2>/dev/null || echo "  No commits yet"
    echo ""
    
    echo "📊 Content stats:"
    echo "  Articles: $(ls articles/*.md 2>/dev/null | wc -l) files"
    echo "  Courses: $(ls courses/ 2>/dev/null | wc -l) directories"
    echo "  Theory: $(ls theory/*.md 2>/dev/null | wc -l) files"
    echo "  Persona: $(ls persona/*.md 2>/dev/null | wc -l) files"
    echo ""
    
    # Server status
    if pgrep -f "server.py" > /dev/null; then
        echo "🟢 Server: Running"
    else
        echo "🔴 Server: Not running"
        echo "   Start with: cd $PROJECT_ROOT && python server.py"
    fi
}

# Main
case "$ACTION" in
    init|i)
        init_project
        ;;
    article|a)
        create_article "${2:-New Article}"
        ;;
    course|c)
        create_course "${2:-New Course}"
        ;;
    theory|t)
        create_theory "${2:-New Framework}"
        ;;
    persona|p)
        create_persona "${2:-New Persona}"
        ;;
    list|ls)
        list_content
        ;;
    commit|git)
        git_commit "${2:-Update content}"
        ;;
    link|url)
        generate_link "$2"
        ;;
    status|s)
        show_status
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
