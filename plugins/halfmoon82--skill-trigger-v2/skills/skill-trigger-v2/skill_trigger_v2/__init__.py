"""
Skill Trigger V2 - 智能技能触发系统

统一阈值 + 优先级仲裁的快速技能匹配。
"""

from .core import (
    SkillTrigger,
    FitResult,
    fit_gate,
    generate_declaration,
    check_dependencies,
    VERSION
)

__version__ = VERSION
__all__ = [
    "SkillTrigger",
    "FitResult", 
    "fit_gate",
    "generate_declaration",
    "check_dependencies",
    "VERSION"
]
