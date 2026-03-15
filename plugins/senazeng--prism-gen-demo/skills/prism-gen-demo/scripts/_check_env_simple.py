#!/usr/bin/env python3
"""
简化环境检查
只检查是否安装了必要包，不自动安装
"""

import sys
import importlib.util
import warnings

# 忽略所有警告
warnings.filterwarnings('ignore')

def check_package(package_name):
    """检查包是否已安装"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except:
        return False

def main():
    """主函数：检查必要包"""
    required_packages = [
        "pandas",
        "numpy", 
        "matplotlib",
        "seaborn",
        "scipy",
        "scikit-learn"
    ]
    
    missing = []
    for package in required_packages:
        if not check_package(package):
            missing.append(package)
    
    if missing:
        print(f"缺少包: {', '.join(missing)}")
        print("请安装: pip install " + " ".join(missing))
        return False
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)