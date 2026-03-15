#!/usr/bin/env python3
"""
Redash CLI - 通过命令行与 Redash API 交互
从环境变量读取：
  REDASH_API_KEY - API 密钥（必须）
  REDASH_URL     - Redash 地址（默认 https://zhu.yingmi-inc.com）
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error

REDASH_URL = os.environ.get("REDASH_URL", "https://zhu.yingmi-inc.com").rstrip("/")
REDASH_API_KEY = os.environ.get("REDASH_API_KEY", "")


def _request(method, path, data=None):
    if not REDASH_API_KEY:
        print("错误：未设置 REDASH_API_KEY 环境变量，让用户登录redash生成API KEY并提供，然后执行init操作", file=sys.stderr)
        sys.exit(1)

    url = f"{REDASH_URL}{path}"
    headers = {
        "Authorization": f"Key {REDASH_API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ─────────────────────────── Queries ───────────────────────────

def list_queries(args):
    """搜索/列出 queries"""
    q = getattr(args, "q", None) or ""
    if q:
        result = _request("GET", f"/api/queries/search?q={urllib.parse.quote(q)}")
    else:
        result = _request("GET", "/api/queries?page_size=25")
        result = result.get("results", result)
    for item in result:
        print(f"[{item['id']:>5}] {item['name']}")


def get_query(args):
    """根据 ID 获取 query 详细信息"""
    result = _request("GET", f"/api/queries/{args.id}")
    _print(result)


def create_query(args):
    """创建新 query"""
    payload = {
        "name": args.name,
        "query": args.sql,
        "data_source_id": args.data_source_id,
        "description": getattr(args, "description", ""),
        "options": {"parameters": []},
    }
    result = _request("POST", "/api/queries", payload)
    print(f"创建成功，Query ID: {result['id']}")
    _print(result)


def execute_query(args):
    """执行已有 query 并等待结果（polling）"""
    # 触发 refresh
    resp = _request("POST", f"/api/queries/{args.id}/refresh")
    job = resp.get("job", {})
    job_id = job.get("id")

    if not job_id:
        # 直接返回了结果
        if "query_result" in resp:
            _print_query_result(resp["query_result"])
            return
        _print(resp)
        return

    print(f"Job ID: {job_id}，等待执行完成...")
    _poll_job(job_id)


def _poll_job(job_id):
    """轮询 job 状态直到完成"""
    for _ in range(60):
        resp = _request("GET", f"/api/jobs/{job_id}")
        job = resp.get("job", {})
        status = job.get("status")
        # status: 1=pending, 2=started, 3=success, 4=failure, 5=cancelled
        if status == 3:
            result_id = job.get("query_result_id")
            result = _request("GET", f"/api/query_results/{result_id}")
            _print_query_result(result["query_result"])
            return
        elif status in (4, 5):
            print(f"执行失败：{job.get('error', '未知错误')}", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
    print("超时：查询执行超过 60 秒", file=sys.stderr)
    sys.exit(1)


def _print_query_result(query_result):
    data = query_result.get("data", {})
    rows = data.get("rows", [])
    columns = [c["name"] for c in data.get("columns", [])]
    retrieved_at = query_result.get("retrieved_at", "")
    print(f"数据时间: {retrieved_at}，共 {len(rows)} 行\n")
    if columns:
        col_width = max(len(c) for c in columns)
        header = "  ".join(str(c).ljust(col_width) for c in columns)
        print(header)
        print("-" * len(header))
        for row in rows:
            print("  ".join(str(row.get(c, "")).ljust(col_width) for c in columns))


# ─────────────────────────── Latest Result ───────────────────────────

def get_latest_result(args):
    """获取 query 最近一次缓存的结果，不重新执行 SQL"""
    query = _request("GET", f"/api/queries/{args.id}")
    result_id = query.get("latest_query_data_id")
    if not result_id:
        print("该 query 尚无缓存结果，请先执行一次 execute-query", file=sys.stderr)
        sys.exit(1)
    retrieved_at = query.get("updated_at", "")
    print(f"Query: [{args.id}] {query.get('name', '')}")
    print(f"缓存结果 ID: {result_id}")
    result = _request("GET", f"/api/query_results/{result_id}")
    _print_query_result(result["query_result"])


# ─────────────────────────── Adhoc ───────────────────────────

def execute_adhoc(args):
    """执行临时 SQL 查询（不保存）"""
    payload = {
        "query": args.sql,
        "data_source_id": args.data_source_id,
        "max_age": 0,
    }
    resp = _request("POST", "/api/query_results", payload)

    job = resp.get("job", {})
    job_id = job.get("id")
    if job_id:
        print(f"Job ID: {job_id}，等待执行完成...")
        _poll_job(job_id)
    elif "query_result" in resp:
        _print_query_result(resp["query_result"])
    else:
        _print(resp)


# ─────────────────────────── Init ───────────────────────────

def _detect_rc_file(shell: str, platform: str) -> str:
    """根据 shell 名称和操作系统平台，返回最合适的 shell 配置文件路径。"""
    home = os.path.expanduser("~")
    shell_name = os.path.basename(shell).lower()

    if "zsh" in shell_name:
        return os.path.join(home, ".zshrc")

    if "fish" in shell_name:
        return os.path.join(home, ".config", "fish", "config.fish")

    if "bash" in shell_name:
        if platform == "darwin":
            # macOS：bash 启动时优先读 .bash_profile，其次 .bashrc
            bash_profile = os.path.join(home, ".bash_profile")
            bashrc = os.path.join(home, ".bashrc")
            return bash_profile if os.path.exists(bash_profile) else bashrc
        else:
            # Linux/其他：优先 .bashrc，其次 .bash_profile
            bashrc = os.path.join(home, ".bashrc")
            bash_profile = os.path.join(home, ".bash_profile")
            return bashrc if os.path.exists(bashrc) else bash_profile

    if "ksh" in shell_name:
        return os.path.join(home, ".kshrc")

    if "csh" in shell_name or "tcsh" in shell_name:
        return os.path.join(home, ".cshrc")

    # 兜底：POSIX 兼容的 .profile
    return os.path.join(home, ".profile")


def _make_export_line(shell_name: str, key: str, value: str) -> str:
    """根据 shell 类型生成对应的环境变量导出语句。"""
    if "fish" in shell_name:
        return f'set -x {key} "{value}"'
    return f'export {key}="{value}"'


def _is_export_line(shell_name: str, line: str, key: str) -> bool:
    """判断某行是否是对指定变量的导出语句（兼容多种 shell）。"""
    stripped = line.strip()
    if "fish" in shell_name:
        return stripped.startswith(f"set -x {key} ") or stripped.startswith(f"set -Ux {key} ")
    return stripped.startswith(f"export {key}=") or stripped.startswith(f"export {key} =")


def init(args):
    """初始化：将 REDASH_API_KEY 持久化写入用户的 shell 配置文件。"""
    api_key = args.api_key.strip()
    if not api_key:
        print("错误：API Key 不能为空", file=sys.stderr)
        sys.exit(1)

    shell = os.environ.get("SHELL", "")
    platform = sys.platform
    shell_name = os.path.basename(shell).lower()

    rc_file = _detect_rc_file(shell, platform)
    export_line = _make_export_line(shell_name, "REDASH_API_KEY", api_key)

    # 确保目标目录存在（如 ~/.config/fish/）
    rc_dir = os.path.dirname(rc_file)
    if rc_dir and not os.path.exists(rc_dir):
        os.makedirs(rc_dir, exist_ok=True)

    if os.path.exists(rc_file):
        with open(rc_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        already_exists = any(_is_export_line(shell_name, ln, "REDASH_API_KEY") for ln in lines)

        if already_exists:
            # 替换已有行，保留文件结构
            new_lines = []
            for ln in lines:
                if _is_export_line(shell_name, ln, "REDASH_API_KEY"):
                    new_lines.append(export_line + "\n")
                else:
                    new_lines.append(ln)
            with open(rc_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"✓ 已更新 {rc_file} 中的 REDASH_API_KEY")
        else:
            # 追加到文件末尾
            with open(rc_file, "a", encoding="utf-8") as f:
                f.write(f"\n# Redash API Key（由 redash init 自动写入）\n{export_line}\n")
            print(f"✓ 已将 REDASH_API_KEY 追加到 {rc_file}")
    else:
        # rc 文件不存在，直接创建
        with open(rc_file, "w", encoding="utf-8") as f:
            f.write(f"# Redash API Key（由 redash init 自动写入）\n{export_line}\n")
        print(f"✓ 已创建 {rc_file} 并写入 REDASH_API_KEY")

    print(f"\n请执行以下命令让配置在当前终端立即生效：")
    print(f"  source {rc_file}")
    print(f"\n重新打开终端后也会自动生效。")


# ─────────────────────────── Dashboards ───────────────────────────

def list_dashboards(args):
    """列出/搜索 dashboards（客户端关键词过滤）"""
    result = _request("GET", "/api/dashboards?page_size=500")
    items = result if isinstance(result, list) else result.get("results", [])
    q = (getattr(args, "q", None) or "").lower()
    for item in items:
        name = item.get("name", "")
        if q and q not in name.lower():
            continue
        slug = item.get("slug", "")
        print(f"[{item['id']:>5}] {name}  (slug: {slug})")


def get_dashboard(args):
    """根据 slug 或 ID 获取 dashboard 详细信息"""
    result = _request("GET", f"/api/dashboards/{args.slug}")
    # 简化输出：展示基本信息和 widget 列表
    print(f"ID: {result['id']}")
    print(f"名称: {result['name']}")
    print(f"Slug: {result.get('slug', '')}")
    print(f"创建时间: {result.get('created_at', '')}")
    print(f"更新时间: {result.get('updated_at', '')}")
    widgets = result.get("widgets", [])
    print(f"\nWidgets ({len(widgets)} 个):")
    for w in widgets:
        viz = w.get("visualization", {})
        query_name = viz.get("query", {}).get("name", "") if viz else ""
        print(f"  - Widget #{w['id']}: {viz.get('name', '')} (Query: {query_name})")


# ─────────────────────────── CLI ───────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Redash CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p = sub.add_parser("init", help="初始化：将 REDASH_API_KEY 写入 shell 配置文件")
    p.add_argument("api_key", help="Redash API Key（在 Redash 个人设置页面生成）")
    p.set_defaults(func=init)

    # list-queries
    p = sub.add_parser("list-queries", help="列出/搜索 queries")
    p.add_argument("-q", metavar="KEYWORD", help="搜索关键词")
    p.set_defaults(func=list_queries)

    # get-query
    p = sub.add_parser("get-query", help="获取 query 详情")
    p.add_argument("id", type=int, help="Query ID")
    p.set_defaults(func=get_query)

    # create-query
    p = sub.add_parser("create-query", help="创建新 query")
    p.add_argument("--name", required=True, help="Query 名称")
    p.add_argument("--sql", required=True, help="SQL 语句")
    p.add_argument("--data-source-id", type=int, required=True, dest="data_source_id",
                   help="数据源 ID（默认使用 41）")
    p.add_argument("--description", default="", help="描述")
    p.set_defaults(func=create_query)

    # execute-query
    p = sub.add_parser("execute-query", help="执行已有 query（真实触发 SQL）")
    p.add_argument("id", type=int, help="Query ID")
    p.set_defaults(func=execute_query)

    # get-latest-result
    p = sub.add_parser("get-latest-result", help="获取 query 最近一次缓存结果（不重新执行 SQL）")
    p.add_argument("id", type=int, help="Query ID")
    p.set_defaults(func=get_latest_result)

    # execute-adhoc
    p = sub.add_parser("execute-adhoc", help="执行临时 SQL（不保存）")
    p.add_argument("--sql", required=True, help="SQL 语句")
    p.add_argument("--data-source-id", type=int, default=41, dest="data_source_id",
                   help="数据源 ID（默认 41）")
    p.set_defaults(func=execute_adhoc)

    # list-dashboards
    p = sub.add_parser("list-dashboards", help="列出/搜索 dashboards")
    p.add_argument("-q", metavar="KEYWORD", help="按名称关键词过滤（客户端过滤）")
    p.set_defaults(func=list_dashboards)

    # get-dashboard
    p = sub.add_parser("get-dashboard", help="获取 dashboard 详情")
    p.add_argument("slug", help="Dashboard slug 或 ID")
    p.set_defaults(func=get_dashboard)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
