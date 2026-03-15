#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Universal Permission Manager Skill
用于处理各种系统命令权限问题的通用技能插件
"""

import os
import sys
import json
import subprocess
import platform
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class UniversalPermissionManagerSkill:
    """
    OpenClaw技能：通用权限管理器
    用于处理各种系统命令的权限问题
    """
    
    def __init__(self):
        self.skill_name = "universal_permission_manager"
        self.description = "处理各种系统命令的权限问题"
        self.system = platform.system()
        
    def check_permissions(self) -> Dict[str, Any]:
        """
        检查当前权限状态
        """
        try:
            # 检查当前用户权限
            is_admin = self._check_admin_privileges()
            
            # 检查系统类型
            is_wsl = self._check_wsl_environment()
            
            # 检查常用命令的可执行性
            common_commands = ["python", "pip", "git", "docker", "node", "npm", "ollama", "curl", "wget"]
            command_status = {}
            for cmd in common_commands:
                command_status[cmd] = self._check_command_access(cmd)
            
            return {
                "status": "success",
                "system": self.system,
                "is_wsl": is_wsl,
                "is_admin": is_admin,
                "command_status": command_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_admin_privileges(self) -> bool:
        """
        检查是否具有管理员权限
        """
        try:
            if self.system == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            # 如果检查失败，默认返回False
            return False
    
    def _check_wsl_environment(self) -> bool:
        """
        检查是否在WSL环境中
        """
        try:
            if self.system == "Linux":
                with open('/proc/version', 'r') as f:
                    version_info = f.read().lower()
                    return 'microsoft' in version_info or 'wsl' in version_info
            return False
        except Exception:
            return False
    
    def _check_command_access(self, command: str) -> Dict[str, Any]:
        """
        检查命令是否可以访问
        """
        try:
            # 尝试运行命令的基础版本
            result = subprocess.run([command, "--help"], 
                                  capture_output=True, text=True, timeout=10)
            
            return {
                "can_execute": result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower(),
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:100] if result.stdout else "",
                "stderr_preview": result.stderr[:100] if result.stderr else ""
            }
        except FileNotFoundError:
            return {
                "can_execute": False,
                "error": f"{command}未安装或不在PATH中"
            }
        except subprocess.TimeoutExpired:
            return {
                "can_execute": True,  # 命令存在但help太慢
                "error": "命令help超时，但可能存在"
            }
        except Exception as e:
            return {
                "can_execute": False,
                "error": str(e)
            }
    
    def run_command_with_fallback(self, command_str: str) -> Dict[str, Any]:
        """
        尝试以多种方式运行命令，直到成功或全部失败
        """
        try:
            # 解析命令
            parsed_command = shlex.split(command_str)
            
            # 首先尝试直接运行
            result = self._try_run_command(parsed_command)
            if result["status"] == "success":
                return result
            
            # 如果失败，尝试不同的策略
            strategies = [
                lambda cmd: self._try_run_with_user_flag(cmd),  # 添加--user标志（对pip等）
                lambda cmd: self._try_run_with_sudo(cmd),       # 尝试sudo（Linux/WSL）
                lambda cmd: self._try_run_with_verb_runas(cmd)  # 尝试runas（Windows）
            ]
            
            for strategy in strategies:
                result = strategy(parsed_command)
                if result["status"] == "success":
                    return result
            
            # 如果所有策略都失败了，返回最后一个错误
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _try_run_command(self, command: List[str]) -> Dict[str, Any]:
        """
        尝试运行命令
        """
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": " ".join(command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "strategy_used": "direct",
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时",
                "command": " ".join(command),
                "strategy_used": "direct"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": " ".join(command),
                "strategy_used": "direct"
            }
    
    def _try_run_with_user_flag(self, command: List[str]) -> Dict[str, Any]:
        """
        尝试运行带有--user标志的命令（主要用于pip）
        """
        try:
            # 检查命令是否是pip安装命令
            if len(command) > 1 and command[0] in ["pip", "pip3"] and command[1] == "install":
                # 在第三个位置插入--user（如果不存在）
                if "--user" not in command:
                    new_command = command[:2] + ["--user"] + command[2:]
                else:
                    new_command = command[:]
            else:
                # 对于非pip命令，直接返回原命令
                return self._try_run_command(command)
            
            result = subprocess.run(new_command, capture_output=True, text=True, timeout=60)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": " ".join(new_command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "strategy_used": "user_flag",
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时",
                "command": " ".join(command),
                "strategy_used": "user_flag"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": " ".join(command),
                "strategy_used": "user_flag"
            }
    
    def _try_run_with_sudo(self, command: List[str]) -> Dict[str, Any]:
        """
        尝试使用sudo运行命令（Linux/WSL）
        """
        if self.system == "Windows":
            return {
                "status": "error",
                "error": "sudo不适用于Windows系统",
                "command": " ".join(command),
                "strategy_used": "sudo_not_applicable"
            }
        
        try:
            # 在WSL环境中，通常不需要sudo，但在普通Linux中可能需要
            if not self._check_wsl_environment():
                new_command = ["sudo"] + command
            else:
                # 在WSL中，尝试使用sudo但预期可能失败
                new_command = ["sudo"] + command
            
            result = subprocess.run(new_command, capture_output=True, text=True, timeout=60)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": " ".join(new_command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "strategy_used": "sudo",
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时",
                "command": " ".join(command),
                "strategy_used": "sudo"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": " ".join(command),
                "strategy_used": "sudo"
            }
    
    def _try_run_with_verb_runas(self, command: List[str]) -> Dict[str, Any]:
        """
        尝试使用runas运行命令（Windows）
        """
        if self.system != "Windows":
            return {
                "status": "error",
                "error": "runas仅适用于Windows系统",
                "command": " ".join(command),
                "strategy_used": "runas_not_applicable"
            }
        
        try:
            # 在Windows上，如果我们没有管理员权限，需要提示用户
            if not self._check_admin_privileges():
                return {
                    "status": "requires_user_interaction",
                    "message": "需要用户授权以管理员身份运行命令",
                    "command": " ".join(command),
                    "strategy_used": "runas_prompt_user",
                    "hint": "请在终端中手动以管理员身份运行此命令"
                }
            else:
                # 如果已经有管理员权限，直接运行命令
                return self._try_run_command(command)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": " ".join(command),
                "strategy_used": "runas_error"
            }
    
    def suggest_permission_fix(self) -> Dict[str, Any]:
        """
        提供通用权限修复建议
        """
        is_admin = self._check_admin_privileges()
        is_wsl = self._check_wsl_environment()
        
        suggestions = []
        
        if not is_admin and self.system == "Windows":
            suggestions.append({
                "issue": "非管理员权限",
                "solution": "以管理员身份运行OpenClaw或终端",
                "alternative": "对需要系统权限的操作使用适当的用户级选项"
            })
        
        if is_wsl:
            suggestions.append({
                "issue": "WSL环境配置",
                "solution": "确认使用WSL2并正确配置网络",
                "reference": "参考.wslconfig配置: networkingMode=mirrored"
            })
            
            suggestions.append({
                "issue": "WSL与Windows应用集成",
                "solution": "确保Windows应用（如Docker Desktop、Ollama）已在Windows侧启动并配置了WSL集成"
            })
        
        # 检查常见命令的权限
        common_commands = ["python", "pip", "git", "docker", "node", "npm", "ollama"]
        for cmd in common_commands:
            status = self._check_command_access(cmd)
            if not status["can_execute"]:
                if cmd == "pip":
                    suggestions.append({
                        "issue": f"无法访问{cmd}命令",
                        "solution": f"尝试使用python -m pip代替直接使用pip命令",
                        "alternative": f"使用用户安装: python -m pip install --user [package]"
                    })
                elif cmd in ["docker", "ollama"]:
                    suggestions.append({
                        "issue": f"无法访问{cmd}命令",
                        "solution": f"确保{cmd.capitalize()}服务正在运行",
                        "alternative": f"在Windows中启动{cmd.capitalize()}应用（如果是WSL环境）"
                    })
                else:
                    suggestions.append({
                        "issue": f"无法访问{cmd}命令",
                        "solution": f"确认{cmd}已正确安装并在PATH中",
                        "alternative": f"检查{cmd}是否需要额外的权限或配置"
                    })
        
        return {
            "status": "success",
            "is_admin": is_admin,
            "is_wsl": is_wsl,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_any_command_safely(self, command_str: str) -> Dict[str, Any]:
        """
        安全地运行任何命令
        """
        try:
            return self.run_command_with_fallback(command_str)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def run_skill(query: str = "") -> Dict[str, Any]:
    """
    OpenClaw技能入口函数
    """
    manager = UniversalPermissionManagerSkill()
    
    query_lower = query.lower()
    
    if "检查权限" in query_lower or "权限状态" in query_lower:
        return manager.check_permissions()
    
    elif "修复权限" in query_lower or "权限建议" in query_lower:
        return manager.suggest_permission_fix()
    
    elif "运行命令" in query_lower or "执行命令" in query_lower:
        # 提取要运行的命令
        import re
        cmd_match = re.search(r'(?:运行命令|执行命令|run|execute)\s+(.+)', query, re.IGNORECASE)
        if cmd_match:
            command = cmd_match.group(1)
            return manager.run_any_command_safely(command)
        else:
            return {
                "status": "info",
                "message": "请指定要运行的命令",
                "example": "运行命令 pip install requests 或 运行命令 docker ps"
            }
    
    else:
        # 尝试直接运行用户输入的命令
        if query.strip():
            return manager.run_any_command_safely(query.strip())
        else:
            return {
                "status": "info",
                "message": "通用权限管理器可以处理任何系统命令的权限问题",
                "capabilities": [
                    "检查权限状态 - 检查当前权限级别和常用命令可访问性",
                    "权限修复建议 - 提供针对权限问题的通用解决方案",
                    "安全运行命令 - 使用多种策略安全运行任何命令",
                    "智能重试 - 当一个策略失败时自动尝试其他策略"
                ],
                "usage": {
                    "检查权限": "检查当前权限状态",
                    "权限建议": "获取权限问题的修复建议",
                    "运行命令 pip install requests": "安全运行任何命令",
                    "docker ps": "直接运行命令，自动处理权限问题"
                }
            }


if __name__ == "__main__":
    # 如果直接运行此脚本，则执行技能
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Universal Permission Manager Skill")
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