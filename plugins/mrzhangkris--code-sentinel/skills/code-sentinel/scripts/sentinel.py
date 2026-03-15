#!/usr/bin/env python3
"""
智能代码审查系统 - Code Sentinel v0.1
四维一体：安全 + 性能 + 质量 + 架构
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 获取当前脚本目录
SCRIPT_DIR = Path(__file__).parent

# 导入检测器模块（使用相对路径）
sys.path.insert(0, str(SCRIPT_DIR))

# 导入所有检测器
from security.sql_injection import SQLInjectionDetector
from security.xss_detector import XSSDetector
from security.path_traversal import PathTraversalDetector
from security.command_injection import CommandInjectionDetector
from performance.memory_leak import MemoryLeakDetector
from performance.complexity import ComplexityAnalyzer

# 多语言支持
from languages.abstract import JavaDetector, GoDetector, RustDetector

# Control Center 集成
from cc_integration import ControlCenterIntegration

# OmniMemory 学习
from omni_memory import get_omni_memory

# 进化集成
from evolution import get_code_sentinel_evolution


class CodeSentinel:
    """智能代码审查系统核心引擎"""
    
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.reports = {
            "security": [],
            "performance": [],
            "quality": [],
            "architecture": [],
            "summary": {}
        }
        self.cc = ControlCenterIntegration()
        self.omni = get_omni_memory()
        self.evolution = get_code_sentinel_evolution()
        
    def scan(self, rules: list = None) -> dict:
        """运行审查"""
        print(f"🔍 开始审查: {self.target_dir}")
        
        if not rules or "security" in rules:
            self._scan_security()
        if not rules or "performance" in rules:
            self._scan_performance()
        if not rules or "quality" in rules:
            self._scan_quality()
        if not rules or "architecture" in rules:
            self._scan_architecture()
        
        self._generate_summary()
        return self.reports
    
    def _scan_security(self):
        """安全检测入口"""
        print("🛡️  安全检测...")
        all_issues = []
        
        for detector_class in [SQLInjectionDetector, XSSDetector, PathTraversalDetector, CommandInjectionDetector]:
            detector = detector_class()
            if self.target_dir.is_file():
                all_issues.extend(detector.scan_file(self.target_dir))
            else:
                all_issues.extend(detector.scan_directory(self.target_dir))
        
        self.reports["security"] = all_issues
    
    def _scan_performance(self):
        """性能检测入口"""
        print("⚡ 性能检测...")
        for detector_class in [MemoryLeakDetector, ComplexityAnalyzer]:
            detector = detector_class()
            if self.target_dir.is_file():
                issues = detector.scan_file(self.target_dir)
            else:
                issues = detector.scan_directory(self.target_dir)
            self.reports["performance"].extend(issues)
    
    def _scan_quality(self):
        """质量检测入口（占位）"""
        print("📊 质量检测...")
        self.reports["quality"] = []
    
    def _scan_architecture(self):
        """架构检测入口（占位）"""
        print("🏗️  架构检测...")
        self.reports["architecture"] = []
    
    def _generate_summary(self):
        """生成审查总结"""
        total_issues = sum(len(v) for k, v in self.reports.items() if k != "summary")
        
        # 记录 OmniMemory
        self.omni.learn_from_files([str(f) for f in self.target_dir.rglob("*") if f.is_file()])
        
        # 记录反馈日志
        for category, issues in self.reports.items():
            if category != "summary":
                for issue in issues:
                    self.evolution.add_feedback({
                        "type": issue["type"],
                        "file": issue["file"],
                        "line": issue["line"],
                        "feedback": "positive"
                    })
        
        self.evolution.evolve()
        
        self.reports["summary"] = {
            "total_issues": total_issues,
            "timestamp": datetime.now().isoformat(),
            "target": str(self.target_dir)
        }
    
    def output_json(self, output_path: str = None):
        """输出 JSON 报告"""
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.reports, f, indent=2, ensure_ascii=False)
            print(f"📋 报告已保存至: {output_path}")
        else:
            print(json.dumps(self.reports, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="智能代码审查系统 - Code Sentinel")
    parser.add_argument("target", help="目标目录或文件路径")
    parser.add_argument("-o", "--output", help="输出报告路径 (JSON)")
    parser.add_argument("-r", "--rules", nargs="+", choices=["security", "performance", "quality", "architecture"], help="指定审查规则")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    if not Path(args.target).exists():
        print(f"❌ 错误: 目标不存在 - {args.target}")
        sys.exit(1)
    
    sentinel = CodeSentinel(args.target)
    reports = sentinel.scan(rules=args.rules)
    
    if args.format == "json":
        sentinel.output_json(args.output)
        # 同步到 Control Center
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        cc_path = sentinel.cc.upload_results(reports, session_id)
        print(f" synced to Control Center: {cc_path}")
    else:
        print("\n✅ 审查完成")
        print(f"总问题数: {reports['summary']['total_issues']}")
        if reports["security"]:
            print(f"安全问题: {len(reports['security'])}")
        if reports["performance"]:
            print(f"性能问题: {len(reports['performance'])}")


if __name__ == "__main__":
    main()
