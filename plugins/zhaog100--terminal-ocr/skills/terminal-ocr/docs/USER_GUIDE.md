# 终端OCR技能用户指南

## 📋 快速开始

### 1. 安装技能
```bash
cd ~/.openclaw/workspace/skills/terminal-ocr
bash install.sh
```

### 2. 基本使用
```bash
# 处理单张图片
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png

# 指定输出目录
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -o ./output/

# 交互式模式
python scripts/enhanced-terminal-ocr.py -i
```

### 3. 高级选项
```bash
# 强制使用AI视觉分析
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -e ai

# 使用自定义配置
python scripts/enhanced-terminal-ocr.py /path/to/screenshot.png --config ./my-config.json
```

## 🎯 功能特性

### ✅ 智能预处理
- **自动分块**：超长截图自动分割
- **对比度增强**：提升文字可读性
- **二值化处理**：优化黑白对比
- **尺寸限制**：防止内存溢出

### ✅ 多引擎支持
- **Tesseract OCR**：高精度文本识别（需要安装）
- **AI视觉分析**：无依赖备用方案
- **智能切换**：自动选择最佳引擎

### ✅ 用户友好
- **交互式模式**：简单易用的对话界面
- **错误处理**：详细的错误信息和建议
- **配置文件**：灵活的参数调整
- **进度显示**：实时处理状态反馈

## 🔧 配置说明

### 配置文件位置
`config/ocr-config.json`

### 主要配置项
```json
{
  "preprocessing": {
    "block_height": 2000,        // 分块高度
    "contrast_enhancement": 1.5,  // 对比度增强
    "binary_threshold": 150      // 二值化阈值
  },
  "ocr_engines": {
    "tesseract": {
      "enabled": true,
      "languages": ["eng", "chi_sim"]  // 支持的语言
    },
    "ai_vision": {
      "enabled": true
    }
  },
  "output": {
    "format": "text",            // 输出格式
    "preserve_formatting": true   // 保留格式
  }
}
```

## 💡 使用技巧

### 最佳实践
1. **图片质量**：确保截图清晰，避免模糊
2. **字体大小**：终端字体不宜过小
3. **背景对比**：黑白对比度越高越好
4. **分块处理**：超长截图会自动分块处理

### 故障排除
- **"图片文件不存在"**：检查路径是否正确
- **"图片文件过大"**：图片超过50MB，建议裁剪
- **"Tesseract未找到"**：使用AI视觉分析或安装tesseract
- **"处理失败"**：查看详细错误信息，调整配置

## 📊 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 处理速度 | < 10秒/图 | 取决于图片大小 |
| 内存使用 | < 512MB | ✅ |
| 支持格式 | PNG/JPG | ✅ |
| 最大尺寸 | 10000px | ✅ |

## 🚀 未来计划

### 短期
- [ ] 完整Tesseract集成
- [ ] 命令行语法高亮
- [ ] 日志格式识别

### 中期
- [ ] 批量处理支持
- [ ] Web界面
- [ ] 移动端适配

### 长期
- [ ] 实时OCR
- [ ] 多语言支持
- [ ] 与OpenClaw深度集成

---
*让终端截图变得可读！*
*版本：0.2.0（增强版）*
*创建时间：2026-03-05*