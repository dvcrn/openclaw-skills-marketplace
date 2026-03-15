# -*- coding: utf-8 -*-
"""
Data+AI Daily Brief — 企业微信推送脚本
自动识别日报文件，提取摘要并推送到企业微信群。

用法:
  python send_wecom.py                        # 推送今天的日报
  python send_wecom.py 2026-03-10             # 推送指定日期的日报
  python send_wecom.py --webhook <url>        # 使用自定义 webhook

环境变量:
  WECOM_WEBHOOK_URL  — 企业微信 Webhook 地址（优先级高于配置文件）
"""
import json
import urllib.request
import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_DIR / "daily-brief-config.json"


def load_config():
    """加载配置文件。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_webhook_url(args_webhook=None):
    """获取 Webhook URL，优先级：命令行参数 > 环境变量 > 配置文件。"""
    if args_webhook:
        return args_webhook

    env_url = os.environ.get("WECOM_WEBHOOK_URL")
    if env_url:
        return env_url

    config = load_config()
    wechat_config = config.get("adapters", {}).get("wechatwork", {})
    url = wechat_config.get("webhook_url", "")
    if url:
        return url

    print("[错误] 未配置企微 Webhook URL")
    print("  方式 1: 设置环境变量 WECOM_WEBHOOK_URL")
    print("  方式 2: 在 daily-brief-config.json 中配置")
    print("  方式 3: 使用 --webhook 参数")
    sys.exit(1)


def find_file(date_str, ext, search_dirs=None):
    """查找指定日期的日报文件。支持多种命名模式和搜索路径。"""
    if search_dirs is None:
        search_dirs = [PROJECT_DIR, Path(".")]

    patterns = [
        f"Data+AI全球日报_{date_str}.{ext}",
        f"Data+AI全球日报_{date_str}_v3.{ext}",
        f"Data+AI全球日报_{date_str}_v2.{ext}",
    ]

    for directory in search_dirs:
        for name in patterns:
            path = directory / name
            if path.exists():
                return path
    return None


def extract_summary_from_md(md_path, max_chars=3900):
    """从 Markdown 文件中提取精简摘要。

    提取逻辑: 标题 + 今日变化 + 总判断 + 各板块的事件标题和一句话摘要。
    摘要中不带任何链接，来源链接仅在 HTML 完整版中呈现。
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    summary_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        # 跳过来源行（来源链接只在 HTML 完整版中呈现）
        if stripped.startswith("**来源**") or stripped.startswith("- **来源**"):
            continue

        # 保留标题
        if stripped.startswith("# "):
            summary_lines.append(stripped)
            continue

        # 保留今日变化和总判断
        if stripped.startswith("## 今日") or stripped.startswith("## 🔥"):
            in_section = True
            summary_lines.append("")
            summary_lines.append(stripped)
            continue

        if in_section:
            if stripped.startswith("## ") or stripped.startswith("---"):
                in_section = False
            else:
                summary_lines.append(line)
                continue

        # 保留总判断
        if stripped.startswith("> 总判断") or stripped.startswith("> **总判断"):
            summary_lines.append("")
            summary_lines.append(stripped)
            continue

        # 保留板块标题
        if re.match(r"^## [A-E]\.", stripped) or re.match(r"^---$", stripped):
            summary_lines.append("")
            summary_lines.append(stripped)
            continue

        # 保留三级标题
        if re.match(r"^###\s+\d+\.", stripped):
            title_text = re.sub(r"^###\s+", "", stripped)
            summary_lines.append(title_text)
            continue

        # 保留加粗标题行
        if stripped.startswith("**") and ("：" in stripped or ":" in stripped or "—" in stripped):
            summary_lines.append(stripped)
            continue

        # 保留编号条目
        if re.match(r"^\d+\.\s+\*\*", stripped):
            summary_lines.append(stripped)
            continue

    summary = "\n".join(summary_lines).strip()

    # 剥离所有 Markdown 链接语法 [text](url) → text（摘要保持纯文本）
    summary = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', summary)

    # 添加尾部
    summary += "\n\n> 完整版含详细来源链接和分析师论点，见下方HTML文档。"
    summary += f"\n> *截至北京时间 {datetime.now().strftime('%Y-%m-%d')} 08:00*"

    # 企微 Markdown 消息限制是 4096 字节（非字符），中文 UTF-8 每字 3 字节
    MAX_BYTES = 4096
    encoded = summary.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        truncated = "\n\n... (完整版见下方 HTML 文档)"
        target = MAX_BYTES - len(truncated.encode("utf-8"))
        for i in range(len(summary), 0, -1):
            if len(summary[:i].encode("utf-8")) <= target:
                summary = summary[:i] + truncated
                break

    return summary


def send_markdown(webhook_url, content):
    """推送 Markdown 消息到企微。"""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    print(f"  摘要长度: {len(content)} 字符 / {len(data)} 字节")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"  [摘要] errcode: {result.get('errcode')}, errmsg: {result.get('errmsg')}")
        return result


def upload_and_send_file(webhook_url, filepath):
    """上传文件并推送到企微。"""
    upload_url = webhook_url.replace("/send?", "/upload_media?") + "&type=file"
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_data = f.read()

    boundary = "----PythonBoundary7MA4YWxk"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"media\"; filename=\"{filename}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        upload_url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        media_id = result.get("media_id")
        print(f"  [上传] errcode: {result.get('errcode')}, media_id: {media_id}")

    if media_id:
        payload = {"msgtype": "file", "file": {"media_id": media_id}}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"  [文档] errcode: {result.get('errcode')}, errmsg: {result.get('errmsg')}")


def main():
    parser = argparse.ArgumentParser(description="Data+AI 日报企微推送")
    parser.add_argument("date", nargs="?", default=None, help="日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--webhook", help="企微 Webhook URL")
    parser.add_argument("--md-only", action="store_true", help="仅推送摘要，不推送 HTML 文件")
    parser.add_argument("--search-dir", action="append", help="额外搜索日报文件的目录")
    args = parser.parse_args()

    # 确定日期
    if args.date:
        try:
            dt = datetime.strptime(args.date, "%Y-%m-%d")
            date_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            print(f"[错误] 日期格式无效: {args.date}，应为 YYYY-MM-DD")
            sys.exit(1)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    webhook_url = get_webhook_url(args.webhook)

    # 搜索目录
    search_dirs = [PROJECT_DIR, Path(".")]
    if args.search_dir:
        search_dirs.extend(Path(d) for d in args.search_dir)

    print("=" * 55)
    print(f"  Data+AI Daily Brief — 企微推送")
    print(f"  目标日期: {date_str}")
    print("=" * 55)

    # 查找 MD 文件
    md_path = find_file(date_str, "md", search_dirs)
    if not md_path:
        print(f"\n[错误] 未找到 {date_str} 的 Markdown 日报文件")
        sys.exit(1)
    print(f"\n[MD] {md_path.name}")

    # 查找 HTML 文件
    html_path = find_file(date_str, "html", search_dirs) if not args.md_only else None

    # 推送精简摘要
    print(f"\n步骤 1/2: 从 MD 提取摘要并推送...")
    summary = extract_summary_from_md(md_path)
    send_markdown(webhook_url, summary)

    # 推送 HTML 完整版
    if html_path:
        print(f"\n步骤 2/2: 推送完整版 HTML 文档...")
        upload_and_send_file(webhook_url, str(html_path))
    else:
        print(f"\n步骤 2/2: 跳过（无 HTML 文件或 --md-only）")

    print("\n" + "=" * 55)
    print("  推送完成!")
    print("=" * 55)


if __name__ == "__main__":
    main()
