---
name: xiaohongshu-commenter
description: "小红书视频评论助手。打开浏览器访问小红书视频链接，提取标题和正文，生成贴近作品的评论并自动发送。触发词：(1) \"分析评论小红书\"，(2) \"帮我去评论小红书\"，(3) \"评论小红书视频\" 后跟视频链接。"
---

# 小红书评论助手

自动分析小红书视频内容并生成评论。

## 工作流程

### 1. 提取视频链接

从用户消息中提取小红书视频链接，格式如：
- `https://www.xiaohongshu.com/explore/xxxxx`
- `https://www.xiaohongshu.com/discovery/item/xxxxx`
- `https://xhslink.com/xxxxx`（短链接）

### 2. 打开浏览器访问视频

使用 `browser` 工具控制用户电脑上的 Chrome 浏览器：
- `profile: "chrome"` — 使用用户现有的 Chrome 浏览器
- 打开视频链接

```javascript
browser action=open targetUrl="<视频链接>" profile="chrome"
```

**重要：** 用户需要先在 Chrome 浏览器标签页上点击 OpenClaw Browser Relay 扩展图标激活连接（badge 显示 ON）。

### 3. 提取作品信息

获取页面快照，提取标题和正文：

**标题选择器：** `#detail-title`
```html
<div id="detail-title" class="title">跟亲戚胡说八道简直太爽了吧！</div>
```

**正文选择器：** `#detail-desc` 或 `.note-text`
```html
<div id="detail-desc" class="desc">
  <span class="note-text">
    #搞笑 #过年 #内容过于真实 ...
  </span>
</div>
```

**提取方法：**
1. 获取页面 snapshot
2. 从 HTML 中解析 `#detail-title` 的文本内容作为标题
3. 从 `#detail-desc .note-text` 提取正文和标签

### 4. 生成评论内容

根据提取的标题和正文，生成 3-5 条贴近作品风格的评论建议：

**评论风格参考：**
- 幽默风：配合搞笑内容
- 共鸣型：表达认同感
- 互动型：引发讨论
- 标签呼应：结合话题标签

**示例：**
- 标题："跟亲戚胡说八道简直太爽了吧！"
- 标签：#搞笑 #过年
- 生成评论："哈哈哈哈太真实了，过年回家我也要试试这招！😂"

### 5. 发布评论

**步骤：**

1. **点击输入框** — 找到"说点什么"区域：
```html
<div class="inner">
  <span>说点什么...</span>
</div>
```

2. **输入评论** — 在评论输入框粘贴文本：
```html
<p id="content-textarea" contenteditable="true" class="content-input"></p>
```

3. **点击发送按钮**：
```html
<button class="btn submit"> 发送 </button>
```

**browser 操作序列：**
```
1. snapshot 获取页面状态
2. 点击"说点什么"区域
3. 在 #content-textarea 输入评论内容
4. 点击"发送"按钮
```

## 使用示例

**用户输入：**
```
帮我去评论小红书，视频链接为：https://www.xiaohongshu.com/explore/xxxxx
```

**执行流程：**
1. 提取链接
2. 打开 Chrome 访问该链接
3. 提取标题和正文
4. 生成评论："这内容太真实了，笑死我了 🤣"
5. 自动输入并发送

## 注意事项

1. **浏览器连接**：确保 Chrome 扩展已激活（badge ON）
2. **登录状态**：用户需已在浏览器登录小红书账号
3. **评论频率**：避免短时间内发送过多评论
4. **内容合规**：生成的评论需符合平台规范

## HTML 选择器参考

| 元素 | 选择器 |
|-----|-------|
| 标题 | `#detail-title` |
| 正文 | `#detail-desc` 或 `.note-text` |
| 评论入口 | `.inner` 包含 "说点什么" |
| 评论输入框 | `#content-textarea` |
| 发送按钮 | `button.btn.submit` |
| 标签 | `#hash-tag` 或 `.tag` |