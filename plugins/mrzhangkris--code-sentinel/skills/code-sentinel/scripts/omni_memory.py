#!/usr/bin/env python3
"""
OmniMemory 学习模块 - 基于用户编码风格自适应优化
"""

import json
from pathlib import Path
from datetime import datetime


class OmniMemoryAdapter:
    """编码风格学习与适应"""
    
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.home() / ".openclaw" / "workspace-panshi"
        self.memory_file = self.workspace / "code-sentinel" / "omni_memory.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """加载记忆"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "coding_preferences": {},
            "false_positive_cases": [],
            "learning_log": []
        }
    
    def learn_from_files(self, files: list):
        """从文件学习编码风格"""
        for file_path in files:
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                lang = self._detect_language(file_path)
                
                # 记录命名偏好
                if lang in ["python", "javascript"]:
                    self._analyze_naming_pattern(content, lang)
                
                # 记录代码复杂度偏好
                if lang == "python":
                    self._analyze_complexity(content)
                    
            except Exception as e:
                continue
        
        self.memory["last_updated"] = datetime.now().isoformat()
        self._save_memory()
    
    def _analyze_naming_pattern(self, content: str, lang: str):
        """分析命名模式"""
        if lang == "python":
            # 检查变量命名
            import re
            variable_pattern = r"var\s+(\w+)|([a-z_]+)\s*[:=]"
            matches = re.findall(variable_pattern, content)
            for match in matches:
                var_name = match[0] or match[1]
                if var_name and len(var_name) > 2:
                    self._record_preference("naming", "python", var_name[:2])
        
        elif lang == "javascript":
            # 检查驼峰/下划线
            import re
            camel_pattern = r"(?:const|let|var)\s+([a-z][a-zA-Z]+)"
            matches = re.findall(camel_pattern, content)
            for match in matches:
                if any(c.isupper() for c in match[1:]):
                    self._record_preference("naming", "javascript", "camelCase")
    
    def _analyze_complexity(self, content: str):
        """分析复杂度偏好"""
        import re
        # 检查函数长度
        func_pattern = r"def\s+(\w+)\(.*?\):\n((?:\s+.*\n)+)"
        matches = re.findall(func_pattern, content)
        for name, body in matches:
            lines = len([l for l in body.split("\n") if l.strip()])
            if lines > 50:
                self._record_preference("complexity", "max_function_lines", 50)
    
    def _record_preference(self, category: str, lang: str, pattern: str):
        """记录偏好"""
        key = f"{category}_{lang}"
        if key not in self.memory["coding_preferences"]:
            self.memory["coding_preferences"][key] = []
        
        if pattern not in self.memory["coding_preferences"][key]:
            self.memory["coding_preferences"][key].append(pattern)
    
    def _detect_language(self, file_path: str) -> str:
        """检测语言"""
        suffix = Path(file_path).suffix.lower()
        mappings = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
        }
        return mappings.get(suffix, "unknown")
    
    def _save_memory(self):
        """保存记忆"""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def get_style_suggestions(self, lang: str) -> list:
        """获取风格建议"""
        suggestions = []
        
        prefs = self.memory.get("coding_preferences", {})
        
        if f"naming_{lang}" in prefs:
            patterns = prefs[f"naming_{lang}"]
            if "camelCase" in patterns:
                suggestions.append(f"建议在 {lang} 中使用 camelCase 命名")
            elif "_" in str(patterns):
                suggestions.append(f"建议在 {lang} 中使用下划线命名")
        
        if f"complexity_{lang}" in prefs:
            max_lines = prefs[f"complexity_{lang}"][0] if prefs[f"complexity_{lang}"] else 30
            suggestions.append(f"建议函数行数不超过 {max_lines}")
        
        return suggestions
    
    def log_false_positive(self, case: dict):
        """记录误报"""
        self.memory["false_positive_cases"].append({
            **case,
            "timestamp": datetime.now().isoformat()
        })
        self.memory["last_updated"] = datetime.now().isoformat()
        self._save_memory()
        self.memory["learning_log"].append(f"False positive logged: {case.get('type')}")


# 全局实例
_omni = None


def get_omni_memory() -> OmniMemoryAdapter:
    """获取全局实例"""
    global _omni
    if _omni is None:
        _omni = OmniMemoryAdapter()
    return _omni
