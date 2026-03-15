---
name: session-memory-enhanced
description: "Session-Memory Enhanced v4.0 - 统一增强版。融合 session-memory + memu-engine 核心功能。特性：结构化提取 + 向量检索 + 不可变分片 + 三位一体自动化 + 多代理隔离 + AI 摘要 + 零配置启动。"
---

# Session-Memory Enhanced v4.0

**统一增强版 - 融合 session-memory + memu-engine 核心功能**

## 🎯 核心特性

### 吸收的 memu-engine 优势 ⭐⭐⭐⭐⭐

1. **结构化记忆提取**
   - LLM 提取用户画像
   - 事件识别与记录
   - 知识点提取
   - 决策追踪
   - 经验教训总结

2. **向量检索系统**
   - OpenAI Embeddings API
   - 语义搜索（不仅仅是关键词）
   - 相似度计算
   - 智能排序

3. **多代理隔离架构**
   - 目录隔离（memory/agents/<agent>/）
   - 数据库隔离（<agent>/memu.db）
   - 权限控制（searchableStores）

4. **去重机制**
   - .processed 标记文件
   - 防止重复处理
   - 减少系统负载

### 保留的 session-memory 优势 ⭐⭐⭐⭐⭐

1. **不可变分片策略**
   - Token 节省 90%+
   - 避免重复加载

2. **三位一体自动化**
   - 记忆保存
   - QMD 知识库更新
   - Git 自动提交

3. **AI 摘要系统**
   - 关键词提取
   - 重要性评估
   - 自动生成摘要

4. **零配置启动**
   - 默认使用轻量级模式
   - 可选启用高级功能

## 📁 文件结构

```
/root/.openclaw/workspace/skills/session-memory-enhanced/
├── scripts/
│   ├── session-memory-enhanced-v4.sh       # 主脚本（统一版）
│   ├── ai-summarizer.sh                    # AI 摘要
│   └── deep-sanitizer.sh                   # 深度清洗
│
├── python/                                 # Python 核心（吸收 memu 优势）
│   ├── extractor.py                        # 结构化提取器
│   ├── embedder.py                         # 向量嵌入器
│   ├── searcher.py                         # 语义搜索器
│   └── requirements.txt                    # Python 依赖
│
├── config/
│   └── unified.json.example                # 配置模板
│
├── docs/
│   ├── UNIFIED_IMPLEMENTATION.md           # 完整实现文档
│   └── INTEGRATION_PLAN.md                 # 整合计划
│
└── SKILL.md                                # 本文档
```

## 🚀 安装

### 快速安装

```bash
# 1. 复制配置模板
cd /root/.openclaw/workspace/skills/session-memory-enhanced
cp config/unified.json.example config/unified.json

# 2. 重启即可使用（轻量级模式）
```

### 启用高级功能

```bash
# 1. 安装 Python 依赖
cd python
pip3 install -r requirements.txt

# 2. 配置 API Key
export OPENAI_API_KEY="your_key"

# 3. 启用功能
jq '.features.structuredExtraction = true' config/unified.json > tmp.json
mv tmp.json config/unified.json

jq '.features.vectorSearch = true' config/unified.json > tmp.json
mv tmp.json config/unified.json

# 4. 重启
```

## 📋 配置说明

### unified.json

```json
{
  "version": "4.0.0",
  "flushIdleSeconds": 1800,
  "maxMessagesPerPart": 60,
  
  "features": {
    "structuredExtraction": false,  // 启用结构化提取
    "vectorSearch": false,          // 启用向量检索
    "aiSummary": true,              // AI 摘要
    "gitBackup": true,              // Git 备份
    "qmdUpdate": true               // QMD 更新
  },
  
  "openaiApiKey": "${OPENAI_API_KEY}",
  
  "agents": {
    "main": {
      "searchableStores": ["self", "shared"],
      "flushIdleSeconds": 1800,
      "maxMessagesPerPart": 60
    }
  }
}
```

## 🎯 使用方式

### 自动模式（推荐）

```bash
# 每小时自动运行
crontab -e
# 添加：
0 * * * * /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh
```

### 手动模式

```bash
# 立即执行
bash /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 检索
python3 /root/.openclaw/workspace/skills/session-memory-enhanced/python/searcher.py \
    --query "查询关键词" \
    --db /root/.openclaw/workspace/memory/agents/main/vectors.db \
    --agent main \
    --api-key "your_key"
```

## 📊 功能对比

| 功能 | v3.4（旧版） | v4.0（统一版） |
|------|-------------|---------------|
| **不可变分片** | ✅ | ✅ |
| **三位一体** | ✅ | ✅ |
| **Git 备份** | ✅ | ✅ |
| **QMD 集成** | ✅ | ✅ |
| **AI 摘要** | ✅ | ✅ |
| **结构化提取** | ❌ | ✅ |
| **向量检索** | ❌ | ✅ |
| **多代理隔离** | ✅ | ✅ |
| **去重机制** | ✅ | ✅（增强）|
| **Python 集成** | ❌ | ✅（可选） |

## 🌟 优势总结

### 来自 memu-engine 的优势
1. ⭐ **结构化记忆** - 深度理解对话内容
2. ⭐ **向量检索** - 语义搜索，更智能
3. ⭐ **多代理隔离** - 企业级架构
4. ⭐ **去重机制** - 避免重复处理

### 来自 session-memory 的优势
1. ⭐ **不可变分片** - Token 节省 90%+
2. ⭐ **三位一体** - 一次触发，三件事完成
3. ⭐ **Git 备份** - 自动备份，安全可靠
4. ⭐ **零配置** - 开箱即用

### 融合后的优势
1. ⭐⭐⭐ **功能完整** - 两大系统所有功能
2. ⭐⭐⭐ **灵活配置** - 可选择启用功能
3. ⭐⭐⭐ **向下兼容** - 不启用时与 v3.4 一致
4. ⭐⭐⭐ **平滑升级** - 无缝从 v3.4 升级

## 📝 更新日志

### v4.0.0 (2026-03-09)
- ✅ 吸收 memu-engine 的结构化提取
- ✅ 吸收 memu-engine 的向量检索
- ✅ 吸收 memu-engine 的多代理隔离
- ✅ 吸收 memu-engine 的去重机制
- ✅ 保留 session-memory 的所有优势
- ✅ 统一配置文件（unified.json）
- ✅ 可选 Python 集成
- ✅ 智能降级方案（向量检索 → QMD 检索）

---

**作者**：米粒儿  
**版本**：v4.0.0  
**创建时间**：2026-03-09 19:30  
**更新时间**：2026-03-09 19:50
