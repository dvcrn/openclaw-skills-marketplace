#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Backup Skill Wrapper
OpenClaw 调用接口
"""

import subprocess
import os
import sys

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "memory_backup.py")

def main():
    """OpenClaw 调用入口"""
    result = subprocess.run(
        ["python3", SCRIPT_PATH],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_PATH)))
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
