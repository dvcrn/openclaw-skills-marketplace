---
name: obsidian-save-article
description: "Obsidian Save Article"
---

# obsidian-save-article

将网页文章保存到本地 Obsidian vault。

## 触发方式

当用户发送：
- 一个网页链接
- 可选的 notes 或 comments

例如：
- "https://example.com/article 这篇文章不错"
- "帮我保存这个：https://xxx.com 内容：我的笔记"

## 格式要求

保存到 Obsidian 的格式如下：

### YAML Frontmatter (开头)
```yaml
---
title: "文章标题"
url: "原始链接"
created: "YYYY/MM/DD"
pagecomment: "用户添加的页面评论"
---
```

### 全文内容 (折叠的 Callout)
```
> [!note]- 📄 Full Article
> 文章第一段内容...
> 文章第二段内容...
```

### 用户 Notes (引用块)
```
> 用户笔记内容
^note-xxx
```

## 执行步骤

1. **解析输入**: 从用户消息中提取 URL 和 notes
2. **抓取网页**: 
   - 优先使用 Jina.ai Reader: `https://r.jina.ai/<URL>`
   - 如果失败，使用 `web_fetch` 工具
   - X (Twitter) 链接必须用 Jina.ai Reader
3. **提取标题**: 从页面中提取标题（`<title>` 或 `<h1>`）
4. **生成文件名**: 标题作为文件名
   - 特殊字符 `<>:"|?*` 替换为 `-`
   - 空格替换为 `-`
5. **构建内容**: 
   - 生成 YAML frontmatter（title, url, created, pagecomment）
   - 清理全文内容：
     - 限制 50000 字符，超出部分截断并添加 `[...内容已截断...]`
     - 去除零宽字符：`\u200B\u200C\u200D\uFEFF`
     - 去除其他控制字符
   - 将 notes 转为 block quote 格式，每条 note 生成唯一 block reference
6. **保存到本地**: 
   - 默认路径：`~/Documents/Obsidian Vault/Collections/`
   - 文件名：标题作为文件名（安全处理特殊字符）
   - 如果文件已存在（通过 URL 判断），则替换对应块

## 关键代码逻辑

### 生成 Block Reference ID
```javascript
function generateBlockReferenceId(noteText, url) {
  const hash = simpleHash(`${url}|${noteText}`.toLowerCase());
  return `note-${hash}`;
}

function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(36);
}
```

### 清理特殊字符
```javascript
function cleanSpecialCharacters(text) {
  return text
    .replace(/[\u200B\u200C\u200D\uFEFF]/g, '')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
    .replace(/[\u00A0\u1680\u180E\u2000-\u200A\u202F\u205F\u3000]/g, ' ')
    .replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069]/g, '')
    .replace(/[\uE000-\uF8FF]/g, '')
    .replace(/  +/g, ' ');
}
```

### 生成 Foldable Callout
```
> [!note]- 📄 Full Article (max 50000 chars)
> 第一行
> 第二行
> ...
```

## 注意事项

- **Jina.ai Reader**: 免费网页抓取服务，URL 格式: `https://r.jina.ai/<原始URL>`
  - X (Twitter) 链接必须用此方式: `https://r.jina.ai/https://x.com/...`
  - 微信公众号链接也可用: `https://r.jina.ai/https://mp.weixin.qq.com/...`
- 文件名中的特殊字符需要处理
- 页面内容超过 50000 字符时需要截断
- 需要清理零宽字符等破坏格式的特殊字符
- 每个 note 需要生成唯一的 block reference ID
- 通过 URL 判断是否已有对应内容块，有则替换、无则追加

## 示例

用户输入：
```
https://example.com/article 我的笔记：这篇文章讲了三件事
```

输出保存到 Obsidian：
```yaml
---
title: "Example Article"
url: "https://example.com/article"
created: "2026/03/04"
pagecomment: ""
---

> [!note]- 📄 Full Article (max 50000 chars)
> Article content here...

> 我的笔记：这篇文章讲了三件事
^note-abc123
```
