---
name: mongolian-ai
description: "蒙语 AI - 蒙古语翻译、文化问答、语音文字处理。基于毅金云 API 提供专业蒙语服务。"
homepage: https://github.com/openclaw/workspace/tree/main/skills/mongolian-ai
---

# 蒙语 AI Skill

基于毅金云开放平台 API，提供专业蒙古语 AI 服务。

## 🎯 功能

- **蒙汉翻译** - 蒙古文↔中文智能互译
- **传统蒙古文** - Unicode 蒙古文渲染和转换
- **文化问答** - 蒙古族文化、历史知识问答
- **语音处理** - 语音↔文字转换（可选）

## 🚀 快速开始

### 1. 获取 API Key

访问 [毅金云开放平台](https://platform.mengguyu.cn) 注册并获取 API Key

### 2. 配置环境变量

```bash
export MENGGUYU_API_KEY="your_api_key_here"
```

或在 OpenClaw 中配置：
```bash
openclaw configure --env MENGGUYU_API_KEY=your_api_key_here
```

### 3. 使用翻译功能

```bash
# 蒙译汉
node scripts/translate.js --from mn --to zh "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ"

# 汉译蒙
node scripts/translate.js --from zh --to mn "你好"

# 使用 Python 脚本
python3 scripts/translate.py "你好" --target mn
```

### 4. 文化问答

```bash
node scripts/culture-qa.js "蒙古族有哪些传统节日？"
```

### 5. 生成小红书笔记

```bash
python3 scripts/xhs-generator.py --topic "蒙语 AI" --output ./output/
```

## 📁 目录结构

```
mongolian-ai/
├── SKILL.md                 # 本文件
├── README.md                # 详细文档
├── scripts/
│   ├── translate.js         # 翻译功能（Node.js）
│   ├── translate.py         # 翻译功能（Python）
│   ├── culture-qa.js        # 文化问答
│   ├── mongolian-render.py  # 蒙古文渲染
│   └── xhs-generator.py     # 小红书笔记生成
├── assets/
│   ├── fonts/               # 蒙古文字体
│   ├── templates/           # 笔记模板
│   └── images/              # Logo 等图片
└── requirements.txt         # Python 依赖
```

## 🔧 脚本说明

### translate.js / translate.py

蒙汉双向翻译

```bash
# 蒙译汉
node scripts/translate.js "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ" --from mn --to zh

# 汉译蒙
python3 scripts/translate.py "你好" --target mn
```

### culture-qa.js

蒙古族文化问答

```bash
node scripts/culture-qa.js "成吉思汗是谁？"
```

### xhs-generator.py

生成小红书笔记（整合 xhs-note-creator）

```bash
python3 scripts/xhs-generator.py --topic "蒙语翻译" --output ./output/
```

## 📝 示例

### 示例 1：翻译

```bash
$ node scripts/translate.js "ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ" --from mn --to zh
蒙古语
```

### 示例 2：文化问答

```bash
$ node scripts/culture-qa.js "蒙古族最大的节日是什么？"
蒙古族最大的节日是那达慕大会...
```

## ⚠️ 注意事项

1. 需要有效的毅金云 API Key
2. API 有调用频率限制，请注意合理使用
3. 蒙古文显示需要支持 Unicode 的字体

## 📚 相关资源

- [毅金云开放平台](https://platform.mengguyu.cn)
- [ClawHub](https://clawhub.com)
- [OpenClaw 文档](https://docs.openclaw.ai)

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
