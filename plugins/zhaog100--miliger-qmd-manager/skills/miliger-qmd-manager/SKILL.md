---
name: miliger-qmd-manager
description: "统一的QMD知识库管理技能，集成官方qmd搜索功能和自定义项目管理/测试/内容创作知识管理。支持BM25关键词搜索、向量语义搜索、多集合管理。"
homepage: https://github.com/miliger/qmd-manager
---

# miliger-qmd-manager - 统一知识库管理

**集成官方qmd搜索 + 自定义项目管理/测试/内容创作知识管理**

## 🎯 核心功能

### ✅ 官方qmd功能
- **BM25关键词搜索** - 快速精准匹配
- **向量语义搜索** - 理解意图，找相关内容
- **混合搜索** - 结合关键词和语义
- **多集合管理** - 支持多个知识库

### ✅ 自定义管理功能
- **项目管理知识库** - PMP、敏捷、瀑布等
- **软件测试知识库** - 自动化测试、性能测试等
- **内容创作知识库** - 公众号、视频号运营
- **TUI交互浏览** - 终端可视化浏览

## 🚀 快速开始

### 安装依赖
```bash
# 安装Bun（如果未安装）
brew install oven-sh/bun/bun  # macOS
# 或
curl -fsSL https://bun.sh/install | bash  # Linux

# 安装qmd
bun install -g https://github.com/tobi/qmd
```

### 配置知识库
```bash
# 添加知识库集合
qmd collection add ./knowledge/project-management --name pm
qmd collection add ./knowledge/software-testing --name testing
qmd collection add ./knowledge/content-creation --name content

# 生成向量索引（首次使用）
qmd embed
```

## 📝 使用方法

### 1. 关键词搜索（默认，最快）
```bash
# 搜索项目管理知识
qmd search "敏捷开发" -n 5

# 搜索测试知识
qmd search "自动化测试" -c testing

# JSON输出（AI友好）
qmd search "内容创作" --json
```

### 2. 语义搜索（理解意图）
```bash
# 当关键词搜索找不到时使用
qmd vsearch "如何提高团队效率"

# 指定集合
qmd vsearch "测试最佳实践" -c testing
```

### 3. 混合搜索（最准确，最慢）
```bash
# 需要最高质量时使用
qmd query "项目风险管理策略"
```

### 4. 获取文档内容
```bash
# 按路径获取
qmd get "knowledge/project-management/pmp-guide.md"

# 按ID获取
qmd get "#docid123"

# 批量获取
qmd multi-get "doc1.md, doc2.md"
```

## 📊 搜索模式对比

| 模式 | 速度 | 准确度 | 适用场景 |
|------|------|--------|----------|
| **search** | ⚡ 秒级 | ⭐⭐⭐ | 关键词明确 |
| **vsearch** | 🐢 1-2分钟 | ⭐⭐⭐⭐ | 需要理解意图 |
| **query** | 🐌 2-5分钟 | ⭐⭐⭐⭐⭐ | 最高质量要求 |

## 🎨 特色功能

### 1. 智能搜索建议
- 自动推荐搜索模式
- 基于查询复杂度选择算法
- 失败时自动降级

### 2. 多集合管理
```bash
# 查看所有集合
qmd status

# 搜索特定集合
qmd search "关键词" -c pm        # 项目管理
qmd search "关键词" -c testing   # 软件测试
qmd search "关键词" -c content   # 内容创作
```

### 3. 性能优化
- **缓存机制** - 重复查询秒级响应
- **增量更新** - 只索引变更文件
- **并行处理** - 多集合并行搜索

## 🔧 高级配置

### 自定义知识库结构
```
./knowledge/
├── project-management/
│   ├── pmp/
│   ├── agile/
│   └── waterfall/
├── software-testing/
│   ├── automation/
│   ├── performance/
│   └── security/
└── content-creation/
    ├── wechat/
    └── video/
```

### 环境变量
```bash
# QMD路径（如果不在PATH中）
export QMD_PATH="/path/to/qmd"

# 知识库根目录
export KNOWLEDGE_BASE="/path/to/knowledge"

# 模型路径（向量搜索）
export QMD_MODEL="/path/to/model"
```

## 📈 使用场景

### 场景1：快速查找PMP知识
```bash
# 关键词搜索
qmd search "风险应对策略" -c pm

# 获取完整文档
qmd get "knowledge/project-management/pmp/risk-management.md"
```

### 场景2：测试方案参考
```bash
# 语义搜索（理解意图）
qmd vsearch "如何设计性能测试方案" -c testing

# 批量获取相关文档
qmd multi-get "test1.md, test2.md, test3.md"
```

### 场景3：内容创作灵感
```bash
# 混合搜索（高质量）
qmd query "公众号运营增长策略" -c content
```

## 🛠️ 维护命令

```bash
# 查看索引状态
qmd status

# 更新索引（增量）
qmd update

# 重新生成向量
qmd embed

# 清理缓存
qmd clean
```

## ⚠️ 性能提示

1. **优先使用search** - BM25通常足够快且准
2. **vsearch需预热** - 首次慢（加载模型），后续快
3. **query慎用** - 仅在需要最高质量时使用
4. **定期update** - 保持索引最新
5. **合理分集合** - 避免单个集合过大

## 📊 适用场景

### ✅ 适合
- 个人知识库管理
- 项目文档检索
- 技术资料查找
- 学习笔记管理

### ⚠️ 不适合
- 代码仓库搜索（用代码搜索工具）
- 海量数据（百万级文档）
- 实时性要求高的场景

## 🔗 相关资源

- **官方qmd**: https://github.com/tobi/qmd
- **Bun**: https://bun.sh
- **问题反馈**: https://github.com/miliger/qmd-manager/issues

---

**版本**: 1.0.0
**作者**: 米粒儿
**更新**: 2026-03-06

**整合了官方qmd的强大搜索能力和自定义的知识管理功能，为项目管理、软件测试、内容创作提供一站式知识检索服务** 🌟
