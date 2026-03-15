#!/usr/bin/env python3
"""
QWeather China Skill 安装脚本
帮助用户配置和风天气API
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """打印标题"""
    print("=" * 60)
    print("QWeather China Skill 安装向导")
    print("=" * 60)
    print()

def check_python_dependencies():
    """检查Python依赖"""
    print("🔍 检查Python依赖...")
    
    dependencies = [
        ("pyjwt", "pyjwt>=2.0.0"),
        ("cryptography", "cryptography>=3.0"),
        ("requests", "requests>=2.25")
    ]
    
    missing = []
    for package, requirement in dependencies:
        try:
            __import__(package)
            print(f"  ✅ {package} 已安装")
        except ImportError:
            print(f"  ❌ {package} 未安装")
            missing.append(requirement)
    
    if missing:
        print(f"\n📦 需要安装以下依赖: {', '.join(missing)}")
        install = input("是否立即安装？(y/n): ").lower()
        if install == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                print("✅ 依赖安装完成")
            except subprocess.CalledProcessError:
                print("❌ 依赖安装失败，请手动安装")
                return False
    else:
        print("✅ 所有依赖已安装")
    
    return True

def setup_configuration():
    """配置API密钥"""
    print("\n[CONFIG] 配置和风天气API")
    print("-" * 40)
    
    print("\n请按照以下步骤获取API密钥：")
    print("1. 访问 https://dev.qweather.com/ 注册账号")
    print("2. 创建项目并获取项目ID (sub)")
    print("3. 生成JWT密钥，下载私钥文件")
    print("4. 记录凭据ID (kid)")
    print("5. 在'设置 → 开发者信息'中查看API Host")
    print()
    
    print("请输入以下信息：")
    
    config = {}
    config["QWEATHER_SUB"] = input("项目ID (sub): ").strip()
    config["QWEATHER_KID"] = input("凭据ID (kid): ").strip()
    
    api_host = input("API Host (从和风天气控制台获取): ").strip()
    config["QWEATHER_API_HOST"] = api_host if api_host else ""
    
    private_key_path = input("私钥文件路径: ").strip()
    if private_key_path:
        config["QWEATHER_PRIVATE_KEY_PATH"] = private_key_path
    
    print("\n[INFO] 配置信息汇总：")
    for key, value in config.items():
        if value:
            print(f"  {key}: {value}")
    
    print("\n[INFO] 配置完成！")
    print("请按照以下方式设置环境变量：")
    print("\nWindows PowerShell:")
    for key, value in config.items():
        if value:
            print(f'  $env:{key}="{value}"')
    
    print("\nLinux/macOS:")
    for key, value in config.items():
        if value:
            print(f'  export {key}="{value}"')
    
    print("\n[NOTE] 如果通过ClawHub安装，请在安装时输入以上配置")
    
    return True

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置...")
    
    # 设置环境变量
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    # 检查必要的环境变量
    required_vars = ["QWEATHER_SUB", "QWEATHER_KID", "QWEATHER_PRIVATE_KEY_PATH"]
    missing_vars = []
    
    for var in required_vars:
        if var not in os.environ or not os.environ[var]:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请运行 setup.py 重新配置")
        return False
    
    # 检查私钥文件
    key_path = os.environ.get("QWEATHER_PRIVATE_KEY_PATH")
    if not Path(key_path).exists():
        print(f"❌ 私钥文件不存在: {key_path}")
        return False
    
    print("✅ 基本配置检查通过")
    
    # 询问是否运行测试
    test = input("\n是否运行API连接测试？(y/n): ").lower()
    if test == 'y':
        try:
            print("正在测试API连接...")
            result = subprocess.run(
                [sys.executable, "qweather.py", "now", "--city", "beijing"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ API连接测试成功")
                print("\n示例输出:")
                print("-" * 40)
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            else:
                print("❌ API连接测试失败")
                print("错误信息:")
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("❌ 连接超时，请检查网络")
            return False
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print_header()
    
    # 检查工作目录
    if not Path("qweather.py").exists():
        print("❌ 错误: 请在技能目录中运行此脚本")
        return 1
    
    # 步骤1: 检查依赖
    if not check_python_dependencies():
        return 1
    
    # 步骤2: 配置
    if not setup_configuration():
        return 1
    
    # 步骤3: 测试
    if not test_configuration():
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 安装完成！")
    print("=" * 60)
    print("\n使用方法:")
    print("1. 在OpenClaw中直接查询天气")
    print("   '北京天气怎么样？'")
    print("2. 命令行使用:")
    print("   python qweather.py now --city beijing")
    print("\n详细文档:")
    print("- README.md - 基本使用指南")
    print("- CONFIGURATION.md - 详细配置说明")
    print("- SKILL.md - OpenClaw技能文档")
    print("\n如需帮助，请查看文档或提交Issue")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())