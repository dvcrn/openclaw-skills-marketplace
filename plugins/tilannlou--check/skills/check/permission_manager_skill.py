#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Permission Manager Skill
用于处理系统权限问题的技能插件
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class PermissionManagerSkill:
    """
    OpenClaw技能：权限管理器
    用于处理系统权限问题，特别是PIP、Ollama、Docker等系统服务的权限
    """
    
    def __init__(self):
        self.skill_name = "permission_manager"
        self.description = "处理系统权限问题，特别是PIP、Ollama、Docker等系统服务的权限"
        self.system = platform.system()
        
    def check_permissions(self) -> Dict[str, Any]:
        """
        检查当前权限状态
        """
        try:
            # 检查当前用户权限
            is_admin = self._check_admin_privileges()
            
            # 检查Python环境权限
            python_path = sys.executable
            python_dir = Path(python_path).parent
            
            # 检查pip权限
            pip_result = self._check_pip_permissions()
            
            # 检查Ollama权限
            ollama_result = self._check_ollama_permissions()
            
            # 检查Docker权限
            docker_result = self._check_docker_permissions()
            
            # 检查系统类型
            is_wsl = self._check_wsl_environment()
            
            return {
                "status": "success",
                "system": self.system,
                "is_wsl": is_wsl,
                "is_admin": is_admin,
                "python_path": str(python_path),
                "python_directory": str(python_dir),
                "pip_status": pip_result,
                "ollama_status": ollama_result,
                "docker_status": docker_result,
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
    
    def _check_pip_permissions(self) -> Dict[str, Any]:
        """
        检查pip权限
        """
        try:
            # 尝试运行pip list检查权限
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                "can_execute": result.returncode == 0,
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:200] if result.stdout else "",
                "stderr_preview": result.stderr[:200] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "can_execute": False,
                "error": "命令执行超时"
            }
        except Exception as e:
            return {
                "can_execute": False,
                "error": str(e)
            }
    
    def _check_ollama_permissions(self) -> Dict[str, Any]:
        """
        检查Ollama权限
        """
        try:
            # 尝试运行ollama命令检查权限
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                "can_execute": result.returncode == 0,
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:200] if result.stdout else "",
                "stderr_preview": result.stderr[:200] if result.stderr else ""
            }
        except FileNotFoundError:
            return {
                "can_execute": False,
                "error": "Ollama未安装"
            }
        except subprocess.TimeoutExpired:
            return {
                "can_execute": False,
                "error": "命令执行超时"
            }
        except Exception as e:
            return {
                "can_execute": False,
                "error": str(e)
            }
    
    def _check_docker_permissions(self) -> Dict[str, Any]:
        """
        检查Docker权限
        """
        try:
            # 尝试运行docker命令检查权限
            result = subprocess.run(["docker", "ps"], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                "can_execute": result.returncode == 0,
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:200] if result.stdout else "",
                "stderr_preview": result.stderr[:200] if result.stderr else ""
            }
        except FileNotFoundError:
            return {
                "can_execute": False,
                "error": "Docker未安装"
            }
        except subprocess.TimeoutExpired:
            return {
                "can_execute": False,
                "error": "命令执行超时"
            }
        except Exception as e:
            return {
                "can_execute": False,
                "error": str(e)
            }
    
    def run_with_elevated_privileges(self, command: str) -> Dict[str, Any]:
        """
        尝试以提升的权限运行命令
        """
        try:
            # 根据系统类型决定如何运行命令
            if self.system == "Windows":
                return self._run_command_windows(command)
            else:
                return self._run_command_linux(command)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_command_windows(self, command: str) -> Dict[str, Any]:
        """
        在Windows上运行命令
        """
        try:
            # 检查是否已经有管理员权限
            if self._check_admin_privileges():
                # 直接运行命令
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                return {
                    "status": "success",
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                # 尝试使用runas运行命令（需要用户交互）
                return {
                    "status": "requires_user_interaction",
                    "message": "需要用户授权以管理员身份运行命令",
                    "command": command,
                    "hint": "请在终端中手动以管理员身份运行此命令"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _run_command_linux(self, command: str) -> Dict[str, Any]:
        """
        在Linux/WSL上运行命令
        """
        try:
            # 检查是否在WSL中
            if self._check_wsl_environment():
                # 在WSL中尝试运行命令
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                
                return {
                    "status": "success",
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                # 普通Linux环境，可能需要sudo
                result = subprocess.run(['sudo'] + command.split(), 
                                      capture_output=True, text=True, timeout=60)
                
                return {
                    "status": "success",
                    "command": f"sudo {command}",
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def suggest_permission_fix(self) -> Dict[str, Any]:
        """
        提供权限修复建议
        """
        is_admin = self._check_admin_privileges()
        is_wsl = self._check_wsl_environment()
        pip_status = self._check_pip_permissions()
        ollama_status = self._check_ollama_permissions()
        docker_status = self._check_docker_permissions()
        
        suggestions = []
        
        if not pip_status["can_execute"]:
            if self.system == "Windows":
                suggestions.append({
                    "service": "pip",
                    "issue": "PIP执行失败",
                    "solution": "尝试以用户模式安装: pip install --user <package_name>",
                    "alternative": "使用虚拟环境: python -m venv myenv && myenv\\Scripts\\activate && pip install <package_name>"
                })
            else:
                if is_wsl:
                    suggestions.append({
                        "service": "pip",
                        "issue": "WSL环境PIP执行失败",
                        "solution": "在WSL中使用用户安装: pip install --user <package_name>",
                        "alternative": "确保Python安装在WSL环境中而不是Windows中"
                    })
                else:
                    suggestions.append({
                        "service": "pip",
                        "issue": "PIP执行失败",
                        "solution": "使用用户安装: pip install --user <package_name>",
                        "alternative": "考虑使用虚拟环境: python -m venv myenv"
                    })
        
        if not ollama_status["can_execute"]:
            if "not found" in ollama_status.get("error", "").lower() or "未安装" in ollama_status.get("error", ""):
                suggestions.append({
                    "service": "ollama",
                    "issue": "Ollama未安装",
                    "solution": "请先安装Ollama",
                    "reference": "访问 https://ollama.ai 下载安装"
                })
            else:
                if self.system == "Windows":
                    suggestions.append({
                        "service": "ollama",
                        "issue": "Ollama权限不足",
                        "solution": "以管理员身份运行Ollama服务",
                        "alternative": "检查Ollama是否正在运行: ollama serve"
                    })
                else:
                    if is_wsl:
                        suggestions.append({
                            "service": "ollama",
                            "issue": "WSL环境Ollama权限问题",
                            "solution": "确保Ollama服务已在WSL或Windows侧正确启动",
                            "reference": "在Windows中启动Ollama应用，或在WSL中运行: ollama serve"
                        })
                    else:
                        suggestions.append({
                            "service": "ollama",
                            "issue": "Ollama权限不足",
                            "solution": "检查Ollama服务是否正在运行: systemctl status ollama (或 ollama serve)",
                            "alternative": "可能需要将用户添加到ollama组: sudo usermod -aG ollama $USER"
                        })
        
        if not docker_status["can_execute"]:
            if "not found" in docker_status.get("error", "").lower() or "未安装" in docker_status.get("error", ""):
                suggestions.append({
                    "service": "docker",
                    "issue": "Docker未安装",
                    "solution": "请先安装Docker",
                    "reference": "访问 https://docker.com 获取安装指南"
                })
            else:
                if self.system == "Windows":
                    suggestions.append({
                        "service": "docker",
                        "issue": "Docker权限不足或服务未运行",
                        "solution": "启动Docker Desktop应用",
                        "alternative": "确保Docker服务正在运行"
                    })
                else:
                    if is_wsl:
                        suggestions.append({
                            "service": "docker",
                            "issue": "WSL环境Docker权限问题",
                            "solution": "确保Docker Desktop在Windows上运行且启用了WSL集成",
                            "reference": "在Docker Desktop设置中启用对应WSL发行版的集成"
                        })
                    else:
                        suggestions.append({
                            "service": "docker",
                            "issue": "Docker权限不足",
                            "solution": "将用户添加到docker组: sudo usermod -aG docker $USER",
                            "alternative": "使用sudo运行docker命令"
                        })
        
        if not is_admin and self.system == "Windows":
            suggestions.append({
                "service": "general",
                "issue": "非管理员权限",
                "solution": "以管理员身份运行OpenClaw或终端",
                "alternative": "对需要系统权限的操作使用--user标志"
            })
        
        if is_wsl:
            suggestions.append({
                "service": "general",
                "issue": "WSL环境配置",
                "solution": "确认使用WSL2并正确配置网络",
                "reference": "参考.wslconfig配置: networkingMode=mirrored"
            })
        
        return {
            "status": "success",
            "is_admin": is_admin,
            "is_wsl": is_wsl,
            "services_status": {
                "pip": not pip_status["can_execute"],
                "ollama": not ollama_status["can_execute"],
                "docker": not docker_status["can_execute"]
            },
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_service_command_safely(self, service: str, command: str) -> Dict[str, Any]:
        """
        安全地运行服务命令
        """
        try:
            if service.lower() == "pip":
                return self.run_pip_command_safely(command)
            elif service.lower() == "ollama":
                return self.run_ollama_command_safely(command)
            elif service.lower() == "docker":
                return self.run_docker_command_safely(command)
            else:
                return {
                    "status": "error",
                    "error": f"不支持的服务: {service}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_pip_command_safely(self, pip_command: str) -> Dict[str, Any]:
        """
        安全地运行pip命令
        """
        try:
            # 检测是否是安装命令
            is_install_command = 'install' in pip_command
            
            # 构建安全的pip命令
            full_command = [sys.executable, "-m", "pip"] + pip_command.split()
            
            # 如果是安装命令，添加用户安装标志以避免权限问题
            if is_install_command and '--user' not in pip_command:
                full_command.insert(3, '--user')
            
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "success",
                "command": " ".join(full_command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时（超过300秒）",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_ollama_command_safely(self, ollama_command: str) -> Dict[str, Any]:
        """
        安全地运行ollama命令
        """
        try:
            full_command = ["ollama"] + ollama_command.split()
            
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "success",
                "command": " ".join(full_command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时（超过300秒）",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_docker_command_safely(self, docker_command: str) -> Dict[str, Any]:
        """
        安全地运行docker命令
        """
        try:
            # 检查是否在WSL中
            if self._check_wsl_environment():
                full_command = ["docker"] + docker_command.split()
            else:
                # 在普通Linux上可能需要sudo
                full_command = ["sudo", "docker"] + docker_command.split()
            
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "success",
                "command": " ".join(full_command),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "命令执行超时（超过300秒）",
                "timestamp": datetime.now().isoformat()
            }
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
    manager = PermissionManagerSkill()
    
    query_lower = query.lower()
    
    if "检查权限" in query_lower or "权限状态" in query_lower:
        return manager.check_permissions()
    
    elif "修复权限" in query_lower or "权限建议" in query_lower:
        return manager.suggest_permission_fix()
    
    elif "pip" in query_lower:
        # 提取pip命令
        import re
        pip_match = re.search(r'(install|uninstall|upgrade|list|show|freeze).*$', query, re.IGNORECASE)
        if pip_match:
            pip_cmd = pip_match.group(0)
            return manager.run_service_command_safely("pip", pip_cmd)
        else:
            return {
                "status": "error",
                "message": "未能识别pip命令，请明确指定要执行的pip操作",
                "example": "pip安装 requests"
            }
    
    elif "ollama" in query_lower:
        # 提取ollama命令
        import re
        ollama_match = re.search(r'(serve|list|pull|run|stop|cp|push).*$', query, re.IGNORECASE)
        if ollama_match:
            ollama_cmd = ollama_match.group(0)
            return manager.run_service_command_safely("ollama", ollama_cmd)
        else:
            return {
                "status": "error",
                "message": "未能识别ollama命令，请明确指定要执行的ollama操作",
                "example": "ollama list 或 ollama pull llama2"
            }
    
    elif "docker" in query_lower:
        # 提取docker命令
        import re
        docker_match = re.search(r'(ps|images|run|stop|start|build|pull|push|logs|exec|rm|rmi).*$', query, re.IGNORECASE)
        if docker_match:
            docker_cmd = docker_match.group(0)
            return manager.run_service_command_safely("docker", docker_cmd)
        else:
            return {
                "status": "error",
                "message": "未能识别docker命令，请明确指定要执行的docker操作",
                "example": "docker ps 或 docker run hello-world"
            }
    
    elif "运行命令" in query_lower:
        # 提取要运行的命令
        import re
        cmd_match = re.search(r'(?:运行命令|run)\s+(.+)', query, re.IGNORECASE)
        if cmd_match:
            command = cmd_match.group(1)
            return manager.run_with_elevated_privileges(command)
        else:
            return {
                "status": "info",
                "message": "请指定要运行的命令",
                "example": "运行命令 dir 或 运行命令 ls -la"
            }
    
    else:
        return {
            "status": "info",
            "message": "权限管理器可以检查权限状态、提供修复建议、安全运行pip/ollama/docker命令等",
            "capabilities": [
                "检查权限状态 - 检查当前权限级别和系统环境",
                "权限修复建议 - 提供针对权限问题的解决方案",
                "安全运行pip - 以避免权限问题的方式运行pip命令",
                "安全运行ollama - 以适当方式运行ollama命令",
                "安全运行docker - 以适当方式运行docker命令",
                "运行系统命令 - 尝试以适当权限运行系统命令"
            ],
            "usage": {
                "检查权限": "检查当前权限状态",
                "权限建议": "获取权限问题的修复建议",
                "pip安装 requests": "安全安装Python包",
                "ollama list": "列出Ollama模型",
                "docker ps": "列出Docker容器"
            }
        }


if __name__ == "__main__":
    # 如果直接运行此脚本，则执行技能
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Permission Manager Skill")
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