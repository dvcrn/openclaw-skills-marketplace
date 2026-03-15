#!/usr/bin/env python3
"""拉取案件列表。使用 JoyDesk SDK browser_fetch_json 自动携带 Electron Cookie。

用法:
    python case_list.py                          # 默认：处理中的诉讼案件，第1页
    python case_list.py --status 2               # 已生效
    python case_list.py --status 3               # 执行中
    python case_list.py --status 4               # 已执结
    python case_list.py --type 11                # 仲裁案件
    python case_list.py --page 2 --size 50       # 第2页，每页50条
    python case_list.py --all                    # 拉取所有页
    python case_list.py --format table           # 表格输出（默认 json）
    python case_list.py --inner-code AJ-xxx      # 按内部案号搜索
    python case_list.py --plaintiff 张三          # 按原告搜索
    python case_list.py --defendant 京东          # 按被告搜索
"""
import argparse
import json
import sys

from joydesk_sdk import browser_fetch_json

API_BASE = "https://jdlawsuit-web.jd.com/api/v1"

STATUS_MAP = {
    "processing": 1, "处理中": 1, "1": 1,
    "effective": 2,  "已生效": 2, "2": 2,
    "executing": 3,  "执行中": 3, "3": 3,
    "completed": 4,  "已执结": 4, "4": 4,
}

CASE_TYPE_MAP = {
    "lawsuit": 1,    "诉讼": 1,   "1": 1,
    "arbitration": 11, "仲裁": 11, "11": 11,
}

TABLE_COLUMNS = [
    ("innerCaseCode",     "内部案号",   25),
    ("outerCaseCode",     "外部案号",   25),
    ("plaintiff",         "原告",       15),
    ("defendant",         "被告",       20),
    ("caseSummary",       "案由",       20),
    ("amountInvolved",    "涉诉金额",   12),
    ("currentStateStr",   "处理阶段",   10),
    ("primaryChargeName", "承办人",      8),
    ("openCourtTalkTime", "开庭时间",   16),
]


def fetch_cases(case_type=1, stage_status=1, page=1, size=10, **search_params):
    """调用 workbench/search 接口获取案件列表。"""
    body = {
        "current": page,
        "size": size,
        "caseType": case_type,
        "stageStatus": stage_status,
    }
    # 可选搜索字段
    if search_params.get("inner_code"):
        body["innerCaseCode"] = search_params["inner_code"]
    if search_params.get("outer_code"):
        body["outerCaseCode"] = search_params["outer_code"]
    if search_params.get("plaintiff"):
        body["plaintiff"] = search_params["plaintiff"]
    if search_params.get("defendant"):
        body["defendant"] = search_params["defendant"]
    if search_params.get("case_cause"):
        body["caseSummary"] = search_params["case_cause"]
    if search_params.get("court"):
        body["courtName"] = search_params["court"]
    if search_params.get("handler"):
        body["primaryChargeName"] = search_params["handler"]

    # browser_fetch_json(url, method, headers, body, cookie_domain, timeout_ms)
    # body 传 dict，SDK 内部会 json.dumps
    # 注意：前端实际调用的是 /workbench/searchCaseList（自动按登录用户过滤），
    # 而非 /workbench/search（返回全量数据，可能越权）
    data = browser_fetch_json(
        f"{API_BASE}/workbench/searchCaseList",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=body,
    )
    return data


def fetch_all_cases(case_type=1, stage_status=1, size=100, **search_params):
    """自动翻页拉取所有案件。"""
    all_records = []
    page = 1
    while True:
        data = fetch_cases(case_type=case_type, stage_status=stage_status, page=page, size=size, **search_params)
        if data.get("code") != 200:
            print(f"Error: {data}", file=sys.stderr)
            break
        records = data.get("data", {}).get("records", [])
        all_records.extend(records)
        total = int(data.get("data", {}).get("total", 0))
        if page * size >= total:
            break
        page += 1
    return all_records


def format_table(records):
    """格式化为表格文本输出。"""
    header = " | ".join(f"{label:<{width}}" for _, label, width in TABLE_COLUMNS)
    sep = "-+-".join("-" * width for _, _, width in TABLE_COLUMNS)
    lines = [header, sep]

    for r in records:
        row = []
        for key, _, width in TABLE_COLUMNS:
            val = str(r.get(key, "") or "")
            if len(val) > width:
                val = val[: width - 2] + ".."
            row.append(f"{val:<{width}}")
        lines.append(" | ".join(row))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="京东诉讼案件管理 - 案件列表")
    parser.add_argument("--type", default="1", help="案件类型: 1=诉讼(默认), 11=仲裁")
    parser.add_argument("--status", default="1", help="状态: 1=处理中, 2=已生效, 3=执行中, 4=已执结")
    parser.add_argument("--page", type=int, default=1, help="页码(默认1)")
    parser.add_argument("--size", type=int, default=10, help="每页条数(默认10，与前端一致)")
    parser.add_argument("--all", action="store_true", help="拉取所有页")
    parser.add_argument("--format", choices=["json", "table"], default="json", help="输出格式")
    parser.add_argument("--inner-code", help="按内部案号搜索")
    parser.add_argument("--outer-code", help="按外部案号搜索")
    parser.add_argument("--plaintiff", help="按原告搜索")
    parser.add_argument("--defendant", help="按被告搜索")
    parser.add_argument("--case-cause", help="按案由搜索")
    parser.add_argument("--court", help="按审理机构搜索")
    parser.add_argument("--handler", help="按承办人搜索")
    args = parser.parse_args()

    case_type = CASE_TYPE_MAP.get(args.type, int(args.type))
    stage_status = STATUS_MAP.get(args.status, int(args.status))

    search_params = {
        "inner_code": args.inner_code,
        "outer_code": args.outer_code,
        "plaintiff": args.plaintiff,
        "defendant": args.defendant,
        "case_cause": args.case_cause,
        "court": args.court,
        "handler": args.handler,
    }

    if args.all:
        records = fetch_all_cases(case_type, stage_status, size=100, **search_params)
        if args.format == "table":
            print(format_table(records))
            print(f"\n共 {len(records)} 条")
        else:
            print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        data = fetch_cases(case_type, stage_status, args.page, args.size, **search_params)
        if args.format == "table":
            records = data.get("data", {}).get("records", [])
            total = data.get("data", {}).get("total", 0)
            print(format_table(records))
            print(f"\n第 {args.page} 页，共 {total} 条")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
