#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查/配置 GITCODE_TOKEN。
按顺序解析：当前进程 -> 用户变量 -> 系统变量；未设置时可提示并可选写入（Windows 用户变量）或输出 export 行（Unix）。

用法:
  python setup_gitcode_token.py              # 仅检查，有则输出来源并 exit 0，无则提示并 exit 1
  python setup_gitcode_token.py --set        # 未设置时提示输入并写入（Windows 用户变量）或打印 export 行（Unix）
  python setup_gitcode_token.py -q           # 静默：仅用退出码表示是否已配置（0=已配置，1=未配置）

跨平台：Windows / Linux / macOS 均可运行，仅依赖 Python 3.6+ 标准库（Windows 写用户变量时调用 PowerShell）。
"""

import os
import subprocess
import sys


def get_token_windows_user():
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "[Environment]::GetEnvironmentVariable('GITCODE_TOKEN','User')"],
            creationflags=0x08000000 if sys.platform == "win32" else 0,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
        if out:
            return out.decode("utf-8", errors="replace").strip()
    except Exception:
        pass
    return None


def get_token_windows_machine():
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "[Environment]::GetEnvironmentVariable('GITCODE_TOKEN','Machine')"],
            creationflags=0x08000000 if sys.platform == "win32" else 0,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
        if out:
            return out.decode("utf-8", errors="replace").strip()
    except Exception:
        pass
    return None


def get_token():
    """按顺序：当前进程 -> 用户级 -> 系统级。返回 (token, source)。"""
    token = os.environ.get("GITCODE_TOKEN")
    if token:
        return (token.strip(), "Process")
    if sys.platform == "win32":
        user_token = get_token_windows_user()
        if user_token:
            return (user_token, "User")
        machine_token = get_token_windows_machine()
        if machine_token:
            return (machine_token, "Machine")
    return (None, None)


def set_token_windows_user(value):
    """写入 Windows 用户级环境变量。通过子进程环境变量传值，避免 token 中特殊字符转义问题。"""
    try:
        env = os.environ.copy()
        env["GITCODE_TOKEN_SET_VALUE"] = value
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$v = [Environment]::GetEnvironmentVariable('GITCODE_TOKEN_SET_VALUE','Process'); "
             "[Environment]::SetEnvironmentVariable('GITCODE_TOKEN', $v, 'User')"],
            check=True,
            timeout=5,
            env=env,
            creationflags=0x08000000 if sys.platform == "win32" else 0,
        )
        return True
    except Exception:
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Check or set GITCODE_TOKEN for GitCode API (cross-platform)."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet: exit 0 if set, 1 if not.")
    parser.add_argument("-s", "--set", action="store_true", dest="set_token",
                        help="If unset, prompt and set (Windows User) or print export line (Unix).")
    args = parser.parse_args()

    token, source = get_token()
    if token:
        if not args.quiet:
            print("GITCODE_TOKEN is set (source: %s)." % source)
        return 0

    # Token not found
    if args.quiet:
        return 1

    print("")
    print("GITCODE_TOKEN is not set. Configure it as follows:")
    print("  1. Create token: https://gitcode.com/setting/token-classic (e.g. read_api, read_repository).")
    if sys.platform == "win32":
        print("  2. Set env var: name GITCODE_TOKEN, value = your token (User or System env vars).")
        print("     (Windows: This PC -> Properties -> Advanced -> Environment Variables -> New under User or System.)")
    else:
        print("  2. Set env var: export GITCODE_TOKEN=your_token (or add to ~/.bashrc / ~/.zshrc).")
    print("  3. Restart terminal or Cursor after changing User/System env vars or profile.")
    print("")

    if args.set_token:
        try:
            prompt = "Enter token to set GITCODE_TOKEN now (or leave blank to skip): "
            input_token = input(prompt).strip()
        except EOFError:
            input_token = ""
        if input_token:
            if sys.platform == "win32":
                if set_token_windows_user(input_token):
                    print("GITCODE_TOKEN saved to User env. Restart terminal or Cursor to take effect.")
                    return 0
                print("Failed to write User env var.", file=sys.stderr)
                return 1
            else:
                print("Add this line to ~/.bashrc or ~/.zshrc, then restart shell:")
                print('  export GITCODE_TOKEN="%s"' % input_token)
                print("")
                return 0

    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
