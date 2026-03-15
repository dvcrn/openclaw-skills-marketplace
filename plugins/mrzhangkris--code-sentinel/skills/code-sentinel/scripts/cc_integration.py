#!/usr/bin/env python3
"""
OpenClaw Control Center 集成模块
"""

import json
from pathlib import Path
from typing import Dict, List


class ControlCenterIntegration:
    """控制台集成器"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace-panshi"
        self.cc_dir = self.workspace / "code-sentinel-results"
        self.cc_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_results(self, results: Dict, session_id: str = None) -> str:
        """上传审查结果到 Control Center"""
        if session_id:
            filename = f"result_{session_id}.json"
        else:
            from datetime import datetime
            filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.cc_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def get_results(self, limit: int = 10) -> List[Dict]:
        """获取最近的审查结果"""
        results = []
        for file in sorted(self.cc_dir.glob("result_*.json"), reverse=True)[:limit]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_filename"] = file.name
                    results.append(data)
            except:
                continue
        return results
    
    def delete_result(self, filename: str) -> bool:
        """删除单个结果"""
        filepath = self.cc_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def clear_all(self) -> int:
        """清除所有结果"""
        count = len(list(self.cc_dir.glob("result_*.json")))
        for file in self.cc_dir.glob("result_*.json"):
            file.unlink()
        return count
