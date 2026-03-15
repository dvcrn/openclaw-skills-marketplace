---
name: wechat-formatter
description: "将 Markdown 文章转换为微信公众号编辑器粘贴格式，保留段落层次和基础格式（加粗、列表、代码块）。使用于需要快速发布文章到公众号的场景。"
---

# 微信公众号格式化工具

## Features
- 去除 Markdown 语法，保留段落结构
- `**加粗**` → `【加粗】`
- `*斜体*` → `斜体`（去掉星号）
- 标题转换为缩进段落
- 列表转换为带圆点格式
- 代码块标记为 `【代码块】`
- 纯文本输出，可直接复制到公众号

## Installation

已安装到 `~/.openclaw/skills/wechat-formatter/`

## Usage

### 格式化文件
```bash
wechat-formatter article.md
```

### 通过管道
```bash
cat article.md | wechat-formatter --stdin
```

### 结合第五篇日记
```bash
wechat-formatter ~/.openclaw/workspace/memory/2026-03-09-day2.md | pbcopy
```

## Example

**Input** (`test.md`):
```markdown
# 标题

这是**加粗**和*斜体*。

- 列表1
- 列表2
```

**Output**:
```
标题

这是【加粗】和斜体。

• 列表1
• 列表2
```

## 为什么需要这个？

公众号编辑器不支持 Markdown 语法，直接粘贴会丢失格式。这个工具帮你转换成**纯文本但保留排版层次**的格式，粘贴后不需要再调整。

## Integration

也可以在其他技能中调用：
```python
from wechat_formatter import format_for_wechat
formatted = format_for_wechat(markdown_content)
```

## License

MIT