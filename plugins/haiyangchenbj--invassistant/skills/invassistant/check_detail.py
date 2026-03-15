#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷入口: TSLA 详细信号分析
内部调用 scripts/portfolio_checker.py --detail TSLA
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from portfolio_checker import load_config, run_detail_check


def main():
    config = load_config()
    run_detail_check(config, "TSLA")


if __name__ == "__main__":
    main()
