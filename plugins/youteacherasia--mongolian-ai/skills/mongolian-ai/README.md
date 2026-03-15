# 蒙语 AI Skill

🤖 基于毅金云开放平台 API 的专业蒙古语 AI 服务

## 📖 简介

这是蒙语系列 AI 微信小程序的 ClawHub Skill 版本，提供：

- **蒙汉翻译** - 专业的蒙古语↔中文智能互译
- **传统蒙古文** - Unicode 蒙古文渲染和转换
- **文化问答** - 蒙古族文化、历史知识问答
- **小红书笔记生成** - 自动生成蒙古语主题的精美笔记

## 🚀 快速开始

### 1. 安装 Skill

```bash
clawhub install mongolian-ai
```

### 2. 获取 API Key

访问 [毅金云开放平台](https://platform.mengguyu.cn) 注册账号并获取 API Key

### 3. 配置环境变量

**方式一：临时设置**
```bash
export MENGGUYU_API_KEY="your_api_key_here"
```

**方式二：OpenClaw 配置**
```bash
openclaw configure --env MENGGUYU_API_KEY=your_api_key_here
```

**方式三：写入配置文件**
在 `~/.openclaw/workspace/memory/mengguyu-api.md` 中保存：
```
MENGGUYU_API_KEY=your_api_key_here
```

### 4. 验证安装

```bash
cd skills/mongolian-ai
node scripts/translate.js "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ" --from mn --to zh
```

## 📚 功能详解

### 1. 翻译功能

**Node.js 版本:**
```bash
# 蒙译汉
node scripts/translate.js "ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ" --from mn --to zh

# 汉译蒙
node scripts/translate.js "你好" --from zh --to mn

# 查看帮助
node scripts/translate.js --help
```

**Python 版本:**
```bash
# 蒙译汉
python3 scripts/translate.py "ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ" --from mn --to zh

# 汉译蒙
python3 scripts/translate.py "你好" --target mn
```

### 2. 文化问答

```bash
node scripts/culture-qa.js "蒙古族有哪些传统节日？"
node scripts/culture-qa.js "成吉思汗是谁？"
node scripts/culture-qa.js "那达慕大会是什么时候举办？"
```

### 3. 小红书笔记生成

```bash
# 生成默认主题
python3 scripts/xhs-generator.py --output ./output/

# 指定主题
python3 scripts/xhs-generator.py --topic "蒙古语翻译" --output ./notes/

# 只生成 Markdown，不渲染图片
python3 scripts/xhs-generator.py --topic "蒙语文化" --no-render
```

**生成的文件:**
- `cover.png` - 封面图片
- `card_1.png`, `card_2.png`... - 正文卡片
- `*.md` - Markdown 源文件

### 4. 发布到小红书

使用生成的图片，结合 xhs-note-creator 发布：

```bash
python3 /root/.openclaw/workspace/skills/xhs-note-creator/scripts/publish_xhs.py \
  --title "🤖 蒙语 AI - 传统蒙古文版" \
  --desc "专业的蒙古语翻译和文化问答工具！" \
  --images output/cover.png output/card_1.png output/card_2.png
```

## 🔧 API 配置

### 毅金云 API 端点

⚠️ **重要：** 以下 API 端点需要根据实际文档更新：

```javascript
// 在 scripts/translate.js 和 scripts/translate.py 中更新
const API_BASE = 'https://api.mengguyu.cn';  // TODO: 确认实际地址

// 翻译接口
POST /v1/translate
{
  "text": "待翻译文本",
  "from": "mongolian",
  "to": "chinese"
}

// 文化问答接口
POST /v1/culture/qa
{
  "question": "问题内容",
  "category": "culture"
}
```

### API 响应格式

请根据毅金云 API 文档更新以下字段解析：

```javascript
// translate.js 中
const result = JSON.parse(data);
return result.translatedText || result.text || result;
```

## 📁 目录结构

```
mongolian-ai/
├── SKILL.md                 # Skill 描述文件
├── README.md                # 本文件
├── requirements.txt         # Python 依赖
├── scripts/
│   ├── translate.js         # 翻译功能 (Node.js)
│   ├── translate.py         # 翻译功能 (Python)
│   ├── culture-qa.js        # 文化问答
│   └── xhs-generator.py     # 小红书笔记生成
└── assets/
    ├── fonts/               # 蒙古文字体（可选）
    ├── templates/           # 笔记模板（可选）
    └── images/              # Logo 等图片（可选）
```

## 🛠️ 开发说明

### 添加新功能

1. 在 `scripts/` 目录创建新脚本
2. 在 `SKILL.md` 中添加功能说明
3. 更新本 README

### 测试

```bash
# 测试翻译
node scripts/translate.js "测试" --from zh --to mn

# 测试文化问答
node scripts/culture-qa.js "测试问题"

# 测试笔记生成
python3 scripts/xhs-generator.py --topic "测试" --no-render
```

### 调试 API 调用

在脚本中添加日志输出：

```javascript
console.log('请求参数:', postData);
console.log('响应结果:', data);
```

## ⚠️ 注意事项

1. **API Key 安全**
   - 不要将 API Key 提交到 Git
   - 使用环境变量管理
   - 定期更换 Key

2. **API 限制**
   - 注意调用频率限制
   - 合理使用配额
   - 错误处理要完善

3. **蒙古文显示**
   - 需要支持 Unicode 的字体
   - 部分系统可能需要安装蒙古文字体
   - 终端可能无法正确显示竖排蒙古文

4. **依赖管理**
   - Node.js 版本 >= 14
   - Python 版本 >= 3.8
   - 需要安装 xhs-note-creator 用于笔记渲染

## 🤝 贡献

欢迎提交 Issue 和 PR！

### 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

- **微信小程序**: 搜索「蒙语 AI」
- **毅金云平台**: https://platform.mengguyu.cn
- **ClawHub**: https://clawhub.com

## 🙏 致谢

感谢：
- 毅金云开放平台提供 API 支持
- OpenClaw 团队提供 Skill 框架
- ClawHub 社区

---

**🎉 开始使用蒙语 AI Skill，让蒙古语服务更便捷！**
