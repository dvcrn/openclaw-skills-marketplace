#!/usr/bin/env python3
"""
向量嵌入器 v1.0
功能：生成文本的向量嵌入（吸收 memu-engine 的向量检索优势）
创建时间：2026-03-09 19:50
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
    """向量嵌入器 - 吸收 memu-engine 的向量检索优势"""
    
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
