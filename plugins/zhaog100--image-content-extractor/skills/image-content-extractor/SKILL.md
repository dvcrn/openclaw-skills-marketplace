---
name: image-content-extractor
description: "统一图片内容提取技能。智能识别终端/文档/通用模式，自动提取内容生成Markdown。"
---

# 图片内容提取技能 v2.0

统一图片内容提取技能，集成terminal-ocr功能，支持智能模式检测，自动提取内容并生成Markdown格式。

## 🎯 核心特性

### ⭐ 三大模式支持
- **终端模式（Terminal）** - 专门处理终端/命令行截图
  - 自动识别命令、路径、错误信息
  - 等宽字体优化
  - 命令高亮显示
  
- **文档模式（Document）** - 专门处理文档截图
  - 智能标题检测（数字编号/中文编号/Markdown标题）
  - 列表识别和格式化
  - 代码块检测
  
- **通用模式（General）** - 适用于各种类型图片
  - 自动检测图片类型
  - 通用结构分析
  - 灵活配置

### ⭐ 智能功能
- **自动模式检测** - 根据图片特征自动选择最佳模式
- **智能分块** - 基于内容边界自动分割超长图片
- **智能合并** - 自动检测重叠内容，精准拼接
- **结构识别** - 标题/段落/列表/代码块自动识别

### ⭐ 技术优势
- **统一代码库** - 一个技能，多模式支持
- **模块化设计** - core（核心）+ modes（模式）架构
- **高可扩展** - 易于添加新模式
- **知识库集成** - 自动更新QMD索引

## 🚀 使用方式

### 基础使用

```bash
# 自动检测模式（推荐）
python3 scripts/extract.py /path/to/image.png

# 指定模式
python3 scripts/extract.py /path/to/terminal.png --mode terminal
python3 scripts/extract.py /path/to/document.png --mode document
python3 scripts/extract.py /path/to/image.png --mode general

# 保存到文件
python3 scripts/extract.py /path/to/image.png -o output.md

# 保存到知识库
python3 scripts/extract.py /path/to/image.png \
    -k -c testing -t "测试用例设计"

# 详细输出
python3 scripts/extract.py /path/to/image.png -v
```

### 批量处理

```bash
# 批量处理整个目录
python3 scripts/extract.py /path/to/images/ \
    --batch \
    -k -c knowledge

# 指定模式批量处理
python3 scripts/extract.py /path/to/screenshots/ \
    --batch \
    --mode terminal \
    -k -c terminal-logs
```

### AI调用方式

```
用户：[发送终端截图]
AI：[自动检测terminal模式] → 提取命令 → 格式化输出

用户：[发送DeepSeek分享截图]
AI：[自动检测document模式] → 提取内容 → 生成Markdown

用户：[发送普通图片]
AI：[使用general模式] → 提取文本 → 结构化输出
```

## 🛠️ 技术架构

### 文件结构

```
image-content-extractor/
├── SKILL.md                    # 本文档
├── README.md                   # 快速开始
├── package.json                # 技能元数据
├── install.sh                  # 安装脚本
├── config/
│   └── extractor-config.json   # 配置文件
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── ocr.py                  # OCR引擎管理
│   ├── preprocess.py           # 图片预处理
│   ├── merge.py                # 内容合并
│   └── structure.py            # 结构分析
├── modes/                      # 模式模块
│   ├── __init__.py
│   ├── terminal.py             # 终端模式
│   ├── document.py             # 文档模式
│   └── general.py              # 通用模式
└── scripts/
    └── extract.py              # 主入口
```

### 处理流程

```
1. 图片输入
   ↓
2. 自动模式检测（可选）
   ↓
3. 模式特定预处理
   ↓
4. 智能分块
   ↓
5. OCR识别（Tesseract + AI备用）
   ↓
6. 智能合并
   ↓
7. 结构分析
   ↓
8. Markdown生成
   ↓
9. 模式特定后处理
   ↓
10. 输出/知识库集成
```

## 💡 使用场景

### 场景1：终端命令行截图
```
输入：终端截图（黑色背景，白色文字）
AI：[terminal模式] → 提取命令 → 高亮显示

输出示例：
```bash
$ npm install
```
**/usr/local/bin**

❌ Error: Package not found
```

### 场景2：DeepSeek分享截图
```
输入：DeepSeek长截图（43,936像素）
AI：[document模式] → 识别8大模块 → 生成Markdown

输出：
# 测试用例设计指南
> 提取时间: 2026-03-06 09:20

## 目录
1. [测试用例设计技术](#测试用例设计技术)
2. [三端测试方案](#三端测试方案)
...
```

### 场景3：知识库建设
```
输入：批量技术文档截图
AI：[batch模式] → 自动分类 → 更新索引 → Git提交

结果：
- 自动识别10个文档
- 分类到knowledge/testing
- 更新QMD索引
```

## 🔧 配置选项

### extractor-config.json

```json
{
  "ocr": {
    "engine": "tesseract",
    "languages": ["chi_sim", "eng"],
    "fallback_to_ai": true,
    "config": "--psm 6 --oem 3",
    "timeout": 30
  },
  "preprocessing": {
    "block_height": 2000,
    "overlap_height": 100,
    "min_block_height": 500,
    "contrast_enhancement": 1.5,
    "binary_threshold": 150
  },
  "structure_detection": {
    "detect_headers": true,
    "detect_lists": true,
    "detect_code_blocks": true,
    "detect_tables": true
  },
  "output": {
    "format": "markdown",
    "add_toc": true,
    "add_metadata": true
  },
  "knowledge_base": {
    "auto_index": true,
    "auto_commit": false,
    "default_category": "uncategorized"
  }
}
```

## 📈 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 识别准确率 | > 95% | 待测试 |
| 处理速度 | < 15秒/图 | 待测试 |
| 模式检测准确率 | > 90% | 待测试 |
| 最大图片尺寸 | 50000px | ✅ |
| 批量处理 | 支持 | ✅ |

## 🎓 最佳实践

### 1. 图片质量优化
- 分辨率 ≥ 1500px宽度
- 对比度清晰（黑白对比最佳）
- 避免压缩过度

### 2. 模式选择
- **终端截图**：使用terminal模式（或auto）
- **文档截图**：使用document模式（或auto）
- **不确定类型**：使用auto模式

### 3. 知识库集成
- 选择合适的分类（如testing、ai-system等）
- 添加描述性标题
- 定期更新索引

### 4. 批量处理
- 按类型分目录处理
- 使用统一的分类命名
- 检查处理结果

## 🔄 与旧版本对比

### terminal-ocr（旧版）
- 仅支持终端截图
- 单一模式
- 独立维护

### image-content-extractor v2.0（新版）
- ✅ 支持终端/文档/通用三种模式
- ✅ 自动模式检测
- ✅ 统一代码库
- ✅ 模块化架构
- ✅ 更易维护和扩展

## 📝 更新日志

### v2.0.0 (2026-03-06) - 统一版本
- ✅ 集成terminal-ocr功能
- ✅ 三大模式支持（terminal/document/general）
- ✅ 自动模式检测
- ✅ 模块化架构（core + modes）
- ✅ 统一配置和接口
- ✅ 批量处理支持

### v1.0.0 (2026-03-06) - 初始版本
- ✅ 基础内容提取
- ✅ Markdown输出
- ✅ 知识库集成

## 🚀 未来规划

### 短期（v2.1）
- [ ] 支持PDF文件
- [ ] 云端OCR集成（百度/腾讯）
- [ ] 实时预览

### 中期（v2.5）
- [ ] 更多模式支持（表格/图表）
- [ ] AI内容摘要
- [ ] 多语言支持

### 长期（v3.0）
- [ ] 在线编辑器
- [ ] 团队协作
- [ ] 智能推荐

## 🔗 相关链接

- **terminal-ocr技能**（已集成）
- **知识库系统**（QMD）
- **ClawHub**（待发布）

---

*图片内容提取技能 v2.0 - 统一版本，更强大更灵活*
*版本：2.0.0*
*创建：2026-03-06*
*更新：2026-03-06*
