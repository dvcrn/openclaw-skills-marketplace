---
name: podcast-production-pipeline
description: "端到端播客制作流程 - 从话题研究、嘉宾调研、大纲生成到后期制作（节目笔记、社交媒体、精华片段），自动化整个播客生产周期"
---

# 🎙️ Podcast Production Pipeline

完整的播客制作流程，从前期研究到后期发布，自动化整个生产周期。

## ✨ 功能特性

### 📋 前期制作 (Pre-Production)

**录制前自动完成**:
- ✅ **嘉宾研究** - 背景、成就、公开观点、争议话题
- ✅ **话题研究** - 趋势、新闻、常见误解、受众知识
- ✅ **节目大纲** - 开场白、采访问题、备用问题、结束语
- ✅ **采访策略** - 从建立融洽感到深度探讨的渐进式问题

### 🎬 后期制作 (Post-Production)

**录制后自动生成**:
- ✅ **节目笔记** - 时间戳、关键点、资源链接
- ✅ **SEO 描述** - Spotify、Apple Podcasts、YouTube 优化
- ✅ **社交媒体包** - Twitter/X、LinkedIn、Instagram 帖子
- ✅ **精华片段** - 适合短视频/转发的 3 个片段

## 🚀 使用方法

### 1️⃣ **前期制作**（录制前）

```bash
cd /Users/xufan65/.openclaw/workspace/scripts

# 研究话题 + 嘉宾 + 生成大纲
node podcast-pre-production.cjs 42 "AI Agent发展现状" "张三"
```

**生成文件**:
- `episodes/ep42/prep/outline.md` - 完整节目大纲
- `episodes/ep42/prep/research.md` - 研究资料

---

### 2️⃣ **后期制作**（录制后）

```bash
# 生成节目笔记 + 社交媒体 + 精华片段
node podcast-post-production.cjs 42 transcript.txt

# 或仅生成模板
node podcast-post-production.cjs 42
```

**生成文件**:
- `episodes/ep42/publish/show-notes.md` - 节目笔记
- `episodes/ep42/publish/description.md` - SEO 描述
- `episodes/ep42/publish/social-media.md` - 社交媒体帖子
- `episodes/ep42/publish/highlights.md` - 精华片段

---

## 📁 文件结构

```
podcast/
├── config/
│   └── podcast-pipeline.json      # 配置文件
├── scripts/
│   ├── podcast-pre-production.cjs # 前期制作脚本
│   └── podcast-post-production.cjs # 后期制作脚本
└── episodes/
    └── ep42/
        ├── prep/
        │   ├── outline.md         # 节目大纲
        │   └── research.md        # 研究资料
        └── publish/
            ├── show-notes.md      # 节目笔记
            ├── description.md     # SEO 描述
            ├── social-media.md    # 社交媒体帖子
            └── highlights.md      # 精华片段
```

---

## 🎯 典型工作流程

### **场景 1: 新一期播客准备**

**用户**: "我要录制第 42 期，话题是 AI Agent，嘉宾是张三"

**自动执行**:
1. ✅ 研究张三背景
2. ✅ 研究 AI Agent 趋势
3. ✅ 生成 7 个采访问题
4. ✅ 准备 3 个备用问题
5. ✅ 生成开场白和结束语

**输出**: `ep42/prep/outline.md`

---

### **场景 2: 录制完成，准备发布**

**用户**: "第 42 期录制完成，生成发布材料"

**自动执行**:
1. ✅ 解析转录文本
2. ✅ 生成时间戳笔记
3. ✅ 写 SEO 优化描述
4. ✅ 创建 Twitter/LinkedIn/Instagram 帖子
5. ✅ 提取 3 个精华片段

**输出**: `ep42/publish/*` (4 个文件)

---

## 🔧 配置

编辑 `config/podcast-pipeline.json`:

```json
{
  "podcast_name": "你的播客名称",
  "host_name": "你的名字",
  "discord_channel": "Discord频道ID",
  "apis": {
    "tavily": "tvly-dev-xxx",
    "gemini": "AIzaSyxxx",
    "elevenlabs": "sk_xxx"
  }
}
```

---

## 💡 高级用法

### **多嘉宾**

```bash
node podcast-pre-production.cjs 43 "技术管理" "张三,李四,王五"
```

### **竞品监控**（可选）

创建 `scripts/competitor-monitor.cjs`:

```javascript
// 监控竞品播客 RSS
// 当新节目发布时自动通知
```

---

## 🎊 集成 Discord

所有输出会自动发送到配置的 Discord 频道：

- ✅ 前期制作完成 → 发送大纲链接
- ✅ 后期制作完成 → 发送发布包
- ✅ 格式化为 Discord 消息（包含 @mentions）

---

## 📊 效率提升

| 任务 | 传统方式 | 使用 Pipeline | 节省时间 |
|------|---------|--------------|----------|
| **嘉宾研究** | 2-3 小时 | 5 分钟 | ⬇️ 95% |
| **大纲生成** | 1-2 小时 | 2 分钟 | ⬇️ 95% |
| **节目笔记** | 30-60 分钟 | 3 分钟 | ⬇️ 90% |
| **社交媒体** | 1-2 小时 | 5 分钟 | ⬇️ 95% |
| **总计** | **5-8 小时** | **15 分钟** | **⬇️ 95%** |

---

## 📝 示例输出

### **节目大纲片段**

```markdown
## 🎙️ 采访问题 (5-7个)

### 开场问题
1. 能不能先介绍一下你自己，你是怎么进入 AI Agent 领域的？

### 核心问题
2. 关于 AI Agent，你觉得目前最大的误解是什么？
3. 在你的职业生涯中，有没有遇到特别相关的经历？
4. 你认为未来 12-18 个月，AI Agent 会有什么变化？
5. 对于我们的听众，你有什么实用的建议？

### 深度问题
6. 有没有哪个观点是你觉得被过度吹捧或低估的？
7. 如果你要预测 3 年后的情况，会是什么样？
```

---

## 🔗 相关链接

- [Podcast RSS Feed Spec](https://podcasters.apple.com/support/823-podcast-requirements)
- [Spotify for Podcasters](https://podcasters.spotify.com/)
- [Transistor](https://transistor.fm/)
- [Buzzsprout](https://www.buzzsprout.com/)

---

**安装时间**: 2026-03-11  
**版本**: 1.0.0  
**作者**: OpenClaw Community
