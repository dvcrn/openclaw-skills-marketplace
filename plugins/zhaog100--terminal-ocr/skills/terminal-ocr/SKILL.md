---
name: terminal-ocr
description: "终端截图OCR识别技能。专门处理终端/命令行界面的截图，提取文本内容并进行分析。"
---

# 终端OCR技能

专门针对终端/命令行界面截图的OCR识别和文本提取技能。

## 🎯 核心特性

### ⭐ 智能图像预处理
- ✅ **自动分块**：超长截图自动分割为可处理的块
- ✅ **对比度增强**：提升终端文字的可读性
- ✅ **二值化处理**：优化黑白对比，减少噪声
- ✅ **字体识别**：针对等宽字体优化识别

### ⭐ 多引擎支持
- ✅ **Tesseract OCR**：本地OCR引擎（需要安装）
- ✅ **AI视觉分析**：无OCR环境下的替代方案
- ✅ **混合模式**：结合两种方法提高准确率

### ⭐ 终端专用优化
- ✅ **命令行语法高亮**：识别命令、路径、错误信息
- ✅ **日志格式解析**：自动识别时间戳、日志级别
- ✅ **表格结构重建**：还原终端表格格式
- ✅ **编码检测**：自动检测UTF-8、GBK等编码

## 🚀 使用方式

### 1. 安装技能
```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/terminal-ocr

# 运行安装脚本
bash install.sh
```

### 2. 基础OCR识别
```bash
# 分析终端截图
./scripts/terminal-ocr.sh /path/to/screenshot.png

# 输出文本内容
./scripts/extract-text.sh /path/to/screenshot.png
```

### 3. 高级分析
```bash
# 命令行分析
./scripts/analyze-commands.sh /path/to/screenshot.png

# 日志分析  
./scripts/analyze-logs.sh /path/to/screenshot.png

# 错误诊断
./scripts/diagnose-errors.sh /path/to/screenshot.png
```

## 🛠️ 技术实现

### 文件结构
```
terminal-ocr/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── config/
│   └── ocr-config.json
├── scripts/
│   ├── terminal-ocr.sh          # 主OCR脚本
│   ├── extract-text.sh         # 文本提取
│   ├── analyze-commands.sh     # 命令分析
│   ├── analyze-logs.sh         # 日志分析
│   ├── diagnose-errors.sh      # 错误诊断
│   ├── preprocess-image.py     # 图像预处理
│   └── fallback-ai-analysis.py # AI视觉分析备用
└── data/
    └── processed/
```

### 核心算法
1. **图像预处理**：分块 + 增强 + 二值化
2. **OCR识别**：Tesseract + 自定义词典
3. **后处理**：语法高亮 + 结构重建
4. **备用方案**：AI视觉分析（无OCR环境）

## 💡 使用场景

### 场景1：系统日志分析
```
用户：[发送系统日志截图]
AI：[调用terminal-ocr] → 提取日志内容 → 分析错误信息
```

### 场景2：命令行输出解析
```
用户：[发送命令行输出截图]  
AI：[调用terminal-ocr] → 识别命令和输出 → 提供解释
```

### 场景3：配置文件查看
```
用户：[发送配置文件截图]
AI：[调用terminal-ocr] → 提取配置内容 → 分析设置
```

## 🔧 环境要求

### 必需依赖
- Python 3.8+
- OpenCV-Python
- Pillow

### 可选依赖（推荐）
- Tesseract OCR (tesseract-ocr)
- 中文语言包 (tesseract-ocr-chi-sim)

### 无依赖模式
- 纯AI视觉分析（准确率较低但无需安装）

## 📈 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 处理速度 | < 10秒/图 | 待测试 |
| 准确率 | > 85% | 待测试 |
| 支持格式 | PNG/JPG | ✅ |
| 最大尺寸 | 10000px | ✅ |

## 🚀 未来规划

### 短期
- [ ] 完成基础OCR功能
- [ ] 实现图像预处理
- [ ] 添加AI视觉备用方案

### 中期  
- [ ] 命令行语法分析
- [ ] 日志格式识别
- [ ] 错误诊断功能

### 长期
- [ ] 多语言支持
- [ ] 实时OCR
- [ ] 与OpenClaw深度集成

---
*终端OCR技能 - 让终端截图变得可读*
*版本：0.1.0（开发中）*
*创建时间：2026-03-05*