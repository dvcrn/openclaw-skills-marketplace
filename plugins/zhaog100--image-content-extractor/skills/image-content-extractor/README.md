# Image Content Extractor v2.0

统一图片内容提取技能 - 支持终端/文档/通用三种模式

## 🎯 快速开始

### 安装
```bash
cd ~/.openclaw/workspace/skills/image-content-extractor
bash install.sh
```

### 使用
```bash
# 自动检测模式
python3 scripts/extract.py /path/to/image.png

# 指定模式
python3 scripts/extract.py /path/to/terminal.png --mode terminal

# 保存到知识库
python3 scripts/extract.py /path/to/image.png -k -c testing -t "标题"
```

## ✨ 核心特性

✅ **三种模式** - Terminal（终端）/ Document（文档）/ General（通用）
✅ **自动检测** - 智能识别图片类型
✅ **统一接口** - 一个技能，多场景使用
✅ **知识库集成** - 自动更新QMD索引

## 📚 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 🔄 变更

**v2.0** - 集成terminal-ocr，统一三大模式
**v1.0** - 初始版本

---
版本: 2.0.0
更新: 2026-03-06
