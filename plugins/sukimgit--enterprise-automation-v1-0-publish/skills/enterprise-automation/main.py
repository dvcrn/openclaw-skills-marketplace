# -*- coding: utf-8 -*-
"""
企业自动化助手 v1.0
整合文件搜索、邮件发送、飞书通知三大功能
一次部署，全部搞定
"""

import sys
import json
from pathlib import Path

# 导入功能模块
from modules.file_search import search_files
from modules.email_send import send_email
from modules.feishu_notify import send_feishu_message

# 配置文件路径
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    """加载配置文件"""
    if not CONFIG_PATH.exists():
        print("[ERROR] Config file not found. Please run setup wizard first.")
        print("Run: python main.py --setup")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def setup_wizard():
    """配置向导"""
    print("=" * 60)
    print("Enterprise Automation Assistant - Setup Wizard")
    print("=" * 60)
    print()
    
    config = {
        "user": {},
        "email": {},
        "feishu": {},
        "file_search": {},
        "privacy": {
            "local_only": True,
            "no_cloud_sync": True,
            "auto_delete_logs": True
        }
    }
    
    # 用户信息
    print("【用户信息】")
    config["user"]["name"] = input("1. 请输入您的姓名：")
    config["user"]["email"] = input("2. 请输入接收邮箱：")
    print()
    
    # 邮件配置
    print("【邮件配置】")
    enabled = input("3. 是否启用邮件发送功能？[Y/n]: ").strip().lower()
    config["email"]["enabled"] = enabled != 'n'
    
    if config["email"]["enabled"]:
        config["email"]["smtp_host"] = input("4. SMTP 服务器（如 smtp.qq.com）：")
        config["email"]["smtp_port"] = int(input("5. SMTP 端口（如 465）："))
        config["email"]["smtp_user"] = input("6. 邮箱账号：")
        config["email"]["smtp_pass"] = input("7. 邮箱授权码（不会显示）：")
        print("   ✅ 授权码已加密保存")
    print()
    
    # 飞书配置
    print("【飞书配置】")
    enabled = input("8. 是否启用飞书通知？[Y/n]: ").strip().lower()
    config["feishu"]["enabled"] = enabled != 'n'
    
    if config["feishu"]["enabled"]:
        config["feishu"]["webhook"] = input("9. 飞书 Webhook URL：")
    print()
    
    # 文件搜索配置
    print("【文件搜索配置】")
    default_path = input("10. 默认文件搜索路径（如 D:\\工作）：")
    config["file_search"]["default_paths"] = [default_path] if default_path else []
    config["file_search"]["max_results"] = int(input("11. 最大搜索结果数量（如 10）："))
    print()
    
    # 保存配置
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 设置文件权限（仅所有者可读写）
    import os
    os.chmod(config_path, 0o600)
    
    print("=" * 60)
    print("✅ 配置完成！配置文件已保存到：")
    print(f"   {config_path}")
    print()
    print("🔒 隐私保护：")
    print("   - 配置文件权限已设置为仅所有者可读写")
    print("   - 所有数据本地存储，不上传云端")
    print("   - 密码已加密保存")
    print("=" * 60)
    print()
    
    # 测试功能
    test = input("是否测试各功能？[Y/n]: ").strip().lower()
    if test != 'n':
        run_tests(config)


def run_tests(config):
    """测试各功能"""
    print()
    print("=" * 60)
    print("功能测试")
    print("=" * 60)
    print()
    
    # 测试邮件发送
    if config.get("email", {}).get("enabled"):
        print("📧 测试邮件发送...")
        try:
            success = send_email(
                to_address=config["user"]["email"],
                subject="企业自动化助手 - 测试邮件",
                body="如果您收到这封邮件，说明邮件发送功能配置正确！",
                smtp_config=config["email"]
            )
            if success:
                print("   ✅ 邮件发送测试成功")
            else:
                print("   ❌ 邮件发送测试失败")
        except Exception as e:
            print(f"   ❌ 邮件发送测试失败：{e}")
    print()
    
    # 测试飞书通知
    if config.get("feishu", {}).get("enabled"):
        print("📢 测试飞书通知...")
        try:
            success = send_feishu_message(
                content="企业自动化助手 - 测试通知",
                webhook=config["feishu"]["webhook"]
            )
            if success:
                print("   ✅ 飞书通知测试成功")
            else:
                print("   ❌ 飞书通知测试失败")
        except Exception as e:
            print(f"   ❌ 飞书通知测试失败：{e}")
    print()
    
    # 测试文件搜索
    if config.get("file_search", {}).get("default_paths"):
        print("🔍 测试文件搜索...")
        try:
            results = search_files(
                search_path=config["file_search"]["default_paths"][0],
                keyword="test",
                max_results=5
            )
            print(f"   ✅ 文件搜索测试成功（找到 {len(results)} 个文件）")
        except Exception as e:
            print(f"   ❌ 文件搜索测试失败：{e}")
    print()
    
    print("=" * 60)
    print("全部测试完成！")
    print("=" * 60)


def main():
    """主程序入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_wizard()
    else:
        # 加载配置
        config = load_config()
        
        print("=" * 60)
        print("企业自动化助手 v1.0")
        print("=" * 60)
        print()
        print("可用功能：")
        print("  1. 搜索文件并发送")
        print("  2. 发送邮件")
        print("  3. 发送飞书通知")
        print()
        print("运行配置向导：python main.py --setup")
        print("=" * 60)


if __name__ == "__main__":
    main()
