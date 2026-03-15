#!/usr/bin/env python3
"""一致性检查模块"""

import sqlite3
import time
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from statistics import stdev
from typing import Dict, List, Optional

from ai_client import get_client
from config import ConfigManager


class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # 初始化数据库
        db_path = self.config.get("history_db", "history.db")
        self.db_path = Path(db_path)
        self._init_db()
        
        # AI客户端
        provider = self.config.get("api_provider", "mock")
        self.ai_client = get_client(provider)
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                output TEXT NOT NULL,
                temperature REAL,
                seed INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON history(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_seed 
            ON history(seed)
        """)
        
        conn.commit()
        conn.close()
    
    def check_consistency(
        self, 
        prompt: str, 
        samples: int = 3,
        threshold: float = 80.0,
        temperature: float = None
    ) -> Dict:
        """检查多次输出的一致性
        
        Args:
            prompt: 输入提示词
            samples: 采样次数（默认3次）
            threshold: 一致性阈值（默认80%）
            temperature: 温度参数（None则使用配置）
        
        Returns:
            一致性检查结果
        """
        if samples < 2:
            raise ValueError("采样次数至少为2")
        
        # 获取温度
        if temperature is None:
            temperature = self.config.get("temperature", 0.5)
        
        # 多次采样
        outputs = []
        start_time = time.time()
        
        for i in range(samples):
            output = self.ai_client.generate(prompt, temperature=temperature)
            outputs.append(output)
            
            # 保存到历史
            self._save_history(prompt, output, temperature)
        
        # 计算一致性评分
        scores = []
        for i in range(len(outputs)):
            for j in range(i+1, len(outputs)):
                score = self._calculate_similarity(outputs[i], outputs[j])
                scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # 计算统计指标
        min_score = min(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        std_score = stdev(scores) if len(scores) > 1 else 0.0
        
        elapsed_time = time.time() - start_time
        
        return {
            "consistency_score": round(avg_score, 2),
            "passed": avg_score >= threshold,
            "samples": samples,
            "threshold": threshold,
            "temperature": temperature,
            "elapsed_time": round(elapsed_time, 2),
            "details": {
                "min": round(min_score, 2),
                "max": round(max_score, 2),
                "std": round(std_score, 2)
            },
            "outputs_preview": [
                o[:100] + "..." if len(o) > 100 else o 
                for o in outputs
            ]
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（使用difflib）"""
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio() * 100
    
    def _save_history(self, prompt: str, output: str, temperature: float, seed: int = None):
        """保存到历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO history (prompt, output, temperature, seed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (prompt, output, temperature, seed, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史记录
        
        Args:
            limit: 返回数量限制
        
        Returns:
            历史记录列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, prompt, output, temperature, seed, timestamp
            FROM history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "id": row[0],
                "prompt": row[1],
                "output": row[2][:100] + "..." if len(row[2]) > 100 else row[2],
                "temperature": row[3],
                "seed": row[4],
                "timestamp": row[5]
            })
        
        conn.close()
        return records
    
    def clear_history(self, days: int = None):
        """清理历史记录
        
        Args:
            days: 清理多少天前的数据（None则清空所有）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if days is None:
            cursor.execute("DELETE FROM history")
        else:
            cursor.execute("""
                DELETE FROM history
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
        
        conn.commit()
        conn.close()


# ========== 顶层函数包装器（兼容test.sh）==========

def check_consistency(outputs: List[str], threshold: float = 80.0) -> Dict:
    """检查输出列表的一致性（包装器）
    
    Args:
        outputs: 输出文本列表
        threshold: 一致性阈值（默认80%）
    
    Returns:
        dict: 包含average_similarity, consistency_level等
    """
    if not outputs or len(outputs) < 2:
        return {
            "average_similarity": 0.0,
            "consistency_level": "数据不足",
            "details": {}
        }
    
    # 计算两两相似度
    scores = []
    for i in range(len(outputs)):
        for j in range(i+1, len(outputs)):
            score = SequenceMatcher(None, outputs[i], outputs[j]).ratio() * 100
            scores.append(score)
    
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # 确定一致性等级
    if avg_score >= 95:
        level = "优秀"
    elif avg_score >= 85:
        level = "良好"
    elif avg_score >= 70:
        level = "一般"
    else:
        level = "较差"
    
    return {
        "average_similarity": round(avg_score, 2),
        "consistency_level": level,
        "passed": avg_score >= threshold,
        "threshold": threshold,
        "details": {
            "min": round(min(scores), 2) if scores else 0.0,
            "max": round(max(scores), 2) if scores else 0.0,
            "std": round(stdev(scores), 2) if len(scores) > 1 else 0.0
        }
    }
