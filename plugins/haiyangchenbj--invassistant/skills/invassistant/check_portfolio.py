#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷入口: 全组合信号检查
内部调用 scripts/portfolio_checker.py
"""
import sys
from pathlib import Path

# 确保 scripts 目录在 path 中
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from portfolio_checker import main

if __name__ == "__main__":
    main()
