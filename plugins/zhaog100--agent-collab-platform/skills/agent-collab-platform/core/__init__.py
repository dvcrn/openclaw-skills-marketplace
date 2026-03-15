#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-collab-platform 核心模块

版本: v1.0.0
创建者: 小米粒（Dev代理）
创建时间: 2026-03-15
"""

from .base_skill import BaseSkill
from .github_monitor import GitHubMonitor
from .message_router import MessageRouter
from .state_manager import StateManager
from .issue_handler import IssueHandler

__all__ = [
    'BaseSkill',
    'GitHubMonitor',
    'MessageRouter',
    'StateManager',
    'IssueHandler'
]

__version__ = '1.0.0'
