"""
Auto-Coding Skill
自动编码 - 自主编码 Agent 技能

Usage:
  # 方式 1: Python 模块调用
  from auto_coding import AutonomousCodingController
  
  controller = AutonomousCodingController(
      project_name="my-app",
      requirements="创建一个 Todo 应用"
  )
  result = await controller.run_full_cycle()

  # 方式 2: OpenClaw Skill 调用
  # /auto-coding 创建一个 Todo 应用
"""

__version__ = "1.0.0"
__author__ = "Krislu + Claw Soft"

from .agent_controller import AutonomousCodingController
from .task_manager import TaskManager
from .security import validate_command, get_security_report

# OpenClaw Skill 导出
try:
    from .skill import AutoCodingSkill, register
    __all__ = [
        "AutonomousCodingController",
        "TaskManager",
        "validate_command",
        "get_security_report",
        "AutoCodingSkill",
        "register",
    ]
except ImportError:
    __all__ = [
        "AutonomousCodingController",
        "TaskManager",
        "validate_command",
        "get_security_report",
    ]
