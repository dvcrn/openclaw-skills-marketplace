---
name: feishu-doc-writer
description: "飞书文档写入工具。用于解决飞书文档创建后内容为空的问题。正确流程：先用 create 创建文档（只有标题），再用 append 追加内容。支持 Markdown 格式自动转换。"
---

# 飞书文档写入工具

解决 feishu_doc 工具写入内容为空的问题。

## 重要发现

**直接用 create + content 参数会导致内容丢失！**

正确流程：
1. 先用 `create` 创建文档（只有标题）
2. 再用 `append` 追加内容

## 使用方法

### 方式一：使用 OpenClaw 内置工具

```python
# 第一步：创建文档（只有标题）
feishu_doc(action="create", title="文档标题", content="")

# 第二步：追加内容（重要！）
feishu_doc(action="append", doc_token="文档ID", content="实际内容")
```

### 方式二：使用 Python 脚本

```bash
python3 scripts/feishu_doc_writer.py "文档标题" "内容文件.md"
```

## 关键要点

1. **不要在 create 时传 content** — 会导致内容丢失
2. **先 create 再 append** — 分两步执行
3. **append 会自动渲染 Markdown** — 支持标题、列表、粗体等

## 示例代码

```python
# 创建文档（空内容）
doc = feishu_doc(
    action="create",
    title="我的报告",
    content=""
)
doc_id = doc["document_id"]

# 追加内容
feishu_doc(
    action="append",
    doc_token=doc_id,
    content="# 报告标题\n\n内容..."
)
```

## 常见问题

- **内容为空**：检查是否在 create 时传了 content
- **append 失败**：确保 doc_token 正确
- **格式不对**：append 支持 Markdown 自动转换
