# 终端OCR技能

专门处理终端/命令行界面截图的OCR识别技能。

## 📋 功能特点

### ✅ 已实现（v0.2.0增强版）
- **智能图像分块**：自动分割超长截图（支持10000px高度）
- **图像增强处理**：对比度提升 + 二值化，提高文字可读性  
- **多引擎支持**：Tesseract OCR + AI视觉分析双引擎
- **交互式模式**：用户友好的对话界面
- **配置文件**：灵活的参数调整（config/ocr-config.json）
- **错误处理**：详细的错误信息和建议
- **独立虚拟环境**：不依赖系统包，避免权限问题

### ⏳ 待实现
- **完整Tesseract集成**：需要宿主机安装tesseract-ocr
- **命令行语法高亮**：识别命令、路径、错误信息
- **日志格式解析**：自动识别时间戳和日志级别

## 🚀 使用方法

### 1. 安装技能
```bash
cd ~/.openclaw/workspace/skills/terminal-ocr
bash install.sh
```

### 2. 基本使用
```bash
# 处理单张图片
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png

# 交互式模式（推荐新手）
python scripts/enhanced-terminal-ocr.py -i

# 指定输出目录
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -o ./output/
```

### 3. 高级选项
```bash
# 强制使用AI视觉分析
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -e ai

# 使用自定义配置
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png --config ./my-config.json
```

## 💡 使用建议

### 最佳实践
1. **提供原始文本**：最准确的方案
2. **使用技能预处理**：改善图片质量
3. **宿主机安装OCR**：获得完整功能

### 技术限制
- VMware虚拟机无法安装系统级OCR引擎
- 超长截图需要分块处理
- AI视觉分析准确率有限

## 📁 文件结构

```
terminal-ocr/
├── SKILL.md          # 技能文档
├── README.md         # 使用说明
├── install.sh        # 安装脚本
├── config/           # 配置文件
│   └── ocr-config.json
├── scripts/          # 脚本目录
│   ├── enhanced-terminal-ocr.py  # 主脚本（增强版）
│   ├── preprocess-image.py      # 图像预处理
│   └── fallback-ai-analysis.py  # AI视觉分析
├── docs/            # 文档目录
│   ├── USER_GUIDE.md           # 用户指南
│   └── DEVELOPER_GUIDE.md     # 开发者指南
└── venv/            # Python虚拟环境
```

## 🔧 开发状态

- **版本**：0.2.0（增强版）
- **状态**：✅ 基础功能完成 + 交互式模式 + 配置支持
- **测试**：✅ 终端截图处理成功
- **文档**：✅ 用户指南 + 开发者指南
- **发布**：待完善Tesseract功能后发布到ClawHub

## 📊 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 处理速度 | < 10秒/图 | 取决于图片大小 |
| 内存使用 | < 512MB | ✅ |
| 支持格式 | PNG/JPG | ✅ |
| 最大尺寸 | 10000px | ✅ |

---
*让终端截图变得可读！*
*版本：0.2.0（增强版）*
*创建时间：2026-03-05*