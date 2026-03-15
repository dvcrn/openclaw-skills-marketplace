---
name: smart-model-switch
description: "智能模型自动切换。根据消息复杂度和文件类型自动选择最优模型（Flash/Main/Coding/Vision/Complex），提升响应质量和效率。Trigger on \"模型切换\", \"智能模型\", \"自动选择模型\", \"model switch\"。"
---

# 智能模型切换技能

根据消息复杂度、文件类型、关键词、代码特征等自动选择最优模型，实现无感知的模型切换。

## 🎯 核心特性

### ⭐ 智能分析
- ✅ **消息复杂度评分**：0-10分，简单→复杂
- ✅ **文件类型检测**：视频、图片、文档、代码等自动识别
- ✅ **特征检测**：代码、视觉、长文本、关键词
- ✅ **多维度评估**：长度（30%）+ 关键词（40%）+ 代码（20%）+ 视觉（10%）

### ⭐ 自动选择
- ✅ **Flash模型**（0-3分）：简单问答、快速查询
- ✅ **Main模型**（4-6分）：常规对话、分析任务
- ✅ **Coding模型**：代码相关任务
- ✅ **Vision模型**：图片、截图、视频分析
- ✅ **Complex模型**（8-10分）：深度分析、架构设计、文档处理
- ✅ **Long-Context模型**：超长上下文对话（256k窗口）

### ⭐ 无感切换
- ✅ 用户无需关心模型选择
- ✅ 自动优化响应质量和速度
- ✅ 节省Token成本

## 📊 模型选择规则

### 优先级顺序
1. **文件类型**（最高优先级）
2. **消息特征**（视觉/代码关键词）
3. **复杂度评分**（长度/关键词）
4. **默认模型**（GLM-5）

### 文件类型映射
| 文件类型 | 扩展名 | 推荐模型 |
|----------|--------|----------|
| 视觉文件 | .jpg, .png, .mp4, .avi... | Vision |
| 代码文件 | .js, .py, .java, .html... | Coding |
| 文档文件 | .pdf, .docx, .pptx... | Complex |
| 文本文件 | .txt, .md, .csv | Main |

### 策略2：上下文监控切换 ⭐

**核心机制**：
- 监控上下文使用率（每10分钟）
- 连续2次超过85%阈值 → 自动提醒
- 目标模型：Kimi长上下文（256k窗口）
- 冷却期：切换后10分钟内不再切换

## 🚀 使用方式

### 1. 安装技能

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/smart-model-switch

# 运行安装脚本
bash install.sh

# 或从ClawHub安装
clawhub install smart-model-switch
```

### ⭐ AI主动检测机制（v1.3增强版）⭐⭐⭐⭐⭐

**每次回复前自动检查上下文使用率、消息特征和文件类型**

#### 自动集成（推荐）

**AI行为规则（强制）：**
```bash
# 在每次回复前执行（在生成回复内容之前）
~/.openclaw/workspace/skills/smart-model-switch/scripts/integrate-check.sh
```

### 2. 增强版分析

```bash
# 消息 + 文件双分析
./scripts/smart-switch-enhanced.sh "分析这个视频" "/path/to/video.mp4"

# 输出示例
{
  "fileType": "vision",
  "selectedModel": "aihubmix/gemini-3.1-flash-image-preview-free"
}
```

## 🛠️ 技术实现

### v1.3.0 新增功能
- ✅ **文件类型分析**：`analyze-file-type.js`
- ✅ **增强切换脚本**：`smart-switch-enhanced.sh`
- ✅ **完整文件映射**：config中的file_type_mapping
- ✅ **优先级系统**：文件 > 消息 > 默认

### 支持的文件类型
- **视觉文件**：.jpg, .jpeg, .png, .gif, .webp, .bmp, .tiff, .mp4, .avi, .mov, .mkv, .webm
- **代码文件**：.js, .jsx, .ts, .tsx, .py, .java, .cpp, .c, .html, .css, .json, .xml, .yaml, .yml  
- **文档文件**：.pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx
- **文本文件**：.txt, .md, .csv

## 📁 文件结构

```
smart-model-switch/
├── SKILL.md                          # 技能文档
├── README.md                         # 使用说明
├── RELEASE-NOTES.md                  # 发布说明（v1.3.0）
├── package.json                      # ClawHub发布配置
├── install.sh                        # 安装脚本
├── config/
│   └── model-rules.json              # 完整模型规则配置 ⭐
├── scripts/
│   ├── analyze-complexity.js         # 消息复杂度分析
│   ├── analyze-file-type.js          # 文件类型分析 ⭐
│   ├── smart-switch-enhanced.sh      # 增强切换脚本 ⭐
│   ├── integrate-check.sh            # AI主动检测集成
│   ├── ai-proactive-check.sh         # 主动检测主逻辑
│   └── 其他工具脚本...
└── data/
    └── context-state.json            # 上下文状态追踪
```

## 💡 核心优势

### v1.3.0 增强功能
- ✅ **文件类型支持**：直接发送的视频、图片、文档自动检测
- ✅ **智能优先级**：文件类型优先于消息内容分析
- ✅ **全覆盖支持**：视觉/代码/文档/文本文件完整支持
- ✅ **无感体验**：用户发送任何文件，系统自动选择最优模型

### 双策略优势 ⭐
- ✅ **快速响应**：消息复杂度分析（毫秒级）
- ✅ **文件智能**：自动识别文件类型并选择模型
- ✅ **长期保护**：上下文监控（避免超限）
- ✅ **三重保障**：文件+消息+上下文，覆盖所有场景

## 📝 使用示例

### 场景1：直接发送视频
```
用户：[发送 video.mp4]
AI：[检测.mp4扩展名] → Vision模型 → 视频分析
```

### 场景2：直接发送PDF
```
用户：[发送 report.pdf]  
AI：[检测.pdf扩展名] → Complex模型 → 文档分析
```

### 场景3：发送代码文件
```
用户：[发送 app.js]
AI：[检测.js扩展名] → Coding模型 → 代码审查
```

### 场景4：长对话保护
```
对话进行中...
第1次检查：上下文85% → 记录1次
第2次检查：上下文87% → 记录2次 → 触发提醒
AI：【AI主动提醒】上下文使用率已达87%...
```

---

*智能模型切换技能 v1.3.0*
*让模型选择完全自动化，优化每一条消息的响应质量*
*版本：1.3.0（文件类型支持 + 智能优先级）⭐⭐⭐⭐⭐*
*创建时间：2026-03-05*
*最后更新：2026-03-05 09:10*
*状态：✅ 完整功能，支持所有文件类型*

**核心价值**：
- 自动优化：根据任务选择最优模型 ⭐
- 成本节省：简单任务用Flash节省Token ⭐
- 质量提升：复杂任务用专业模型保证质量 ⭐
- 文件智能：自动识别文件类型并选择模型 ⭐
- 无感体验：用户无需任何操作，完全自动化 ⭐