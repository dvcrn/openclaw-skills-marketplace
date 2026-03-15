#!/usr/bin/env python3
"""
Whisper模型升级脚本
自动下载并优化模型配置
"""

import os
import sys
import json

CONFIG_FILE = os.path.expanduser("~/.openclaw/skills/voice-chat/config.json")

def check_model_installed(model_size: str) -> bool:
    """检查模型是否已下载"""
    model_path = os.path.expanduser(f"~/.cache/whisper/{model_size}.pt")
    return os.path.exists(model_path)

def get_model_info(model_size: str) -> dict:
    """获取模型信息"""
    models = {
        "tiny": {"size": "39MB", "params": "39M", "speed": "32x"},
        "base": {"size": "74MB", "params": "74M", "speed": "16x"},
        "small": {"size": "244MB", "params": "244M", "speed": "6x"},
        "medium": {"size": "769MB", "params": "769M", "speed": "2x"},
        "large": {"size": "1.5GB", "params": "1.5B", "speed": "1x"},
    }
    return models.get(model_size, {})

def download_model(model_size: str):
    """下载Whisper模型"""
    try:
        import whisper
        print(f"⏬ 下载Whisper {model_size}模型...")
        print(f"   大小：{get_model_info(model_size)['size']}")
        print(f"   参数：{get_model_info(model_size)['params']}")
        print(f"   这可能需要几分钟，请耐心等待...\n")
        
        model = whisper.load_model(model_size)
        
        print(f"✅ {model_size}模型下载完成！\n")
        return True
    except Exception as e:
        print(f"❌ 下载失败：{e}")
        return False

def update_config(model_size: str):
    """更新配置文件"""
    config = {
        "default_model": model_size,
        "default_dialect": "auto",
        "supported_dialects": ["mandarin", "cantonese", "shanghainese", "hakka", "minnan"],
        "models": {
            "tiny": {"installed": check_model_installed("tiny")},
            "base": {"installed": check_model_installed("base")},
            "small": {"installed": check_model_installed("small")},
            "medium": {"installed": check_model_installed("medium")},
            "large": {"installed": check_model_installed("large")},
        }
    }
    
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置已更新：{CONFIG_FILE}\n")

def show_status():
    """显示当前状态"""
    print("\n📊 模型安装状态：\n")
    print(f"{'模型':<8} {'大小':<8} {'状态':<12} {'推荐'}")
    print("─" * 50)
    
    models = ["tiny", "base", "small", "medium", "large"]
    for model in models:
        info = get_model_info(model)
        installed = check_model_installed(model)
        status = "✅ 已安装" if installed else "❌ 未安装"
        recommend = "⭐ 推荐" if model == "medium" else ""
        print(f"{model:<8} {info['size']:<8} {status:<12} {recommend}")
    
    print()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Whisper模型管理工具")
    parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"],
                       help="下载指定模型")
    parser.add_argument("-s", "--status", action="store_true",
                       help="显示模型状态")
    parser.add_argument("--set-default", choices=["tiny", "base", "small", "medium", "large"],
                       help="设置默认模型")
    parser.add_argument("--upgrade", action="store_true",
                       help="升级到medium模型（推荐）")
    
    args = parser.parse_args()
    
    # 显示状态
    if args.status:
        show_status()
        return
    
    # 升级到medium
    if args.upgrade:
        print("🚀 升级到medium模型...\n")
        if download_model("medium"):
            update_config("medium")
            print("✅ 升级完成！现在可以使用medium模型进行更准确的识别。")
            print("\n使用方法：")
            print("  python3 recognize_enhanced.py audio.mp3 -m medium")
        return
    
    # 下载指定模型
    if args.model:
        if check_model_installed(args.model):
            print(f"✅ {args.model}模型已安装")
        else:
            download_model(args.model)
            update_config(args.model)
        return
    
    # 设置默认模型
    if args.set_default:
        if not check_model_installed(args.set_default):
            print(f"❌ {args.set_default}模型未安装，请先下载")
            print(f"   运行：python3 model_manager.py -m {args.set_default}")
            sys.exit(1)
        
        update_config(args.set_default)
        print(f"✅ 默认模型已设置为：{args.set_default}")
        return
    
    # 默认显示帮助
    parser.print_help()
    print("\n快速开始：")
    print("  python3 model_manager.py --status          # 查看状态")
    print("  python3 model_manager.py --upgrade         # 升级到medium（推荐）")
    print("  python3 model_manager.py -m medium         # 下载medium模型")

if __name__ == "__main__":
    main()
