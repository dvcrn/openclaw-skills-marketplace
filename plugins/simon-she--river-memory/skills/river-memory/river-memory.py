#!/usr/bin/env python3
"""
River Memory - 向量记忆 CLI
用 Ollama nomic-embed-text 实现语义搜索
"""
import json
import os
import requests
import numpy as np
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/memory/vector-memory.json")
OLLAMA_URL = "http://localhost:11434"

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
    """调用 Ollama 获取 embedding"""
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", 
                        json={'model': 'nomic-embed-text', 'prompt': text},
                        timeout=30)
    resp.raise_for_status()
    return resp.json()['embedding']

def cosine_sim(a, b):
    """计算余弦相似度"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def store(content, category='other', importance=5):
    """存储记忆"""
    print(f"📝 Storing: {content[:50]}...")
    emb = get_embedding(content)
    memories = load_memories()
    memory = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S') + str(hash(content))[:6],
        'content': content,
        'category': category,
        'importance': importance,
        'embedding': emb,
        'createdAt': datetime.now().isoformat()
    }
    memories.append(memory)
    save_memories(memories)
    print(f"✅ Stored! Total: {len(memories)}")
    return memory['id']

def search(query, limit=5, threshold=0.3):
    """语义搜索"""
    print(f"🔍 Searching: {query}")
    query_emb = get_embedding(query)
    memories = load_memories()
    
    results = []
    for m in memories:
        sim = cosine_sim(query_emb, m['embedding'])
        if sim >= threshold:
            results.append({**m, 'similarity': round(sim, 3)})
    
    results.sort(key=lambda x: x['similarity'], reverse=True)
    results = results[:limit]
    
    print(f"📊 Found {len(results)} results:")
    for r in results:
        print(f"  [{r['similarity']:.2f}] {r['content'][:60]}...")
    return results

def list_memories(limit=20):
    """列出记忆"""
    memories = load_memories()
    print(f"📚 Total: {len(memories)} memories")
    for m in memories[-limit:][::-1]:
        print(f"  [{m['category']}] {m['content'][:50]}...")
    return memories

def delete(memory_id):
    """删除记忆"""
    memories = load_memories()
    before = len(memories)
    memories = [m for m in memories if m['id'] != memory_id]
    if len(memories) == before:
        print(f"❌ Not found: {memory_id}")
        return False
    save_memories(memories)
    print(f"✅ Deleted! Remaining: {len(memories)}")
    return True

if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'store':
        content = sys.argv[2] if len(sys.argv) > 2 else input("Content: ")
        store(content)
    elif cmd == 'search':
        query = sys.argv[2] if len(sys.argv) > 2 else input("Query: ")
        search(query)
    elif cmd == 'list':
        list_memories()
    elif cmd == 'delete':
        if len(sys.argv) > 2:
            delete(sys.argv[2])
        else:
            print("Usage: river-memory.py delete <id>")
    else:
        print("Usage: river-memory.py <store|search|list|delete> [args]")
