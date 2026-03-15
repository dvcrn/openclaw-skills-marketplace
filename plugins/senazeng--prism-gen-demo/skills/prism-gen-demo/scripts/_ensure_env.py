#!/usr/bin/env python3
"""
PRISM_GEN_DEMO 环境检查脚本
确保所有必要的Python包都已安装
支持静默模式
"""

import sys
import subprocess
import importlib.util
import warnings
import os

# 忽略所有警告
warnings.filterwarnings('ignore')

# 设置matplotlib不显示中文字体警告
os.environ['MATPLOTLIBRC'] = os.path.join(os.path.dirname(__file__), '.matplotlibrc')

def check_package(package_name):
    """检查包是否已安装"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name, silent=False):
    """安装指定的包"""
    if not silent:
        print(f"正在安装 {package_name}...")
    try:
        # 尝试多种安装方式
        for pip_cmd in ["pip", "pip3", f"{sys.executable} -m pip"]:
            try:
                cmd = pip_cmd.split() + ["install", package_name]
                if silent:
                    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.check_call(cmd)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not silent:
            print(f"安装 {package_name} 失败 - 请手动安装: pip install {package_name}")
        return False
    except Exception:
        if not silent:
            print(f"安装 {package_name} 失败")
        return False

def main(silent=False):
    """主函数：检查并确保所有必要包已安装"""
    required_packages = [
        "pandas",
        "numpy", 
        "matplotlib",
        "seaborn",
        "scipy",
        "scikit-learn"
    ]
    
    if not silent:
        print("🔍 检查环境依赖...")
    
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        if not silent:
            print(f"缺少 {len(missing_packages)} 个包")
        
        for package in missing_packages:
            if not install_package(package, silent=silent):
                if not silent:
                    print(f"无法安装 {package}，请手动安装")
                return False
        
        if not silent:
            print("✅ 依赖安装完成")
    
    # 快速测试环境
    try:
        import pandas as pd
        import numpy as np
        return True
    except Exception:
        if not silent:
            print("环境测试失败")
        return False

if __name__ == "__main__":
    # 检查是否静默模式
    silent = "--silent" in sys.argv or "--quiet" in sys.argv
    success = main(silent=silent)
    sys.exit(0 if success else 1)