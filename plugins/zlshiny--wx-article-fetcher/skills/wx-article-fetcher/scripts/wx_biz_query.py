#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号 Biz 查询工具

功能：
- 根据公众号名称查询对应的 biz
- 自动缓存查询结果，避免重复调用接口
- 签名信息加密存储

作者：十三香 (agent 管理者)
创建时间：2026-03-13
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path

# ==================== 安全配置 ====================

# 签名存储方式：从环境变量读取（推荐）或加密配置文件
# 生产环境建议使用环境变量：export WX_QUERY_SIGN="your_sign_here"
SIGN_ENV_VAR = "WX_QUERY_SIGN"

# 本地加密存储文件路径（如果不用环境变量）
# 安全隔离：每个 agent 只能访问自己工作空间的签名配置
def get_sign_config_path():
    """获取签名配置文件路径（根据调用 agent 隔离）"""
    import os
    
    # 获取当前 agent 名称
    agent_name = os.environ.get("OPENCLAW_AGENT_NAME", "unknown")
    
    # baseagent (agent 管理者) 可以访问全局配置
    if agent_name == "baseagent":
        return Path.home() / ".wx_biz_query" / "config.enc"
    
    # 其他 agent 只能访问自己工作空间的配置
    workspace = os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace" / agent_name))
    config_dir = Path(workspace) / ".wx_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "wx_sign.enc"

SIGN_CONFIG_FILE = get_sign_config_path()

# 缓存文件路径
# 安全隔离：每个 agent 只能访问自己工作空间的缓存
# 仅 baseagent (agent 管理者) 可以访问全局缓存
def get_cache_path():
    """获取缓存文件路径（根据调用 agent 隔离）"""
    import os
    
    # 获取当前 agent 名称
    agent_name = os.environ.get("OPENCLAW_AGENT_NAME", "unknown")
    
    # baseagent (agent 管理者) 可以访问全局缓存
    if agent_name == "baseagent":
        return Path.home() / ".wx_biz_query" / "cache.json"
    
    # 其他 agent 只能访问自己工作空间的缓存
    workspace = os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace" / agent_name))
    cache_dir = Path(workspace) / ".wx_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "wx_biz_cache.json"

CACHE_FILE = get_cache_path()

# 接口配置
API_BASE_URL = "https://union-api.licaimofang.com/api/jinrong/get_wx_by_name"

# ==================== 安全函数 ====================

def get_sign() -> str:
    """
    获取签名（优先从环境变量，其次从加密文件）
    """
    # 方式 1: 从环境变量读取（最安全）
    sign = os.environ.get(SIGN_ENV_VAR)
    if sign:
        return sign
    
    # 方式 2: 从加密文件读取
    if SIGN_CONFIG_FILE.exists():
        try:
            with open(SIGN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                encrypted = f.read().strip()
            # 简单 Base64 解码（生产环境建议使用更安全的加密）
            import base64
            return base64.b64decode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"⚠️ 读取加密配置文件失败：{e}")
    
    # 方式 3: 交互式输入（首次使用）
    print("🔐 未找到签名配置，请输入签名信息：")
    print("   提示：建议将签名设置到环境变量以增强安全性")
    print(f"   命令：export {SIGN_ENV_VAR}=\"your_sign_here\"")
    sign = input("签名：").strip()
    
    # 询问是否保存
    save = input("是否保存到本地加密文件？(y/n): ").strip().lower()
    if save == 'y':
        save_sign_encrypted(sign)
    
    return sign

def save_sign_encrypted(sign: str):
    """
    加密保存签名到本地文件
    """
    import base64
    
    # 创建目录
    SIGN_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 简单 Base64 编码（生产环境建议使用 cryptography 库）
    encrypted = base64.b64encode(sign.encode('utf-8')).decode('utf-8')
    
    with open(SIGN_CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(encrypted)
    
    # 设置文件权限（仅所有者可读写）
    os.chmod(SIGN_CONFIG_FILE, 0o600)
    
    print(f"✅ 签名已加密保存到：{SIGN_CONFIG_FILE}")

def load_cache() -> dict:
    """
    加载缓存数据
    """
    if not CACHE_FILE.exists():
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"⚠️ 加载缓存失败：{e}")
        return {}

def save_cache(cache: dict):
    """
    保存缓存数据
    """
    # 创建目录
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def query_wx_biz(name: str, use_cache: bool = True) -> dict:
    """
    查询微信公众号 biz
    
    Args:
        name: 公众号名称
        use_cache: 是否使用缓存（默认 True）
    
    Returns:
        dict: 查询结果，包含 biz 等信息
    """
    # 加载缓存
    cache = load_cache()
    
    # 检查缓存
    cache_key = name.strip()
    if use_cache and cache_key in cache:
        cached_data = cache[cache_key]
        print(f"📦 从缓存获取：{name}")
        print(f"   查询时间：{cached_data.get('queried_at', '未知')}")
        return {
            "success": True,
            "from_cache": True,
            "data": cached_data
        }
    
    # 调用接口查询
    print(f"🔍 正在查询：{name}")
    
    try:
        sign = get_sign()
        
        params = {
            "name": name,
            "sign": sign
        }
        
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # 检查接口返回
        if result.get("code") == "000000" or result.get("code") == 0 or result.get("success"):
            result_data = result.get("result", [])
            
            # 结果为空
            if not result_data:
                print(f"⚠️ 未找到公众号：{name}")
                return {
                    "success": False,
                    "error": "未找到该公众号",
                    "from_cache": False
                }
            
            # 取第一个匹配结果
            data = result_data[0] if isinstance(result_data, list) else result_data
            actual_name = data.get("name", name)
            
            # 保存到缓存
            cache[actual_name] = {
                "name": actual_name,
                "biz": data.get("biz"),
                "queried_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "full_data": data
            }
            save_cache(cache)
            
            print(f"✅ 查询成功")
            print(f"   公众号：{actual_name}")
            print(f"   Biz: {data.get('biz', 'N/A')}")
            
            return {
                "success": True,
                "from_cache": False,
                "data": cache[actual_name]
            }
        else:
            error_msg = result.get("message", result.get("msg", "未知错误"))
            print(f"❌ 查询失败：{error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "from_cache": False
            }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误：{e}")
        return {
            "success": False,
            "error": str(e),
            "from_cache": False
        }
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return {
            "success": False,
            "error": str(e),
            "from_cache": False
        }

def list_cache():
    """
    列出所有缓存的查询记录
    """
    cache = load_cache()
    
    if not cache:
        print("📭 缓存为空")
        return
    
    print(f"📦 缓存记录 ({len(cache)} 条):\n")
    print(f"{'公众号名称':<30} {'Biz':<40} {'查询时间'}")
    print("-" * 80)
    
    for name, data in cache.items():
        biz = data.get('biz', 'N/A')[:38] + '..' if len(str(data.get('biz', ''))) > 40 else data.get('biz', 'N/A')
        queried_at = data.get('queried_at', '未知')
        print(f"{name:<30} {biz:<40} {queried_at}")

def clear_cache():
    """
    清空缓存
    """
    if CACHE_FILE.exists():
        confirm = input("⚠️ 确认清空所有缓存？(y/n): ").strip().lower()
        if confirm == 'y':
            CACHE_FILE.unlink()
            print("✅ 缓存已清空")
    else:
        print("📭 缓存为空")

def export_cache(output_file: str = None):
    """
    导出缓存数据到文件
    """
    cache = load_cache()
    
    if not cache:
        print("📭 缓存为空")
        return
    
    if not output_file:
        output_file = f"wx_biz_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已导出 {len(cache)} 条记录到：{output_file}")

# ==================== 命令行交互 ====================

def interactive_mode():
    """
    交互式查询模式
    """
    print("=" * 60)
    print("📱 微信公众号 Biz 查询工具")
    print("=" * 60)
    print("\n命令说明:")
    print("  - 输入公众号名称进行查询")
    print("  - 'list' - 查看所有缓存记录")
    print("  - 'clear' - 清空缓存")
    print("  - 'export' - 导出缓存到文件")
    print("  - 'quit' / 'exit' - 退出程序")
    print("  - 'help' - 显示帮助")
    print("=" * 60)
    
    while True:
        try:
            name = input("\n请输入公众号名称：").strip()
            
            if not name:
                continue
            
            if name.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if name.lower() == 'help':
                print("\n命令说明:")
                print("  - 输入公众号名称进行查询")
                print("  - 'list' - 查看所有缓存记录")
                print("  - 'clear' - 清空缓存")
                print("  - 'export' - 导出缓存到文件")
                print("  - 'quit' / 'exit' - 退出程序")
                continue
            
            if name.lower() == 'list':
                list_cache()
                continue
            
            if name.lower() == 'clear':
                clear_cache()
                continue
            
            if name.lower() == 'export':
                export_cache()
                continue
            
            # 执行查询
            result = query_wx_biz(name)
            
            if result["success"]:
                data = result["data"]
                print(f"\n📊 查询结果:")
                print(f"   公众号：{data.get('name')}")
                print(f"   Biz: {data.get('biz')}")
                if result["from_cache"]:
                    print(f"   来源：缓存")
                    print(f"   查询时间：{data.get('queried_at')}")
                else:
                    print(f"   来源：接口查询")
            else:
                print(f"\n❌ 查询失败：{result.get('error')}")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误：{e}")

# ==================== 主程序 ====================

if __name__ == "__main__":
    import sys
    
    # 命令行参数模式
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['--help', '-h']:
            print("微信公众号 Biz 查询工具")
            print("\n用法:")
            print("  python wx_biz_query.py                    # 交互模式")
            print("  python wx_biz_query.py <公众号名称>        # 查询单个")
            print("  python wx_biz_query.py --list             # 列出缓存")
            print("  python wx_biz_query.py --clear            # 清空缓存")
            print("  python wx_biz_query.py --export [文件]    # 导出缓存")
            print("\n环境变量:")
            print(f"  {SIGN_ENV_VAR} - 签名信息（推荐）")
            sys.exit(0)
        
        elif command == '--list':
            list_cache()
            sys.exit(0)
        
        elif command == '--clear':
            clear_cache()
            sys.exit(0)
        
        elif command == '--export':
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            export_cache(output_file)
            sys.exit(0)
        
        else:
            # 查询单个公众号
            name = ' '.join(sys.argv[1:])
            result = query_wx_biz(name)
            if result["success"]:
                print(json.dumps(result["data"], ensure_ascii=False, indent=2))
            else:
                print(f"查询失败：{result.get('error')}")
                sys.exit(1)
    else:
        # 交互模式
        interactive_mode()
