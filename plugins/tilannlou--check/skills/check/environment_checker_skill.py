#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Environment Checker Skill
用于检查系统环境是否满足AI开发需求的技能插件
"""

import os
import sys
import json
import platform
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class EnvironmentCheckerSkill:
    """
    OpenClaw技能：环境检查工具
    用于检查系统环境是否满足AI/ML开发需求
    """
    
    def __init__(self):
        self.skill_name = "environment_checker"
        self.description = "检查系统环境是否满足AI开发需求，包括Python包、系统工具、工作区等"
        
    def check_environment(self) -> Dict[str, Any]:
        """
        检查整个开发环境
        """
        timestamp = datetime.now().isoformat()
        
        result = {
            "timestamp": timestamp,
            "system": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "summary": {},
            "details": {}
        }
        
        # 执行各项检查
        system_check_result = self._check_system_tools()
        python_check_result = self._check_python_packages()
        workspace_check_result = self._check_workspace()
        rag_check_result = self._check_rag_environment()
        
        result["details"]["system_tools"] = system_check_result
        result["details"]["python_packages"] = python_check_result
        result["details"]["workspace"] = workspace_check_result
        result["details"]["rag_environment"] = rag_check_result
        
        # 生成摘要
        total_checks = 0
        passed_checks = 0
        
        # 检查系统工具
        for tool, info in system_check_result.items():
            total_checks += 1
            if info["installed"]:
                passed_checks += 1
                
        # 检查Python包
        for category, packages in python_check_result.items():
            for pkg, info in packages.items():
                total_checks += 1
                if info["installed"]:
                    passed_checks += 1
                    
        # 检查工作区
        for item in workspace_check_result["items"]:
            total_checks += 1
            if item["exists"]:
                passed_checks += 1
                
        # 检查RAG环境
        for provider in rag_check_result["llm_providers"]:
            total_checks += 1
            if provider["configured"]:
                passed_checks += 1
        
        result["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0,
            "environment_ready": (total_checks == passed_checks)
        }
        
        return result
    
    def _check_system_tools(self) -> Dict[str, Any]:
        """
        检查系统工具
        """
        tools = {
            "python": {"commands": ["python", "python3"], "version_flag": "--version"},
            "pip": {"commands": ["pip", "pip3"], "version_flag": "--version"},
            "git": {"commands": ["git"], "version_flag": "--version"},
            "docker": {"commands": ["docker"], "version_flag": "--version"},
            "node": {"commands": ["node", "nodejs"], "version_flag": "--version"},
        }
        
        results = {}
        
        for name, info in tools.items():
            results[name] = self._check_single_tool(name, info)
            
        return results
    
    def _check_single_tool(self, name: str, info: Dict) -> Dict:
        """
        检查单个工具
        """
        result = {"installed": False, "version": "未知", "path": ""}
        
        for cmd in info["commands"]:
            try:
                output = subprocess.run([cmd, info["version_flag"]],
                                       capture_output=True,
                                       text=True,
                                       timeout=5)
                if output.returncode == 0:
                    result["installed"] = True
                    result["version"] = output.stdout.strip()
                    
                    # 获取工具路径
                    which_cmd = "where" if platform.system() == "Windows" else "which"
                    path_out = subprocess.run([which_cmd, cmd],
                                              capture_output=True,
                                              text=True,
                                              timeout=3)
                    if path_out.returncode == 0:
                        result["path"] = path_out.stdout.strip()
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
                
        return result
    
    def _check_python_packages(self) -> Dict[str, Any]:
        """
        检查Python包
        """
        packages = {
            "AI/ML相关": ["numpy", "pandas", "scipy", "scikit-learn", "torch", "tensorflow", "transformers"],
            "RAG相关": ["langchain", "chromadb", "sentence-transformers", "openai", "llama-index"],
            "工具类": ["requests", "python-dotenv", "tqdm"],
        }
        
        mapping = {
            "sentence-transformers": "sentence_transformers",
            "llama-index": "llama_index",
        }
        
        results = {}
        
        for category, pkgs in packages.items():
            results[category] = {}
            for pkg in pkgs:
                results[category][pkg] = self._check_single_package(pkg, mapping)
                
        return results
    
    def _check_single_package(self, pkg: str, mapping: Dict[str, str]) -> Dict:
        """
        检查单个Python包
        """
        import_name = mapping.get(pkg, pkg)
        result = {"installed": False, "version": "未知", "import_name": import_name}
        
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                result["installed"] = True
                try:
                    if sys.version_info >= (3, 8):
                        from importlib.metadata import version
                        result["version"] = version(pkg)
                    else:
                        result["version"] = "未知 (无法获取)"
                except Exception:
                    result["version"] = "未知 (元数据不可用)"
        except ImportError:
            pass
            
        return result
    
    def _check_workspace(self) -> Dict[str, Any]:
        """
        检查工作区结构
        """
        ws = Path.cwd()
        results = {
            "exists": ws.exists(),
            "is_dir": ws.is_dir() if ws.exists() else False,
            "path": str(ws),
            "items": []
        }
        
        common_items = [
            "model",
            "utils", 
            "scripts",
            "output",
            "data",
            "requirements.txt",
            "config.json",
            "README.md"
        ]
        
        if results["exists"] and results["is_dir"]:
            for name in common_items:
                p = ws / name
                results["items"].append({
                    "name": name, 
                    "exists": p.exists(), 
                    "is_dir": p.is_dir() if p.exists() else False
                })
                
        return results
    
    def _check_rag_environment(self) -> Dict[str, Any]:
        """
        检查RAG环境配置
        """
        providers = [
            {"name": "OpenAI", "env": "OPENAI_API_KEY"},
            {"name": "Anthropic", "env": "ANTHROPIC_API_KEY"},
            {"name": "Cohere", "env": "COHERE_API_KEY"},
            {"name": "HuggingFace", "env": "HUGGINGFACE_API_KEY"},
        ]
        
        results = {"llm_providers": []}
        
        for provider in providers:
            key = os.getenv(provider["env"])
            configured = bool(key and key != "")
            results["llm_providers"].append({
                "name": provider["name"], 
                "env": provider["env"], 
                "configured": configured
            })
            
        return results

    def install_missing_packages(self, packages_to_install: List[str] = None) -> Dict[str, Any]:
        """
        安装缺失的Python包
        """
        if packages_to_install is None:
            # 获取所有缺失的包
            env_result = self.check_environment()
            packages_to_install = []
            
            for category, packages in env_result["details"]["python_packages"].items():
                for pkg_name, pkg_info in packages.items():
                    if not pkg_info["installed"]:
                        packages_to_install.append(pkg_name)
        
        results = []
        failed_installs = []
        
        for pkg in packages_to_install:
            try:
                print(f"正在安装 {pkg}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    install_result = f"✓ 成功安装 {pkg}"
                    results.append(install_result)
                    print(install_result)
                else:
                    install_result = f"✗ 安装失败 {pkg}: {result.stderr[-200:]}"
                    results.append(install_result)
                    failed_installs.append(pkg)
                    print(install_result)
            except subprocess.TimeoutExpired:
                install_result = f"✗ 安装超时 {pkg}"
                results.append(install_result)
                failed_installs.append(pkg)
                print(install_result)
        
        return {
            "total_packages": len(packages_to_install),
            "successful_installs": len(packages_to_install) - len(failed_installs),
            "failed_installs": len(failed_installs),
            "results": results,
            "failed_packages": failed_installs
        }


def run_skill(query: str = "") -> Dict[str, Any]:
    """
    OpenClaw技能入口函数
    """
    checker = EnvironmentCheckerSkill()
    
    if "install" in query.lower() and "missing" in query.lower():
        # 解析要安装的包列表
        env_result = checker.check_environment()
        packages_to_install = []
        
        for category, packages in env_result["details"]["python_packages"].items():
            for pkg_name, pkg_info in packages.items():
                if not pkg_info["installed"]:
                    packages_to_install.append(pkg_name)
        
        if packages_to_install:
            return checker.install_missing_packages(packages_to_install)
        else:
            return {"message": "没有需要安装的缺失包"}
    elif "install" in query.lower():
        # 从查询中提取要安装的包名
        import re
        packages = re.findall(r'install ([a-zA-Z0-9_-]+)', query, re.IGNORECASE)
        if packages:
            return checker.install_missing_packages(packages)
        else:
            return {"message": "未指定要安装的包名"}
    else:
        # 默认执行环境检查
        return checker.check_environment()


if __name__ == "__main__":
    # 如果直接运行此脚本，则执行环境检查
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Environment Checker Skill")
    parser.add_argument("--query", "-q", help="查询字符串", default="")
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    
    args = parser.parse_args()
    
    result = run_skill(args.query)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))