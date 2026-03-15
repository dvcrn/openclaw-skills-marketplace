# Session-Memory Enhanced 整合方案

## 🎯 整合目标

将 **memu-engine** 的企业级功能整合到 **session-memory-enhanced** 中，保持轻量级的同时获得强大的记忆能力。

---

## 📊 整合架构

```
session-memory-enhanced v4.0（融合版）
    │
    ├─ 前端层（Bash + 轻量级）
    │   ├─ 不可变分片策略（保留）
    │   ├─ 三位一体自动化（保留）
    │   ├─ Git自动备份（保留）
    │   └─ QMD知识库更新（保留）
    │
    ├─ 后端层（Python + 企业级）
    │   ├─ 结构化记忆提取（来自memu）
    │   ├─ 向量嵌入生成（来自memu）
    │   ├─ 多代理隔离（来自memu）
    │   └─ 语义搜索（来自memu）
    │
    └─ 统一检索接口
        ├─ 智能路由（自动选择最优方案）
        ├─ 优先：向量语义搜索
        └─ 后备：QMD关键词搜索
```

---

## 🚀 核心特性

### 1. **双引擎协同** ⭐⭐⭐⭐⭐
- **实时记忆**：session-memory 的不可变分片
- **长期记忆**：memu-engine 的结构化存储
- **自动同步**：分片固化后自动提取

### 2. **智能检索** ⭐⭐⭐⭐⭐
- **向量检索**：语义搜索（memu-engine）
- **关键词检索**：精确搜索（QMD）
- **自动选择**：根据查询类型智能路由

### 3. **多代理支持** ⭐⭐⭐⭐
- **目录隔离**：memory/agents/<agent>/
- **数据库隔离**：memory/<agent>/memu.db
- **权限控制**：searchableStores 配置

### 4. **零配置启动** ⭐⭐⭐⭐
- **自动检测**：检测 memu-engine 是否可用
- **降级方案**：不可用时使用 QMD 检索
- **灵活切换**：根据需求选择引擎

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── skills/
│   └── session-memory-enhanced/
│       ├── scripts/
│       │   ├── session-memory-enhanced-v4.sh      # 主脚本（融合版）
│       │   ├── memu-integration.sh                # memu集成脚本
│       │   ├── unified-search.sh                  # 统一检索接口
│       │   └── ai-summarizer.sh                   # AI摘要系统
│       ├── python/                                # Python后端（可选）
│       │   ├── extractor.py                       # 结构化提取
│       │   ├── embedder.py                        # 向量嵌入
│       │   └── searcher.py                        # 语义搜索
│       ├── config/
│       │   └── integration.json                   # 整合配置
│       └── SKILL.md
│
└── memory/
    ├── agents/
    │   ├── main/
    │   │   ├── part000.json                       # 不可变分片
    │   │   ├── memu.db                            # SQLite数据库（memu）
    │   │   └── .summary.json                      # AI摘要
    │   └── research/
    └── shared/
        └── memu.db                                # 共享文档库
```

---

## 🔧 配置文件

### integration.json

```json
{
  "version": "4.0.0",
  "engines": {
    "session_memory": {
      "enabled": true,
      "priority": 1,
      "features": ["realtime", "git_backup", "qmd_update"]
    },
    "memu_engine": {
      "enabled": false,
      "priority": 2,
      "features": ["structured_extraction", "vector_search", "multi_agent"],
      "requirements": {
        "openai_api_key": "${OPENAI_API_KEY}",
        "python_env": "auto"
      }
    }
  },
  "search": {
    "strategy": "hybrid",
    "primary": "memu_engine",
    "fallback": "session_memory",
    "timeout": 5000
  },
  "agents": {
    "main": {
      "memoryEnabled": true,
      "searchEnabled": true,
      "searchableStores": ["self", "shared"],
      "flushIdleSeconds": 1800,
      "maxMessagesPerPart": 60
    },
    "research": {
      "memoryEnabled": true,
      "searchEnabled": true,
      "searchableStores": ["self", "shared"],
      "flushIdleSeconds": 3600,
      "maxMessagesPerPart": 100
    }
  }
}
```

---

## 💻 代码实现

### 1. session-memory-enhanced-v4.sh（主脚本）

```bash
#!/bin/bash
# Session-Memory Enhanced v4.0 - 融合版
# 整合 session-memory + memu-engine 双引擎

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
CONFIG_FILE="$WORKSPACE/skills/session-memory-enhanced/config/integration.json"

# 加载配置
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        MEMU_ENABLED=$(jq -r '.engines.memu_engine.enabled' "$CONFIG_FILE")
        SEARCH_STRATEGY=$(jq -r '.search.strategy' "$CONFIG_FILE")
        log "📋 配置加载完成（memu: $MEMU_ENABLED, 搜索策略: $SEARCH_STRATEGY）"
    else
        MEMU_ENABLED=false
        SEARCH_STRATEGY="session_memory"
    fi
}

# 检查 memu-engine 是否可用
check_memu_available() {
    if [ "$MEMU_ENABLED" = "true" ]; then
        # 检查 Python 环境
        if command -v python3 &> /dev/null; then
            # 检查 memu 模块
            python3 -c "import memu" 2>/dev/null && return 0
        fi
    fi
    return 1
}

# 固化分片（增强版）
flush_tail() {
    # 1. 调用原始 session-memory 逻辑
    original_flush_tail
    
    # 2. 如果 memu-engine 可用，触发结构化提取
    if check_memu_available; then
        log "🔄 触发 memu-engine 结构化提取..."
        bash "$WORKSPACE/skills/session-memory-enhanced/scripts/memu-integration.sh" \
            --action extract \
            --agent "$AGENT_NAME" \
            --part "$part_file"
    fi
    
    # 3. 更新 QMD（保留）
    update_qmd
    
    # 4. Git 提交（保留）
    git_commit
}

# 主流程
main() {
    load_config
    
    if should_flush; then
        flush_tail
    fi
}

main
```

### 2. memu-integration.sh（memu集成脚本）

```bash
#!/bin/bash
# memu-engine 集成脚本
# 功能：从 session-memory 分片提取结构化记忆

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
MEMU_DB="$MEMORY_DIR/memu.db"

# 从分片提取结构化记忆
extract_structured_memory() {
    local part_file="$1"
    
    if [ ! -f "$part_file" ]; then
        log "⚠️ 分片文件不存在：$part_file"
        return 1
    fi
    
    log "📊 从分片提取结构化记忆..."
    
    # 调用 Python 提取器
    python3 "$WORKSPACE/skills/session-memory-enhanced/python/extractor.py" \
        --input "$part_file" \
        --output "$MEMU_DB" \
        --agent "$AGENT_NAME" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ 结构化记忆提取完成"
        return 0
    else
        log "❌ 结构化记忆提取失败"
        return 1
    fi
}

# 生成向量嵌入
generate_embeddings() {
    local part_file="$1"
    
    log "🔍 生成向量嵌入..."
    
    python3 "$WORKSPACE/skills/session-memory-enhanced/python/embedder.py" \
        --input "$part_file" \
        --db "$MEMU_DB" \
        --agent "$AGENT_NAME" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ 向量嵌入生成完成"
        return 0
    else
        log "❌ 向量嵌入生成失败"
        return 1
    fi
}

# 主流程
main() {
    local action="$1"
    shift
    
    case "$action" in
        extract)
            extract_structured_memory "$@"
            ;;
        embed)
            generate_embeddings "$@"
            ;;
        *)
            log "❌ 未知操作：$action"
            return 1
            ;;
    esac
}

main "$@"
```

### 3. unified-search.sh（统一检索接口）

```bash
#!/bin/bash
# 统一检索接口
# 功能：智能路由，自动选择最优检索方式

WORKSPACE="/root/.openclaw/workspace"
CONFIG_FILE="$WORKSPACE/skills/session-memory-enhanced/config/integration.json"

# 智能检索
search() {
    local query="$1"
    local strategy=$(jq -r '.search.strategy' "$CONFIG_FILE")
    
    log "🔍 检索查询：$query（策略：$strategy）"
    
    case "$strategy" in
        hybrid)
            # 优先使用 memu-engine 向量检索
            if check_memu_available; then
                log "📊 使用 memu-engine 向量检索..."
                python3 "$WORKSPACE/skills/session-memory-enhanced/python/searcher.py" \
                    --query "$query" \
                    --agent "$AGENT_NAME" \
                    --timeout 5000
                
                if [ $? -ne 0 ]; then
                    log "⚠️ memu-engine 检索失败，降级到 QMD..."
                    qmd search "$query" -c memory
                fi
            else
                log "📊 使用 QMD 关键词检索..."
                qmd search "$query" -c memory
            fi
            ;;
        
        memu_engine)
            # 仅使用 memu-engine
            python3 "$WORKSPACE/skills/session-memory-enhanced/python/searcher.py" \
                --query "$query" \
                --agent "$AGENT_NAME"
            ;;
        
        session_memory)
            # 仅使用 QMD
            qmd search "$query" -c memory
            ;;
        
        *)
            log "❌ 未知检索策略：$strategy"
            return 1
            ;;
    esac
}

# 检查 memu 是否可用
check_memu_available() {
    command -v python3 &> /dev/null && \
    python3 -c "import memu" 2>/dev/null
}

# 主流程
main() {
    local query="$1"
    
    if [ -z "$query" ]; then
        log "❌ 缺少查询参数"
        return 1
    fi
    
    search "$query"
}

main "$@"
```

---

## 📝 Python 后端实现

### extractor.py（结构化提取）

```python
#!/usr/bin/env python3
"""
结构化记忆提取器
从 session-memory 分片提取结构化信息
"""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
import openai

class MemoryExtractor:
    def __init__(self, db_path: str, agent_name: str):
        self.db_path = Path(db_path)
        self.agent_name = agent_name
        self._init_db()
    
    def _init_db(self):
        """初始化 SQLite 数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_type 
            ON memories(agent, type)
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_from_part(self, part_file: str) -> Dict[str, Any]:
        """从分片文件提取结构化记忆"""
        with open(part_file, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        
        # 提取关键信息
        insights = {
            'profile': self._extract_profile(messages),
            'events': self._extract_events(messages),
            'knowledge': self._extract_knowledge(messages),
            'decisions': self._extract_decisions(messages),
            'lessons': self._extract_lessons(messages)
        }
        
        return insights
    
    def _extract_profile(self, messages: List[Dict]) -> Dict:
        """提取用户画像"""
        # TODO: 实现 LLM 提取
        return {}
    
    def _extract_events(self, messages: List[Dict]) -> List[Dict]:
        """提取事件列表"""
        # TODO: 实现 LLM 提取
        return []
    
    def _extract_knowledge(self, messages: List[Dict]) -> List[Dict]:
        """提取知识库"""
        # TODO: 实现 LLM 提取
        return []
    
    def _extract_decisions(self, messages: List[Dict]) -> List[Dict]:
        """提取决策"""
        # TODO: 实现 LLM 提取
        return []
    
    def _extract_lessons(self, messages: List[Dict]) -> List[Dict]:
        """提取经验教训"""
        # TODO: 实现 LLM 提取
        return []
    
    def save_to_db(self, insights: Dict[str, Any]):
        """保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for memory_type, content in insights.items():
            if content:
                cursor.execute('''
                    INSERT INTO memories (agent, type, content, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (
                    self.agent_name,
                    memory_type,
                    json.dumps(content, ensure_ascii=False),
                    json.dumps({'source': 'session_memory'})
                ))
        
        conn.commit()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='结构化记忆提取器')
    parser.add_argument('--input', required=True, help='输入分片文件')
    parser.add_argument('--output', required=True, help='输出数据库')
    parser.add_argument('--agent', required=True, help='代理名称')
    
    args = parser.parse_args()
    
    extractor = MemoryExtractor(args.output, args.agent)
    insights = extractor.extract_from_part(args.input)
    extractor.save_to_db(insights)
    
    print(f"✅ 提取完成：{args.input}")

if __name__ == '__main__':
    main()
```

---

## 🚀 安装和使用

### 1. 安装

```bash
# 从 ClawHub 安装
clawhub install session-memory-enhanced

# 或手动安装
cd /root/.openclaw/workspace/skills/session-memory-enhanced
bash scripts/install.sh
```

### 2. 配置

```bash
# 复制配置模板
cp config/integration.json.example config/integration.json

# 编辑配置
nano config/integration.json

# 启用 memu-engine
jq '.engines.memu_engine.enabled = true' config/integration.json > tmp.json
mv tmp.json config/integration.json

# 配置 API Key
export OPENAI_API_KEY="your_key"
```

### 3. 使用

**自动模式**（推荐）：
```bash
# 正常使用，自动触发
# 每小时自动运行一次
crontab -l
# 0 * * * * /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh
```

**手动模式**：
```bash
# 立即执行
bash /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 手动检索
bash /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/unified-search.sh "查询关键词"
```

---

## 📊 性能对比

| 功能 | v3.4（旧版） | v4.0（融合版） |
|------|-------------|---------------|
| **实时记忆** | ✅ | ✅ |
| **Git备份** | ✅ | ✅ |
| **QMD检索** | ✅ | ✅ |
| **结构化提取** | ❌ | ✅ |
| **向量检索** | ❌ | ✅ |
| **多代理隔离** | ❌ | ✅ |
| **资源占用** | 🟢 116K | 🟡 116K + Python |
| **安装难度** | 🟢 零配置 | 🟡 可选配置 |

---

## 🎯 总结

**v4.0 融合版优势**：
1. ⭐ **双引擎协同** - 实时 + 长期记忆
2. ⭐ **智能检索** - 向量 + 关键词
3. ⭐ **向下兼容** - 可降级到 v3.4
4. ⭐ **零配置启动** - 自动检测环境

**推荐使用场景**：
- ✅ 需要长期记忆管理
- ✅ 需要语义搜索
- ✅ 需要多代理隔离
- ✅ 需要企业级功能

**不推荐场景**：
- ❌ 仅需简单记忆
- ❌ 资源受限环境
- ❌ 不想配置 Python

---

**下一步**：
1. 实现 Python 后端（extractor + embedder + searcher）
2. 测试双引擎协同
3. 优化性能
4. 发布到 ClawHub
