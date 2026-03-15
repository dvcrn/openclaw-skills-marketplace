#!/usr/bin/env python3
"""随机性监控模块"""

import json
import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List

from config import ConfigManager


class RandomnessMonitor:
    """随机性监控器"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # 数据库路径
        db_path = self.config.get("history_db", "history.db")
        self.db_path = Path(db_path)
    
    def analyze_trends(self, days: int = 7) -> Dict:
        """分析随机性趋势
        
        Args:
            days: 分析天数
        
        Returns:
            趋势分析报告
        """
        if not self.db_path.exists():
            return {"error": "数据库不存在"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询指定天数内的记录
        cursor.execute("""
            SELECT prompt, output, timestamp, temperature
            FROM history 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
        """.format(days))
        
        records = cursor.fetchall()
        conn.close()
        
        if len(records) < 2:
            return {
                "error": "数据不足，至少需要2条记录",
                "current_records": len(records)
            }
        
        # 计算相似度趋势
        trends = []
        for i in range(0, len(records)-1, 2):
            if i+1 < len(records):
                sim = self._calculate_similarity(
                    records[i][1], 
                    records[i+1][1]
                )
                trends.append({
                    "date": records[i][2][:10],  # 只取日期部分
                    "similarity": round(sim, 2),
                    "temperature": records[i][3]
                })
        
        if not trends:
            return {
                "error": "无法计算趋势（记录数不足）",
                "current_records": len(records)
            }
        
        # 计算统计指标
        similarities = [t["similarity"] for t in trends]
        avg_sim = sum(similarities) / len(similarities)
        
        # 判断趋势
        if avg_sim > 70:
            trend_status = "稳定"
        elif avg_sim > 50:
            trend_status = "轻微波动"
        else:
            trend_status = "波动较大"
        
        return {
            "period_days": days,
            "total_records": len(records),
            "average_similarity": round(avg_sim, 2),
            "trend": trend_status,
            "details": trends[-10:] if len(trends) > 10 else trends,  # 最多返回10条
            "min_similarity": round(min(similarities), 2),
            "max_similarity": round(max(similarities), 2)
        }
    
    def detect_anomalies(self, threshold: float = 50.0, limit: int = 100) -> List[Dict]:
        """检测异常输出
        
        Args:
            threshold: 异常阈值（相似度低于此值为异常）
            limit: 检查的记录数
        
        Returns:
            异常记录列表
        """
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, prompt, output, timestamp
            FROM history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        records = cursor.fetchall()
        conn.close()
        
        if len(records) < 2:
            return []
        
        anomalies = []
        
        for i in range(len(records)-1):
            sim = self._calculate_similarity(
                records[i][2], 
                records[i+1][2]
            )
            
            if sim < threshold:
                anomalies.append({
                    "id": records[i][0],
                    "timestamp": records[i][3],
                    "prompt": records[i][1][:50] + "..." if len(records[i][1]) > 50 else records[i][1],
                    "similarity": round(sim, 2)
                })
        
        return anomalies
    
    def export_report(self, output_path: str = "randomness_report.json") -> str:
        """导出监控报告
        
        Args:
            output_path: 输出路径
        
        Returns:
            报告文件路径
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "trends": self.analyze_trends(),
            "anomalies": self.detect_anomalies(),
            "summary": self._generate_summary()
        }
        
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output_file.absolute())
    
    def _generate_summary(self) -> Dict:
        """生成摘要"""
        trends = self.analyze_trends()
        anomalies = self.detect_anomalies()
        
        if "error" in trends:
            return {
                "status": "数据不足",
                "message": trends["error"]
            }
        
        return {
            "total_records": trends["total_records"],
            "average_similarity": trends["average_similarity"],
            "anomaly_count": len(anomalies),
            "trend": trends["trend"],
            "status": "健康" if trends["average_similarity"] > 70 else "需要关注"
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio() * 100
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.db_path.exists():
            return {
                "total_records": 0,
                "db_exists": False
            }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM history")
        total = cursor.fetchone()[0]
        
        # 最近24小时记录数
        cursor.execute("""
            SELECT COUNT(*) FROM history
            WHERE timestamp >= datetime('now', '-1 day')
        """)
        recent_24h = cursor.fetchone()[0]
        
        # 平均温度
        cursor.execute("SELECT AVG(temperature) FROM history")
        avg_temp = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_records": total,
            "recent_24h": recent_24h,
            "average_temperature": round(avg_temp, 2),
            "db_exists": True
        }
