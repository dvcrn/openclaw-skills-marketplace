#!/usr/bin/env python3
"""
AI Agent Security Scanner - 快速扫描接口
用于 OpenClaw Skill 调用
"""
import json
import subprocess
import sys
from pathlib import Path

SCANNER_DIR = Path(__file__).parent.parent.resolve()


def run_scan(
    verbose: bool = True,
    output_json: str = None,
    output_html: str = None,
    feishu: bool = False,
    llm: bool = False,
    llm_provider: str = "zhipu",
) -> dict:
    """
    执行安全扫描
    
    Args:
        verbose: 详细输出
        output_json: JSON 报告输出路径
        output_html: HTML 报告输出路径
        feishu: 生成飞书文档报告
        llm: 启用 LLM 语义分析
        llm_provider: LLM 提供商
    
    Returns:
        扫描结果字典
    """
    cmd = ["aascan", "scan"]
    
    if verbose:
        cmd.append("-v")
    
    if output_json:
        cmd.extend(["-o", output_json])
    
    if output_html:
        cmd.extend(["--html", output_html])
    
    if feishu:
        cmd.extend(["--feishu", "--feishu-title", f"AI Agent 安全扫描报告"])
    
    if llm:
        cmd.extend(["--llm", "--llm-provider", llm_provider])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SCANNER_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        return {
            "success": result.returncode in [0, 1],
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "扫描超时（超过 5 分钟）",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def discover_assets() -> dict:
    """仅执行资产发现"""
    try:
        result = subprocess.run(
            ["aascan", "discover"],
            cwd=SCANNER_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def check_apikey(path: str = None, verify: bool = False) -> dict:
    """检测 API Key 泄露"""
    cmd = ["aascan", "check-apikey"]
    
    if path:
        cmd.append(path)
    
    if verify:
        cmd.append("--verify")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SCANNER_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Agent Security Scanner")
    subparsers = parser.add_subparsers(dest="command")
    
    # scan 子命令
    scan_parser = subparsers.add_parser("scan", help="执行完整扫描")
    scan_parser.add_argument("-o", "--output", help="JSON 报告输出路径")
    scan_parser.add_argument("--html", help="HTML 报告输出路径")
    scan_parser.add_argument("--feishu", action="store_true", help="生成飞书报告")
    scan_parser.add_argument("--llm", action="store_true", help="启用 LLM 分析")
    scan_parser.add_argument("--llm-provider", default="zhipu", help="LLM 提供商")
    scan_parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    
    # discover 子命令
    subparsers.add_parser("discover", help="仅资产发现")
    
    # check-apikey 子命令
    key_parser = subparsers.add_parser("check-apikey", help="检测 API Key")
    key_parser.add_argument("path", nargs="?", help="扫描路径")
    key_parser.add_argument("--verify", action="store_true", help="验证 Key 有效性")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        result = run_scan(
            verbose=not args.quiet,
            output_json=args.output,
            output_html=args.html,
            feishu=args.feishu,
            llm=args.llm,
            llm_provider=args.llm_provider,
        )
    elif args.command == "discover":
        result = discover_assets()
    elif args.command == "check-apikey":
        result = check_apikey(args.path, args.verify)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
