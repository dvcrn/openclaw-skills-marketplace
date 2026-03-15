#!/usr/bin/env python3
"""
Session记忆同步系统
多Session间记忆共享
"""

import os
import json
import glob
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
SHARED_FILE = os.path.join(MEMORY_DIR, "shared", "session_sync.json")

def get_all_sessions():
    """获取所有Session"""
    sessions = []
    
    # 短期记忆目录
    short_dir = os.path.join(MEMORY_DIR, "short")
    if os.path.exists(short_dir):
        for f in glob.glob(os.path.join(short_dir, "*.json")):
            session_id = os.path.basename(f).replace(".json", "")
            sessions.append({
                "id": session_id,
                "type": "short",
                "file": f
            })
    
    return sessions

def sync_to_shared(memory_type="long"):
    """同步到共享记忆"""
    sessions = get_all_sessions()
    shared_data = {
        "synced_at": datetime.now().isoformat(),
        "sessions": {},
        "merged": []
    }
    
    # 合并长期记忆
    long_file = os.path.join(MEMORY_DIR, "long", "long.json")
    if os.path.exists(long_file):
        with open(long_file) as f:
            shared_data["merged"] = json.load(f)
    
    # 收集所有Session的摘要
    for session in sessions:
        with open(session["file"]) as f:
            mems = json.load(f)
            if mems:
                shared_data["sessions"][session["id"]] = {
                    "count": len(mems),
                    "last_memory": mems[-1].get("content", "")[:50] if mems else ""
                }
    
    # 保存
    os.makedirs(os.path.dirname(SHARED_FILE), exist_ok=True)
    with open(SHARED_FILE, 'w') as f:
        json.dump(shared_data, f, ensure_ascii=False, indent=2)
    
    return len(sessions)

def get_shared_context(session_id=None):
    """获取共享上下文"""
    if os.path.exists(SHARED_FILE):
        with open(SHARED_FILE) as f:
            data = json.load(f)
            
            if session_id:
                # 获取特定Session的信息
                return data.get("sessions", {}).get(session_id, {})
            
            return data
    
    return {}

def cross_session_search(query):
    """跨Session搜索"""
    results = []
    
    # 搜索所有短期记忆
    short_dir = os.path.join(MEMORY_DIR, "short")
    for f in glob.glob(os.path.join(short_dir, "*.json")):
        session_id = os.path.basename(f).replace(".json", "")
        
        with open(f) as fp:
            memories = json.load(fp)
            for mem in memories:
                content = mem.get("content", "").lower()
                if query.lower() in content:
                    results.append({
                        "session": session_id,
                        "content": mem.get("content", ""),
                        "time": mem.get("timestamp", "")
                    })
    
    return results

# 测试
if __name__ == "__main__":
    print("=== Session同步系统 ===")
    
    sessions = get_all_sessions()
    print(f"活跃Session: {len(sessions)}")
    for s in sessions:
        print(f"  - {s['id']} ({s['type']})")
    
    print(f"\n同步到共享...")
    count = sync_to_shared()
    print(f"已同步 {count} 个Session")
    
    print(f"\n共享上下文:")
    ctx = get_shared_context()
    print(f"  最后同步: {ctx.get('synced_at', '从未')}")
    print(f"  记忆数: {len(ctx.get('merged', []))}")
