#!/usr/bin/env python3
"""
夏娃记忆系统 v0.1.0
三层记忆系统：短期/中期/长期
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ========== 配置 ==========
CONFIG = {
    "storage_dir": os.path.expanduser("~/.openclaw/workspace/memory"),
    "short_ttl": 24 * 3600,      # 24小时
    "medium_ttl": 7 * 24 * 3600,  # 7天
    "short_max_size": 50,          # 短期记忆最大条数
    "promote_threshold": 7,        # 重要性>=7升级到长期
    "sleep_threshold": 30,          # 30天未访问进入沉睡
}

# ========== 路径 ==========
SHORT_DIR = os.path.join(CONFIG["storage_dir"], "short")
MEDIUM_DIR = os.path.join(CONFIG["storage_dir"], "medium")
LONG_DIR = os.path.join(CONFIG["storage_dir"], "long")

for d in [SHORT_DIR, MEDIUM_DIR, LONG_DIR]:
    os.makedirs(d, exist_ok=True)

# ========== 工具函数 ==========
def now():
    return datetime.now()

def now_iso():
    return datetime.now().isoformat()

def uuid4():
    return str(uuid.uuid4())[:8]

# ========== 记忆类 ==========
class Memory:
    def __init__(self, content: str, importance: int = 5, 
                 session_id: str = None, mem_type: str = "short"):
        self.id = f"{mem_type[0]}_{uuid4()}"
        self.content = content
        self.importance = importance
        self.session_id = session_id or "unknown"
        self.type = mem_type
        self.created_at = now_iso()
        self.accessed_at = now_iso()
        self.accessed_count = 0
        self.state = "active"
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "importance": self.importance,
            "session_id": self.session_id,
            "type": self.type,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "accessed_count": self.accessed_count,
            "state": self.state
        }
    
    @classmethod
    def from_dict(cls, data):
        m = cls(data["content"], data["importance"], data["session_id"], data["type"])
        m.id = data["id"]
        m.created_at = data["created_at"]
        m.accessed_at = data.get("accessed_at", data["created_at"])
        m.accessed_count = data.get("accessed_count", 0)
        m.state = data.get("state", "active")
        return m

# ========== 存储层 ==========
def save_memory(memory: Memory):
    """保存记忆到对应目录"""
    if memory.type == "short":
        path = os.path.join(SHORT_DIR, f"{memory.session_id}.json")
    elif memory.type == "medium":
        path = os.path.join(MEDIUM_DIR, f"{memory.type}.json")
    else:
        path = os.path.join(LONG_DIR, f"{memory.type}.json")
    
    # 读取现有
    memories = load_memories(memory.type, memory.session_id)
    
    # 添加或更新
    found = False
    for i, m in enumerate(memories):
        if m.id == memory.id:
            memories[i] = memory.to_dict()
            found = True
            break
    if not found:
        memories.append(memory.to_dict())
    
    # 保存
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def load_memories(mem_type: str, session_id: str = None) -> List[Dict]:
    """加载记忆"""
    if mem_type == "short":
        path = os.path.join(SHORT_DIR, f"{session_id}.json")
    elif mem_type == "medium":
        path = os.path.join(MEDIUM_DIR, "medium.json")
    else:
        path = os.path.join(LONG_DIR, "long.json")
    
    if not os.path.exists(path):
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ========== 核心功能 ==========
def add_memory(content: str, importance: int = 5, 
               session_id: str = None, mem_type: str = "short") -> Memory:
    """添加记忆"""
    memory = Memory(content, importance, session_id, mem_type)
    save_memory(memory)
    return memory

def get_short_term(session_id: str, limit: int = 10) -> List[Dict]:
    """获取短期记忆"""
    memories = load_memories("short", session_id)
    return memories[-limit:]

def get_medium_term(limit: int = 20) -> List[Dict]:
    """获取中期记忆"""
    return load_memories("medium", "all")[-limit:]

def get_long_term(limit: int = 20) -> List[Dict]:
    """获取长期记忆"""
    return load_memories("long", "all")[-limit:]

def get_context(session_id: str) -> str:
    """获取完整上下文"""
    context = []
    
    # 短期记忆
    short = get_short_term(session_id, 5)
    if short:
        context.append("【最近对话】")
        for m in short:
            context.append(f"- {m['content'][:60]}")
    
    # 长期记忆
    long = get_long_term(5)
    if long:
        context.append("\n【重要记忆】")
        for m in long:
            if m["importance"] >= 7:
                context.append(f"- {m['content']}")
    
    return "\n".join(context) if context else "无相关记忆"

def cleanup_expired():
    """清理过期记忆"""
    now_dt = datetime.now()
    
    # 清理短期记忆
    for f in os.listdir(SHORT_DIR):
        if f.endswith(".json"):
            path = os.path.join(SHORT_DIR, f)
            with open(path, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # 过滤24小时内的
            valid = []
            for m in memories:
                created = datetime.fromisoformat(m["created_at"])
                if (now_dt - created).total_seconds() < CONFIG["short_ttl"]:
                    valid.append(m)
            
            # 超过容量限制
            if len(valid) > CONFIG["short_max_size"]:
                valid = valid[-CONFIG["short_max_size"]:]
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(valid, f, ensure_ascii=False, indent=2)
    
    # 清理过期中期记忆
    medium_path = os.path.join(MEDIUM_DIR, "medium.json")
    if os.path.exists(medium_path):
        with open(medium_path, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        valid = []
        for m in memories:
            created = datetime.fromisoformat(m["created_at"])
            if (now_dt - created).total_seconds() < CONFIG["medium_ttl"]:
                # 检查是否升级
                if m["importance"] >= CONFIG["promote_threshold"]:
                    # 升级到长期
                    m["type"] = "long"
                    long_path = os.path.join(LONG_DIR, "long.json")
                    long_mem = json.load(open(long_path, 'r', encoding='utf-8')) if os.path.exists(long_path) else []
                    long_mem.append(m)
                    with open(long_path, 'w', encoding='utf-8') as f:
                        json.dump(long_mem, f, ensure_ascii=False, indent=2)
                else:
                    valid.append(m)
        
        with open(medium_path, 'w', encoding='utf-8') as f:
            json.dump(valid, f, ensure_ascii=False, indent=2)
    
    return True

# ========== CLI ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("夏娃记忆系统 v0.1.0")
        print("用法:")
        print("  add <内容> [重要性] [session_id]")
        print("  get_context <session_id>")
        print("  short <session_id> [limit]")
        print("  medium [limit]")
        print("  long [limit]")
        print("  cleanup")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        content = sys.argv[2]
        importance = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        session_id = sys.argv[4] if len(sys.argv) > 4 else "cli"
        
        # 自动判断类型
        if importance >= 7:
            mem_type = "long"
        elif importance >= 4:
            mem_type = "medium"
        else:
            mem_type = "short"
        
        m = add_memory(content, importance, session_id, mem_type)
        print(f"✅ 添加成功 [{m.type}] ID: {m.id}")
    
    elif cmd == "get_context":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "cli"
        print(get_context(session_id))
    
    elif cmd == "short":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "cli"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        for m in get_short_term(session_id, limit):
            print(f"[{m['created_at'][-8:]}] {m['content'][:50]}")
    
    elif cmd == "medium":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        for m in get_medium_term(limit):
            print(f"[{m['importance']}] {m['content'][:50]}")
    
    elif cmd == "long":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        for m in get_long_term(limit):
            print(f"[{m['importance']}] {m['content'][:50]}")
    
    elif cmd == "cleanup":
        cleanup_expired()
        print("✅ 清理完成")
    
    else:
        print(f"未知命令: {cmd}")
