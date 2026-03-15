#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷入口: TSLA 建仓标准检查（三条红线）
内部调用 scripts/portfolio_checker.py --detail TSLA
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from portfolio_checker import load_config, run_detail_check
import json
from datetime import datetime


def main():
    config = load_config()
    result = run_detail_check(config, "TSLA")

    if result:
        output_file = f"tsla_check_{datetime.now().strftime('%Y%m%d')}.json"
        output_path = Path(__file__).parent / "output" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"📁 结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
