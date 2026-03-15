#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Code Generator and Tester Skill
用于生成代码、保存文件并运行测试的技能插件
"""

import os
import sys
import json
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CodeGeneratorTesterSkill:
    """
    OpenClaw技能：代码生成和测试运行工具
    用于生成代码、保存文件并运行测试
    """
    
    def __init__(self):
        self.skill_name = "code_generator_tester"
        self.description = "生成代码、保存文件并运行测试"
        
    def generate_and_run_code(self, language: str, requirements: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """
        根据需求生成代码并运行
        """
        try:
            # 生成代码
            generated_code = self.generate_code(language, requirements)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w+', suffix=f'.{self.get_file_extension(language)}', delete=False) as temp_file:
                temp_file.write(generated_code)
                temp_file_path = temp_file.name
            
            # 运行代码
            run_result = self.run_code(temp_file_path, language)
            
            # 如果提供了测试代码，运行测试
            test_result = None
            if test_code:
                test_result = self.run_tests(temp_file_path, test_code, language)
            
            return {
                "status": "success",
                "generated_code": generated_code,
                "run_result": run_result,
                "test_result": test_result,
                "temp_file": temp_file_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_code(self, language: str, requirements: str) -> str:
        """
        根据需求生成代码（这里简化为模拟生成）
        在实际应用中，这将调用LLM来生成代码
        """
        # 这里只是一个示例，实际实现会调用LLM
        if language.lower() == "python":
            # 尝试从需求中提取函数名和功能
            func_match = re.search(r'函数.*?(\w+)', requirements)
            if func_match:
                func_name = func_match.group(1)
            else:
                func_name = "my_function"
            
            code = f"""def {func_name}():
    \"\"\"
    根据需求生成的函数
    需求: {requirements}
    \"\"\"
    # TODO: 实现函数逻辑
    print("执行{requirements}")
    return "完成"

if __name__ == "__main__":
    result = {func_name}()
    print(f"结果: {{result}}")
"""
            return code
        else:
            return f"# 生成{language}代码的需求: {requirements}\n# TODO: 实现代码"
    
    def run_code(self, file_path: str, language: str) -> Dict[str, Any]:
        """
        运行指定语言的代码文件
        """
        try:
            if language.lower() == "python":
                result = subprocess.run([sys.executable, file_path], 
                                      capture_output=True, text=True, timeout=30)
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            elif language.lower() == "javascript":
                result = subprocess.run(["node", file_path], 
                                      capture_output=True, text=True, timeout=30)
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            elif language.lower() == "bash" or language.lower() == "shell":
                result = subprocess.run(["bash", file_path], 
                                      capture_output=True, text=True, timeout=30)
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"不支持的语言: {language}"
                }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "代码执行超时"
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"执行错误: {str(e)}"
            }
    
    def run_tests(self, main_file: str, test_code: str, language: str) -> Dict[str, Any]:
        """
        运行测试代码
        """
        try:
            # 创建测试文件
            test_file_ext = self.get_file_extension(language)
            with tempfile.NamedTemporaryFile(mode='w+', suffix=f'_test.{test_file_ext}', delete=False) as test_file:
                test_file.write(test_code)
                test_file_path = test_file.name
            
            # 运行测试
            if language.lower() == "python":
                # 使用pytest或unittest运行测试
                result = subprocess.run([sys.executable, test_file_path], 
                                      capture_output=True, text=True, timeout=30)
                return {
                    "test_file": test_file_path,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            elif language.lower() == "javascript":
                result = subprocess.run(["node", test_file_path], 
                                      capture_output=True, text=True, timeout=30)
                return {
                    "test_file": test_file_path,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "test_file": test_file_path,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"不支持的语言: {language} for testing"
                }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"测试执行错误: {str(e)}"
            }
    
    def get_file_extension(self, language: str) -> str:
        """
        根据语言返回文件扩展名
        """
        ext_map = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "bash": "sh",
            "shell": "sh",
            "php": "php",
            "ruby": "rb"
        }
        return ext_map.get(language.lower(), "txt")
    
    def save_code_to_project(self, code: str, file_path: str, language: str) -> Dict[str, Any]:
        """
        将代码保存到指定的项目文件路径
        """
        try:
            # 确保目录存在
            path_obj = Path(file_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入代码
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 验证保存是否成功
            if path_obj.exists():
                return {
                    "status": "success",
                    "message": f"代码已保存到 {file_path}",
                    "file_size": path_obj.stat().st_size,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "文件保存失败",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存文件时出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


def run_skill(query: str = "") -> Dict[str, Any]:
    """
    OpenClaw技能入口函数
    """
    tester = CodeGeneratorTesterSkill()
    
    # 解析查询，确定用户想要执行的操作
    query_lower = query.lower()
    
    if "生成" in query_lower and ("代码" in query_lower or "program" in query_lower.lower()):
        # 提取语言和需求
        language_match = re.search(r'(python|javascript|java|cpp|c|go|rust|bash|shell|php|ruby|typescript)', query_lower, re.IGNORECASE)
        language = language_match.group(1) if language_match else "python"
        
        # 提取需求描述（去除语言标识和其他命令词）
        requirements = query
        if language_match:
            requirements = query.replace(language_match.group(1), "", 1)
        
        # 移除常见的命令词
        common_words = ["生成", "代码", "写一个", "创建", "实现", "做一个"]
        for word in common_words:
            requirements = requirements.replace(word, "")
        
        requirements = requirements.strip()
        
        return tester.generate_and_run_code(language, requirements)
    
    elif "运行" in query_lower and ("测试" in query_lower or "test" in query_lower):
        # 这种情况下需要用户提供测试代码
        return {
            "status": "info",
            "message": "请提供要运行的测试代码",
            "usage": "运行测试 <测试代码>"
        }
    
    elif "保存" in query_lower:
        # 从查询中提取文件路径和代码
        path_match = re.search(r'到\s*(.+)', query)
        if path_match:
            file_path = path_match.group(1).strip()
            # 这里需要实际的代码内容，通常从上下文或其他地方获取
            # 暂时返回提示信息
            return {
                "status": "info", 
                "message": f"将代码保存到 {file_path}，需要提供具体代码内容"
            }
    
    else:
        return {
            "status": "info",
            "message": "可用操作: 生成代码、运行测试、保存代码",
            "usage": {
                "生成Python代码并运行": "生成一个计算阶乘的Python函数",
                "生成代码并保存": "生成一个排序算法并保存到 sort.py",
                "运行测试": "运行以下测试代码..."
            }
        }


if __name__ == "__main__":
    # 如果直接运行此脚本，则执行技能
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Code Generator and Tester Skill")
    parser.add_argument("--query", "-q", help="查询字符串", default="help")
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    
    args = parser.parse_args()
    
    result = run_skill(args.query)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))