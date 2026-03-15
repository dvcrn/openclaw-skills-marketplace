#!/usr/bin/env python3
"""
结构化记忆提取器 v1.0
功能：从会话分片提取结构化信息（用户画像、事件、知识、决策、经验）
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
