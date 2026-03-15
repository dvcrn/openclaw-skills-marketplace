# Session-Memory Enhanced v4.0 - 统一实现方案

## 🎯 目标

将 **memu-engine** 的核心功能直接移植到 **session-memory-enhanced** 中，创建一个**统一的增强版记忆技能**。

---

## 📊 功能清单

### 从 memu-engine 移植的核心功能

1. **结构化记忆提取** ⭐⭐⭐⭐⭐
   - 用户画像提取
   - 事件识别
   - 知识提取
   - 技能识别
   - 决策记录

2. **向量检索系统** ⭐⭐⭐⭐⭐
   - OpenAI Embeddings API
   - 本地向量存储（SQLite + JSON）
   - 语义搜索
   - 混合检索（向量 + 关键词）

3. **多代理隔离架构** ⭐⭐⭐⭐
   - 目录隔离（memory/agents/<agent>/）
   - 数据库隔离（<agent>/memu.db）
   - 权限控制（searchableStores）

4. **自动环境自举** ⭐⭐⭐
   - 自动检测 Python 环境
   - 自动安装依赖
   - 降级方案（无 Python 时使用 QMD）

### 保留 session-memory 的核心功能

1. **不可变分片策略** ⭐⭐⭐⭐⭐
2. **三位一体自动化** ⭐⭐⭐⭐⭐
3. **Git 自动备份** ⭐⭐⭐⭐
4. **QMD 知识库集成** ⭐⭐⭐⭐
5. **AI 摘要系统** ⭐⭐⭐

---

## 📁 统一文件结构

```
/root/.openclaw/workspace/skills/session-memory-enhanced/
├── scripts/
│   ├── session-memory-enhanced-v4.sh       # 主脚本（统一版）
│   ├── structured-extractor.sh             # 结构化提取
│   ├── vector-search.sh                    # 向量检索
│   ├── ai-summarizer.sh                    # AI 摘要
│   ├── deep-sanitizer.sh                   # 深度清洗
│   └── install.sh                          # 安装脚本
│
├── python/                                 # Python 核心（可选）
│   ├── extractor.py                        # 结构化提取器
│   ├── embedder.py                         # 向量嵌入器
│   ├── searcher.py                         # 语义搜索器
│   ├── migration.py                        # 迁移工具
│   ├── requirements.txt                    # Python 依赖
│   └── setup.py                            # Python 安装
│
├── config/
│   ├── unified.json                        # 统一配置
│   └── agents.json                         # 代理配置
│
├── docs/
│   ├── UNIFIED_IMPLEMENTATION.md           # 本文档
│   ├── API_REFERENCE.md                    # API 参考
│   └── MIGRATION_GUIDE.md                  # 迁移指南
│
├── tests/
│   ├── test_extractor.py                   # 测试提取器
│   ├── test_embedder.py                    # 测试嵌入器
│   └── test_searcher.py                    # 测试搜索器
│
├── SKILL.md                                # 技能文档
├── README.md                               # 说明文档
└── package.json                            # 技能元数据
```

---

## 🔧 核心代码实现

### 1. session-memory-enhanced-v4.sh（主脚本）

```bash
#!/bin/bash
# Session-Memory Enhanced v4.0 - 统一增强版
# 整合 session-memory + memu-engine 核心功能
# 创建时间：2026-03-09 19:30
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
SHARED_DIR="$WORKSPACE/memory/shared"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"

# Python 组件路径
PYTHON_DIR="$WORKSPACE/skills/session-memory-enhanced/python"
EXTRACTOR="$PYTHON_DIR/extractor.py"
EMBEDDER="$PYTHON_DIR/embedder.py"
SEARCHER="$PYTHON_DIR/searcher.py"

# 配置文件
CONFIG_FILE="$WORKSPACE/skills/session-memory-enhanced/config/unified.json"
AGENT_CONFIG="$WORKSPACE/config/agents.json"

# 默认配置
FLUSH_IDLE_SECONDS=1800
MAX_MESSAGES_PER_PART=60
ENABLE_STRUCTURED_EXTRACTION=false
ENABLE_VECTOR_SEARCH=false
OPENAI_API_KEY=""

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$SHARED_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 Session-Memory Enhanced v4.0 启动（统一增强版）"
log "================================"

# 加载配置
load_config() {
    # 加载主配置
    if [ -f "$CONFIG_FILE" ]; then
        log "📋 加载主配置：$CONFIG_FILE"
        
        FLUSH_IDLE_SECONDS=$(jq -r '.flushIdleSeconds // 1800' "$CONFIG_FILE")
        MAX_MESSAGES_PER_PART=$(jq -r '.maxMessagesPerPart // 60' "$CONFIG_FILE")
        ENABLE_STRUCTURED_EXTRACTION=$(jq -r '.features.structuredExtraction // false' "$CONFIG_FILE")
        ENABLE_VECTOR_SEARCH=$(jq -r '.features.vectorSearch // false' "$CONFIG_FILE")
    fi
    
    # 加载代理配置
    if [ -f "$AGENT_CONFIG" ]; then
        log "📋 加载代理配置：$AGENT_CONFIG"
        
        AGENT_FLUSH=$(jq -r ".agents.${AGENT_NAME}.flushIdleSeconds // empty" "$AGENT_CONFIG")
        AGENT_MAX=$(jq -r ".agents.${AGENT_NAME}.maxMessagesPerPart // empty" "$AGENT_CONFIG")
        
        [ -n "$AGENT_FLUSH" ] && FLUSH_IDLE_SECONDS="$AGENT_FLUSH"
        [ -n "$AGENT_MAX" ] && MAX_MESSAGES_PER_PART="$AGENT_MAX"
    fi
    
    # 加载环境变量
    OPENAI_API_KEY="${OPENAI_API_KEY:-$(jq -r '.openaiApiKey // empty' "$CONFIG_FILE" 2>/dev/null)}"
    
    log "✅ 配置加载完成"
    log "   - 闲置时间：${FLUSH_IDLE_SECONDS}秒"
    log "   - 消息上限：${MAX_MESSAGES_PER_PART}条"
    log "   - 结构化提取：${ENABLE_STRUCTURED_EXTRACTION}"
    log "   - 向量检索：${ENABLE_VECTOR_SEARCH}"
}

# 检查 Python 环境
check_python_available() {
    if ! command -v python3 &> /dev/null; then
        log "⚠️ Python3 未安装"
        return 1
    fi
    
    # 检查依赖
    if [ -f "$PYTHON_DIR/requirements.txt" ]; then
        python3 -c "import openai" 2>/dev/null || {
            log "⚠️ Python 依赖未安装"
            return 1
        }
    fi
    
    return 0
}

# 1. 检查是否需要固化分片
should_flush() {
    [ ! -f "$TAIL_FILE" ] && return 1
    
    local msg_count=$(jq '.messages | length' "$TAIL_FILE" 2>/dev/null || echo "0")
    [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0
    
    local last_modified=$(stat -c %Y "$TAIL_FILE" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local idle_time=$((now - last_modified))
    [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0
    
    return 1
}

# 2. 固化分片（不可变 + 去重）
flush_tail() {
    if [ ! -f "$TAIL_FILE" ]; then
        log "ℹ️ 无需固化（tail文件不存在）"
        return 0
    fi
    
    # 生成 part 编号
    local part_num=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
    local part_file="$MEMORY_DIR/part$(printf '%03d' $part_num).json"
    local processed_marker="$part_file.processed"
    
    # 去重检查（借鉴 memu-engine）
    if [ -f "$processed_marker" ]; then
        log "⚠️ 已处理过，跳过：$part_file"
        return 0
    fi
    
    # 固化分片
    mv "$TAIL_FILE" "$part_file"
    touch "$processed_marker"
    
    log "✅ 固化分片：$part_file"
    
    # 触发增强功能
    enhance_memory "$part_file"
}

# 3. 增强记忆（结构化提取 + 向量嵌入）
enhance_memory() {
    local part_file="$1"
    
    log "🔄 增强记忆处理：$part_file"
    
    # A. 结构化提取（如果启用）
    if [ "$ENABLE_STRUCTURED_EXTRACTION" = "true" ] && check_python_available; then
        extract_structured_memory "$part_file"
    fi
    
    # B. 向量嵌入（如果启用）
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        generate_embeddings "$part_file"
    fi
    
    # C. AI 摘要（保留）
    if [ -f "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh" ]; then
        bash "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh"
    fi
    
    log "✅ 记忆增强完成"
}

# 4. 结构化记忆提取
extract_structured_memory() {
    local part_file="$1"
    
    log "📊 提取结构化记忆..."
    
    if [ -f "$EXTRACTOR" ]; then
        python3 "$EXTRACTOR" \
            --input "$part_file" \
            --output "$MEMORY_DIR/structured.db" \
            --agent "$AGENT_NAME" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 结构化提取完成"
        else
            log "❌ 结构化提取失败"
        fi
    else
        log "⚠️ 提取器不存在：$EXTRACTOR"
    fi
}

# 5. 生成向量嵌入
generate_embeddings() {
    local part_file="$1"
    
    log "🔍 生成向量嵌入..."
    
    if [ -f "$EMBEDDER" ]; then
        python3 "$EMBEDDER" \
            --input "$part_file" \
            --output "$MEMORY_DIR/vectors.db" \
            --agent "$AGENT_NAME" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 向量嵌入完成"
        else
            log "❌ 向量嵌入失败"
        fi
    else
        log "⚠️ 嵌入器不存在：$EMBEDDER"
    fi
}

# 6. 更新 QMD 知识库
update_qmd() {
    log "📚 更新 QMD 知识库..."
    
    if command -v qmd &> /dev/null; then
        qmd update 2>&1 | tee -a "$LOG_FILE"
        log "✅ QMD 更新完成"
    else
        log "⚠️ QMD 未安装，跳过"
    fi
}

# 7. Git 自动提交
git_commit() {
    log "💾 Git 自动提交..."
    
    cd "$WORKSPACE"
    
    # 检查变更
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$changes" -gt 0 ]; then
        # 统计变更
        local added=$(git status --porcelain | grep -c "^A " || echo "0")
        local modified=$(git status --porcelain | grep -c "^ M" || echo "0")
        local deleted=$(git status --porcelain | grep -c "^ D" || echo "0")
        
        # 提交
        git add -A
        git commit -m "chore: session-memory自动更新（+$added ~$modified -$deleted）" \
            --author "miliger <miliger@openclaw.ai>" 2>&1 | tee -a "$LOG_FILE"
        
        log "✅ Git 提交完成（+$added ~$modified -$deleted）"
    else
        log "ℹ️ 无变更，跳过提交"
    fi
}

# 8. 统一检索接口
search() {
    local query="$1"
    
    log "🔍 检索查询：$query"
    
    # 优先使用向量检索
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        log "📊 使用向量检索..."
        
        if [ -f "$SEARCHER" ]; then
            python3 "$SEARCHER" \
                --query "$query" \
                --db "$MEMORY_DIR/vectors.db" \
                --agent "$AGENT_NAME" \
                --api-key "$OPENAI_API_KEY" 2>&1
            
            if [ $? -eq 0 ]; then
                return 0
            fi
        fi
    fi
    
    # 降级到 QMD 检索
    log "📊 降级到 QMD 检索..."
    
    if command -v qmd &> /dev/null; then
        qmd search "$query" -c memory
    else
        log "❌ 无可用检索方式"
        return 1
    fi
}

# 主流程
main() {
    # 1. 加载配置
    load_config
    
    # 2. 检查是否需要固化
    if should_flush; then
        # 3. 固化分片
        flush_tail
        
        # 4. 更新 QMD
        update_qmd
        
        # 5. Git 提交
        git_commit
    fi
    
    log "✅ Session-Memory Enhanced v4.0 完成"
    log "================================"
}

# 执行
main
```

---

## 🐍 Python 核心实现

### extractor.py（结构化提取器）

```python
#!/usr/bin/env python3
"""
结构化记忆提取器
功能：从会话分片提取结构化信息
创建时间：2026-03-09 19:35
作者：米粒儿
"""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
import openai
from datetime import datetime

class StructuredMemoryExtractor:
    """结构化记忆提取器"""
    
    def __init__(self, db_path: str, agent_name: str, api_key: str = None):
        self.db_path = Path(db_path)
        self.agent_name = agent_name
        self.api_key = api_key
        
        if api_key:
            openai.api_key = api_key
        
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
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
                embedding_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                confidence REAL DEFAULT 0.8
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_type 
            ON memories(agent, type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON memories(created_at DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_from_part(self, part_file: str) -> Dict[str, Any]:
        """从分片提取结构化记忆"""
        with open(part_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        content = self._concat_messages(messages)
        
        # 使用 LLM 提取
        insights = self._llm_extract(content)
        
        return insights
    
    def _concat_messages(self, messages: List[Dict]) -> str:
        """拼接消息内容"""
        text = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            text.append(f"[{role}] {content}")
        return "\n".join(text)
    
    def _llm_extract(self, content: str) -> Dict[str, Any]:
        """使用 LLM 提取结构化信息"""
        if not self.api_key:
            return self._rule_based_extract(content)
        
        try:
            prompt = f"""
请从以下对话中提取关键信息，以JSON格式返回：

{content[:2000]}

请提取以下类型的信息：
1. profile: 用户画像（姓名、职业、偏好等）
2. events: 重要事件（时间、地点、人物、事件）
3. knowledge: 知识点（学到的新知识）
4. decisions: 重要决策（做出的选择）
5. lessons: 经验教训（总结的经验）

返回格式：
{{
  "profile": {{...}},
  "events": [...],
  "knowledge": [...],
  "decisions": [...],
  "lessons": [...]
}}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"⚠️ LLM 提取失败：{e}")
            return self._rule_based_extract(content)
    
    def _rule_based_extract(self, content: str) -> Dict[str, Any]:
        """基于规则提取（降级方案）"""
        insights = {
            'profile': {},
            'events': [],
            'knowledge': [],
            'decisions': [],
            'lessons': []
        }
        
        # 简单规则提取
        lines = content.split('\n')
        
        for line in lines:
            # 检测决策
            if '决定' in line or '选择' in line:
                insights['decisions'].append({
                    'content': line,
                    'timestamp': datetime.now().isoformat()
                })
            
            # 检测知识点
            if '学到了' in line or '了解到' in line:
                insights['knowledge'].append({
                    'content': line,
                    'timestamp': datetime.now().isoformat()
                })
        
        return insights
    
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
                    json.dumps({
                        'source': 'session_memory',
                        'extracted_at': datetime.now().isoformat()
                    })
                ))
        
        conn.commit()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='结构化记忆提取器')
    parser.add_argument('--input', required=True, help='输入分片文件')
    parser.add_argument('--output', required=True, help='输出数据库')
    parser.add_argument('--agent', required=True, help='代理名称')
    parser.add_argument('--api-key', help='OpenAI API Key（可选）')
    
    args = parser.parse_args()
    
    extractor = StructuredMemoryExtractor(
        args.output, 
        args.agent, 
        args.api_key
    )
    
    insights = extractor.extract_from_part(args.input)
    extractor.save_to_db(insights)
    
    print(f"✅ 提取完成：{args.input}")

if __name__ == '__main__':
    main()
```

---

### embedder.py（向量嵌入器）

```python
#!/usr/bin/env python3
"""
向量嵌入器
功能：生成文本的向量嵌入
创建时间：2026-03-09 19:40
作者：米粒儿
"""

import argparse
import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict
import openai

class VectorEmbedder:
    """向量嵌入器"""
    
    def __init__(self, db_path: str, agent_name: str, api_key: str):
        self.db_path = Path(db_path)
        self.agent_name = agent_name
        openai.api_key = api_key
        
        self._init_db()
    
    def _init_db(self):
        """初始化向量数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建向量表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent 
            ON vectors(agent)
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成向量嵌入"""
        try:
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            embeddings = [item['embedding'] for item in response['data']]
            return embeddings
            
        except Exception as e:
            print(f"⚠️ 生成嵌入失败：{e}")
            return []
    
    def save_to_db(self, texts: List[str], embeddings: List[List[float]]):
        """保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for text, embedding in zip(texts, embeddings):
            # 转换为 numpy 数组再转为 bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            cursor.execute('''
                INSERT INTO vectors (agent, text, embedding, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                self.agent_name,
                text,
                embedding_bytes,
                json.dumps({'source': 'session_memory'})
            ))
        
        conn.commit()
        conn.close()
    
    def embed_part_file(self, part_file: str):
        """为分片文件生成嵌入"""
        with open(part_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        texts = []
        
        for msg in messages:
            content = msg.get('content', '')
            if content:
                texts.append(content)
        
        if texts:
            embeddings = self.generate_embeddings(texts)
            if embeddings:
                self.save_to_db(texts, embeddings)
                print(f"✅ 生成 {len(embeddings)} 个向量嵌入")

def main():
    parser = argparse.ArgumentParser(description='向量嵌入器')
    parser.add_argument('--input', required=True, help='输入分片文件')
    parser.add_argument('--output', required=True, help='输出数据库')
    parser.add_argument('--agent', required=True, help='代理名称')
    parser.add_argument('--api-key', required=True, help='OpenAI API Key')
    
    args = parser.parse_args()
    
    embedder = VectorEmbedder(args.output, args.agent, args.api_key)
    embedder.embed_part_file(args.input)
    
    print(f"✅ 嵌入完成：{args.input}")

if __name__ == '__main__':
    main()
```

---

### searcher.py（语义搜索器）

```python
#!/usr/bin/env python3
"""
语义搜索器
功能：向量检索 + 语义搜索
创建时间：2026-03-09 19:45
作者：米粒儿
"""

import argparse
import sqlite3
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import openai

class SemanticSearcher:
    """语义搜索器"""
    
    def __init__(self, db_path: str, agent_name: str, api_key: str):
        self.db_path = Path(db_path)
        self.agent_name = agent_name
        openai.api_key = api_key
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义搜索"""
        # 1. 生成查询向量
        query_embedding = self._get_query_embedding(query)
        
        if not query_embedding:
            return []
        
        # 2. 从数据库加载向量
        candidates = self._load_vectors()
        
        # 3. 计算相似度
        results = []
        for candidate in candidates:
            similarity = self._cosine_similarity(
                query_embedding, 
                candidate['embedding']
            )
            
            if similarity > 0.7:  # 阈值
                results.append({
                    'text': candidate['text'],
                    'similarity': similarity,
                    'metadata': candidate.get('metadata', {})
                })
        
        # 4. 排序返回
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询向量"""
        try:
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=[query]
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            print(f"⚠️ 获取查询向量失败：{e}")
            return []
    
    def _load_vectors(self) -> List[Dict]:
        """从数据库加载向量"""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT text, embedding, metadata 
            FROM vectors 
            WHERE agent = ?
            ORDER BY created_at DESC
            LIMIT 100
        ''', (self.agent_name,))
        
        results = []
        for row in cursor.fetchall():
            text, embedding_bytes, metadata = row
            
            # 转换 bytes 为 numpy 数组
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
            
            results.append({
                'text': text,
                'embedding': embedding,
                'metadata': json.loads(metadata) if metadata else {}
            })
        
        conn.close()
        return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        a = np.array(a)
        b = np.array(b)
        
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    parser = argparse.ArgumentParser(description='语义搜索器')
    parser.add_argument('--query', required=True, help='查询文本')
    parser.add_argument('--db', required=True, help='向量数据库')
    parser.add_argument('--agent', required=True, help='代理名称')
    parser.add_argument('--api-key', required=True, help='OpenAI API Key')
    parser.add_argument('--top-k', type=int, default=5, help='返回数量')
    
    args = parser.parse_args()
    
    searcher = SemanticSearcher(args.db, args.agent, args.api_key)
    results = searcher.search(args.query, args.top_k)
    
    print(f"🔍 找到 {len(results)} 个相关结果：")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 相似度：{result['similarity']:.2f}")
        print(f"   内容：{result['text'][:100]}...")

if __name__ == '__main__':
    main()
```

---

## 📋 配置文件

### unified.json（统一配置）

```json
{
  "version": "4.0.0",
  "description": "Session-Memory Enhanced 统一增强版",
  
  "flushIdleSeconds": 1800,
  "maxMessagesPerPart": 60,
  
  "features": {
    "structuredExtraction": false,
    "vectorSearch": false,
    "aiSummary": true,
    "gitBackup": true,
    "qmdUpdate": true
  },
  
  "openaiApiKey": "${OPENAI_API_KEY}",
  
  "python": {
    "enabled": false,
    "autoInstall": true,
    "requirements": "requirements.txt"
  },
  
  "search": {
    "strategy": "hybrid",
    "primaryEngine": "vector",
    "fallbackEngine": "qmd",
    "threshold": 0.7,
    "topK": 5
  }
}
```

---

## 🚀 安装和使用

### 1. 安装

```bash
# 从 ClawHub 安装（未来）
clawhub install session-memory-enhanced

# 或手动安装
cd /root/.openclaw/workspace/skills/session-memory-enhanced
bash scripts/install.sh
```

### 2. 配置

```bash
# 复制配置模板
cp config/unified.json.example config/unified.json

# 编辑配置
nano config/unified.json

# 启用高级功能（可选）
jq '.features.structuredExtraction = true' config/unified.json > tmp.json
mv tmp.json config/unified.json

jq '.features.vectorSearch = true' config/unified.json > tmp.json
mv tmp.json config/unified.json

# 配置 API Key
export OPENAI_API_KEY="your_key"
```

### 3. 安装 Python 依赖（可选）

```bash
cd /root/.openclaw/workspace/skills/session-memory-enhanced/python
pip3 install -r requirements.txt
```

### 4. 运行

```bash
# 自动模式（crontab）
crontab -e
# 添加：
# 0 * * * * /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 手动运行
bash /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 检索
python3 /root/.openclaw/workspace/skills/session-memory-enhanced/python/searcher.py \
    --query "查询关键词" \
    --db /root/.openclaw/workspace/memory/agents/main/vectors.db \
    --agent main \
    --api-key "your_key"
```

---

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
| **Python 集成** | ❌ | ✅（可选） |
| **资源占用** | 🟢 116K | 🟡 116K+ |

---

## 🎯 总结

**v4.0 统一版优势**：
1. ⭐ **功能完整** - 融合两大系统所有功能
2. ⭐ **向下兼容** - 不启用高级功能时与 v3.4 一致
3. ⭐ **灵活配置** - 可选择启用哪些功能
4. ⭐ **平滑升级** - 从 v3.4 无缝升级

**推荐使用场景**：
- ✅ 需要完整的记忆管理
- ✅ 需要语义搜索
- ✅ 需要结构化提取
- ✅ 个人或企业使用

**下一步**：
1. 测试 Python 组件
2. 优化性能
3. 发布到 ClawHub

---

**创建时间**：2026-03-09 19:50
**作者**：米粒儿
**版本**：v4.0.0
