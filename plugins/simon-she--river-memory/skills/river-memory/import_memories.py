#!/usr/bin/env python3
"""导入历史记忆到向量库"""
import json
import os
import glob
import requests
import numpy as np

MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/memory/vector-memory.json")
OLLAMA_URL = "http://localhost:11434"
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

def ensure_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def load_memories():
    ensure_dir()
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f).get('memories', [])

def save_memories(memories):
    ensure_dir()
    with open(MEMORY_FILE, 'w') as f:
        json.dump({'memories': memories}, f, indent=2, ensure_ascii=False)

def get_embedding(text):
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", 
                        json={'model': 'nomic-embed-text', 'prompt': text[:2000]},
                        timeout=60)
    resp.raise_for_status()
    return resp.json()['embedding']

def store(content, category='imported'):
    emb = get_embedding(content)
    memories = load_memories()
    memory = {
        'id': 'import_' + str(len(memories)),
        'content': content,
        'category': category,
        'importance': 5,
        'embedding': emb,
        'createdAt': '2026-03-08T00:00:00'
    }
    memories.append(memory)
    save_memories(memories)
    return len(memories)

# 要导入的记忆文件
files_to_import = [
    (f"{WORKSPACE}/MEMORY.md", "长期记忆"),
    (f"{WORKSPACE}/memory/2026-03-08.md", "今日日志"),
    (f"{WORKSPACE}/memory/2026-03-05.md", "历史日志"),
    (f"{WORKSPACE}/memory/2026-03-04.md", "历史日志"),
    (f"{WORKSPACE}/SOUL.md", "人格定义"),
    (f"{WORKSPACE}/USER.md", "用户信息"),
    (f"{WORKSPACE}/IDENTITY.md", "身份定义"),
]

print("📥 开始导入历史记忆...\n")

total_stored = 0
for filepath, category in files_to_import:
    if not os.path.exists(filepath):
        print(f"⏭️ 跳过: {filepath} (不存在)")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 分块处理（避免超长）
    import re
    # 按标题分割
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        if i == 0:
            text = section.strip()
        else:
            text = "## " + section.strip()
        
        if len(text) < 10:
            continue
            
        try:
            count = store(text, category)
            print(f"✅ [{count}] {text[:50]}...")
            total_stored += 1
        except Exception as e:
            print(f"❌ 失败: {text[:30]}... - {e}")

print(f"\n📊 总计导入: {total_stored} 条")
print(f"📁 记忆库: {MEMORY_FILE}")
