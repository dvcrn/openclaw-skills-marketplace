#!/usr/bin/env python3
"""
语义搜索器 v1.0
功能：向量检索 + 语义搜索（吸收 memu-engine 的检索优势）
创建时间：2026-03-09 19:55
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
    """语义搜索器 - 吸收 memu-engine 的向量检索优势"""
    
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
