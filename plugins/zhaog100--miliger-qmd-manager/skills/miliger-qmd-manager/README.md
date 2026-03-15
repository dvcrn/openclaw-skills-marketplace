# miliger-qmd-manager

> 统一的QMD知识库管理技能 - 官方搜索 + 自定义管理

## 🎯 特色

**双引擎整合：**
- ✅ 官方qmd搜索（BM25 + 向量 + 混合）
- ✅ 自定义知识管理（项目管理/测试/内容创作）

**三大知识域：**
1. **项目管理** - PMP、敏捷、瀑布
2. **软件测试** - 自动化、性能、安全
3. **内容创作** - 公众号、视频号

## 🚀 快速开始

```bash
# 安装
bun install -g https://github.com/tobi/qmd

# 配置知识库
qmd collection add ./knowledge --name knowledge
qmd embed

# 搜索
qmd search "敏捷开发"
qmd vsearch "如何提高团队效率"  # 语义搜索
```

## 📊 搜索模式

| 模式 | 速度 | 准确度 | 场景 |
|------|------|--------|------|
| search | ⚡ 秒级 | ⭐⭐⭐ | 关键词明确 |
| vsearch | 🐢 1-2分钟 | ⭐⭐⭐⭐ | 理解意图 |
| query | 🐌 2-5分钟 | ⭐⭐⭐⭐⭐ | 最高质量 |

## 📝 示例

```bash
# 项目管理
qmd search "风险应对策略" -c pm

# 软件测试
qmd vsearch "性能测试方案" -c testing

# 内容创作
qmd query "公众号增长策略" -c content
```

## 🔗 相关资源

- 官方qmd: https://github.com/tobi/qmd
- ClawHub: https://clawhub.com/skills/miliger-qmd-manager

---

**作者**: 米粒儿
**版本**: 1.0.0
**更新**: 2026-03-06
