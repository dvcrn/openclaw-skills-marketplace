import sys
import argparse
import urllib.parse
import re

# 可疑代码模式清单（用于对目标代码进行基础静态扫描）
SUSPICIOUS_PATTERNS = [
    r"eval\s*\(",
    r"exec\s*\(",
    r"os\.system\s*\(",
    r"subprocess\.\w+\s*\(.+shell\s*=\s*True",
    r"__import__\s*\(",
    r"compile\s*\(.+exec",
]

# 敏感路径关键词（检查代码中是否尝试访问高危目录）
SENSITIVE_PATHS = [
    ".ssh", ".env", "credentials", "id_rsa",
    "passwd", "shadow", "token", "secret",
]

def validate_target(target):
    """
    对传入的扫描目标进行格式校验，
    只允许合法的 URL (http/https) 或纯字母数字的 slug。
    """
    parsed = urllib.parse.urlparse(target)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return True
    if target.replace("-", "").replace("_", "").isalnum():
        return True
    return False

def scan_content(content):
    """
    对代码文本内容进行基础的静态模式匹配扫描。
    返回检测到的可疑信号列表。
    """
    findings = []
    for i, line in enumerate(content.split("\n"), 1):
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, line):
                findings.append(f"L{i}: 检测到可疑调用模式")
                break
        for path_kw in SENSITIVE_PATHS:
            if path_kw in line.lower():
                findings.append(f"L{i}: 涉及敏感路径关键词")
                break
    return findings

def scan_skill(target):
    """
    对指定目标执行基础安全合规检查。
    本脚本为纯 Python 实现，不依赖任何外部命令行工具。
    退出码 0 = 通过，1 = 未通过。
    """
    if not validate_target(target):
        print("[!] 输入格式不合法，仅接受 http/https 链接或纯字母数字 slug。")
        sys.exit(1)

    print(f"[*] 正在对目标执行基础合规检查: {target} ...")

    # 如果是 URL，仅做格式校验（实际内容扫描需在下载后进行）
    parsed = urllib.parse.urlparse(target)
    if parsed.scheme in ("http", "https"):
        print("[+] URL 格式校验通过。深度内容扫描将在文件下载后执行。")
        sys.exit(0)

    # 如果是本地路径或 slug，尝试读取并扫描
    try:
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        findings = scan_content(content)
        if findings:
            print(f"[!] 检测到 {len(findings)} 个可疑信号：")
            for f_item in findings[:5]:
                print(f"    - {f_item}")
            sys.exit(1)
        else:
            print("[+] 基础合规检查通过，未发现可疑模式。")
            sys.exit(0)
    except FileNotFoundError:
        # slug 模式，无本地文件可扫描，仅做格式校验
        print(f"[+] Slug '{target}' 格式校验通过。")
        sys.exit(0)
    except Exception:
        print("[-] 执行检查时发生未知错误。")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Built-in Compliance Scanner")
    parser.add_argument("target", help="要检查的 URL、本地文件路径或组件 slug")
    args = parser.parse_args()
    scan_skill(args.target)
