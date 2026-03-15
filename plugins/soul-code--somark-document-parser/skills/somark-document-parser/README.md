# somark-document-parser

SoMark文档智能致力于不分场景的将PDF，图片等各种文档数据转化为统一的Markdown，Json标准结构化数据，旨在打破“准度-速度-成本不可能三角”，实现在超低硬件成本下以百毫秒级速度完成非结构数据的精准解析。让数据为大模型的训练及新一代RAG、智能Agent等应用场景做好准备。

## 安装

### 方式一：手动安装（推荐）

复制 `somark-document-parser/` 文件夹到：

- **全局（所有项目可用）**：`~/.openclaw/skills/`
- **仅当前项目**：`<workspace>/skills/`

### 方式二：通过 ClawHub CLI

```bash
npx clawhub@latest install somark-document-parser
```

## 配置

在 `~/.openclaw/openclaw.json` 中添加 API Key：

```json
{
  "skills": {
    "entries": {
      "somark-document-parser": {
        "enabled": true,
        "apiKey": "sk-YOUR_SOMARK_API_KEY"
      }
    }
  }
}
```

或者直接设置环境变量：

```bash
export SOMARK_API_KEY=sk-YOUR_SOMARK_API_KEY
```

## 获取 API Key

前往 [https://somark.tech](https://somark.tech) 注册账号并在控制台获取 API Key。

## 支持的文件格式

| 类型 | 格式 |
|------|------|
| 文档 | PDF、DOC、DOCX、PPT、PPTX |
| 图片 | PNG、JPG、JPEG、BMP、TIFF、WEBP、HEIC、HEIF、GIF 等 |

## 使用限制

- 单文件最大 200MB
- 单文件最多 300 页
- Beta 阶段每账号 QPS 为 1

## License

MIT
