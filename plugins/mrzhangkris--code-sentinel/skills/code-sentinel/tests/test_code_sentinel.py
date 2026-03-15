#!/usr/bin/env python3
"""
code-sentinel 单元测试
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import json

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


class TestCodeSentinelCLI(unittest.TestCase):
    """测试 CLI 入口点"""
    
    def test_argument_parsing(self):
        """测试命令行参数解析"""
        from sentinel import main
        # 仅测试 main 函数是否存在
        self.assertIsNotNone(main)
    
    def test_sentinel_class_exists(self):
        """测试 CodeSentinel 类是否存在"""
        from sentinel import CodeSentinel
        self.assertIsNotNone(CodeSentinel)


class TestSecurityDetectors(unittest.TestCase):
    """测试安全检测器"""
    
    def test_sql_injection_detector_exists(self):
        """测试 SQL 注入检测器是否存在"""
        from security.sql_injection import SQLInjectionDetector
        self.assertIsNotNone(SQLInjectionDetector)
    
    def test_xss_detector_exists(self):
        """测试 XSS 检测器是否存在"""
        from security.xss_detector import XSSDetector
        self.assertIsNotNone(XSSDetector)
    
    def test_path_traversal_detector_exists(self):
        """测试路径遍历检测器是否存在"""
        from security.path_traversal import PathTraversalDetector
        self.assertIsNotNone(PathTraversalDetector)
    
    def test_command_injection_detector_exists(self):
        """测试命令注入检测器是否存在"""
        from security.command_injection import CommandInjectionDetector
        self.assertIsNotNone(CommandInjectionDetector)


class TestPerformanceDetectors(unittest.TestCase):
    """测试性能检测器"""
    
    def test_memory_leak_detector_exists(self):
        """测试内存泄漏检测器是否存在"""
        from performance.memory_leak import MemoryLeakDetector
        self.assertIsNotNone(MemoryLeakDetector)
    
    def test_complexity_analyzer_exists(self):
        """测试复杂度分析器是否存在"""
        from performance.complexity import ComplexityAnalyzer
        self.assertIsNotNone(ComplexityAnalyzer)


class TestLanguages(unittest.TestCase):
    """测试多语言支持"""
    
    def test_abstract_detector_exists(self):
        """测试抽象检测器是否存在"""
        from languages.abstract import JavaDetector, GoDetector, RustDetector
        self.assertIsNotNone(JavaDetector)
        self.assertIsNotNone(GoDetector)
        self.assertIsNotNone(RustDetector)


class TestIntegration(unittest.TestCase):
    """测试集成组件"""
    
    def test_cc_integration_exists(self):
        """测试 Control Center 集成是否存在"""
        from cc_integration import ControlCenterIntegration
        self.assertIsNotNone(ControlCenterIntegration)
    
    def test_omni_memory_exists(self):
        """测试 OmniMemory 集成是否存在"""
        from omni_memory import get_omni_memory
        self.assertIsNotNone(get_omni_memory)
    
    def test_evolution_exists(self):
        """测试进化集成是否存在"""
        from evolution import get_code_sentinel_evolution
        self.assertIsNotNone(get_code_sentinel_evolution)


class TestAutoFix(unittest.TestCase):
    """测试自动修复功能"""
    
    def test_autofix_module_exists(self):
        """测试 autofix 模块是否存在"""
        from autofix.core import XSSAutoFixer, SQLInjectionAutoFixer, MemoryLeakAutoFixer, autofix_file
        self.assertIsNotNone(XSSAutoFixer)
        self.assertIsNotNone(SQLInjectionAutoFixer)
        self.assertIsNotNone(MemoryLeakAutoFixer)
        self.assertIsNotNone(autofix_file)


if __name__ == "__main__":
    unittest.main()
