#!/usr/bin/env python3
"""
OpenClaw 进化集成模块 - 持续优化检测规则
"""

import json
from pathlib import Path
from datetime import datetime


class CodeSentinelEvolution:
    """Code Sentinel 自我进化"""
    
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.home() / ".openclaw" / "workspace-panshi"
        self.evolution_file = self.workspace / "code-sentinel" / "evolution.json"
        self.evolution_file.parent.mkdir(parents=True, exist_ok=True)
        self.evolution = self._load_evolution()
    
    def _load_evolution(self) -> dict:
        """加载进化记录"""
        if self.evolution_file.exists():
            try:
                with open(self.evolution_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "created_at": datetime.now().isoformat(),
            "last_evolution": datetime.now().isoformat(),
            "evolution_count": 0,
            "rules": {
                "security": [],
                "performance": [],
                "quality": [],
                "architecture": []
            },
            "feedback_log": []
        }
    
    def add_rule(self, category: str, rule: dict):
        """添加新规则"""
        if category in self.evolution["rules"]:
            self.evolution["rules"][category].append({
                **rule,
                "added_at": datetime.now().isoformat()
            })
            self._save_evolution()
    
    def add_feedback(self, feedback: dict):
        """添加反馈"""
        self.evolution["feedback_log"].append({
            **feedback,
            "timestamp": datetime.now().isoformat()
        })
        self.evolution["last_evolution"] = datetime.now().isoformat()
        self._save_evolution()
    
    def evolve(self):
        """触发进化"""
        self.evolution["evolution_count"] += 1
        self.evolution["last_evolution"] = datetime.now().isoformat()
        self._save_evolution()
    
    def _save_evolution(self):
        """保存进化记录"""
        with open(self.evolution_file, "w", encoding="utf-8") as f:
            json.dump(self.evolution, f, indent=2, ensure_ascii=False)
    
    def get_rules(self, category: str = None) -> dict:
        """获取规则"""
        if category:
            return self.evolution["rules"].get(category, [])
        return self.evolution["rules"]
    
    def export_for_evolution_trigger(self) -> dict:
        """导出给 evolution_trigger"""
        return {
            "domain": "coding",
            "category": "coding",
            "content": json.dumps(self.evolution, ensure_ascii=False),
            "importance": 0.7
        }


# 全局实例
_evolution = None


def get_code_sentinel_evolution() -> CodeSentinelEvolution:
    """获取全局实例"""
    global _evolution
    if _evolution is None:
        _evolution = CodeSentinelEvolution()
    return _evolution
