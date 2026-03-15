#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快递100 实时快递查询脚本。
从环境变量读取 KUAIDI100_KEY、KUAIDI100_CUSTOMER，调用 poll.kuaidi100.com 查询接口。
用法见 SKILL.md 或 --help。
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

API_URL = "https://poll.kuaidi100.com/poll/query.do"

STATE_NAMES = {
    "0": "在途",
    "1": "揽收",
    "2": "疑难",
    "3": "签收",
    "4": "退签",
    "5": "派件",
    "6": "退回",
    "7": "转投",
    "8": "清关",
    "10": "待清关",
    "11": "清关中",
    "12": "已清关",
    "13": "清关异常",
    "14": "拒签",
}


def get_env(key: str) -> str:
    v = os.environ.get(key)
    if not v or not v.strip():
        return ""
    return v.strip()


def make_sign(param_str: str, key: str, customer: str) -> str:
    s = param_str + key + customer
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def query(com: str, num: str, phone: str = "", from_addr: str = "", to_addr: str = "",
          resultv2: str = "4", order: str = "desc", lang: str = "zh") -> dict:
    param = {
        "com": com.strip().lower(),
        "num": num.strip(),
        "order": order,
        "lang": lang,
    }
    if phone:
        param["phone"] = phone.strip()
    if from_addr:
        param["from"] = from_addr.strip()
    if to_addr:
        param["to"] = to_addr.strip()
    if resultv2:
        param["resultv2"] = resultv2

    param_str = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
    key = get_env("KUAIDI100_KEY")
    customer = get_env("KUAIDI100_CUSTOMER")
    if not key or not customer:
        return {"_error": "缺少环境变量 KUAIDI100_KEY 或 KUAIDI100_CUSTOMER"}
    sign = make_sign(param_str, key, customer)
    body = urllib.parse.urlencode({
        "customer": customer,
        "sign": sign,
        "param": param_str,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8")
        except Exception:
            raw = "{}"
        return {"_error": f"HTTP {e.code}", "_body": raw}
    except Exception as e:
        return {"_error": str(e)}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_error": "响应非 JSON", "_body": raw[:500]}


def format_result(data: dict, json_out: bool) -> str:
    if json_out:
        if "_error" in data:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False, indent=2)
    err = data.get("_error")
    if err:
        extra = data.get("_body", "")
        return f"错误: {err}\n{extra}" if extra else f"错误: {err}"
    status = data.get("status")
    message = data.get("message", "")
    if str(status) != "200":
        return f"接口返回 status={status}, message={message}"
    state = data.get("state", "")
    state_name = STATE_NAMES.get(state, state or "未知")
    lines = [f"单号: {data.get('nu', '')}  快递: {data.get('com', '')}  状态: {state_name}"]
    arr = data.get("data") or []
    for i, item in enumerate(arr, 1):
        ftime = item.get("ftime") or item.get("time") or ""
        context = item.get("context", "")
        st = item.get("status", "")
        if st:
            lines.append(f"  {i}. [{ftime}] {context} ({st})")
        else:
            lines.append(f"  {i}. [{ftime}] {context}")
    if data.get("arrivalTime"):
        lines.append(f"预计到达: {data.get('arrivalTime')}")
    if data.get("remainTime"):
        lines.append(f"剩余时间: {data.get('remainTime')}")
    if data.get("probability"):
        lines.append(f"预计准确率: {data.get('probability')}%")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="快递100 实时查询：从环境变量 KUAIDI100_KEY、KUAIDI100_CUSTOMER 读取授权，查询单号轨迹。"
    )
    parser.add_argument("--com", required=True, help="快递公司编码，小写，如 yuantong、shunfeng")
    parser.add_argument("--num", required=True, help="快递单号")
    parser.add_argument("--phone", default="", help="收/寄件人电话（顺丰、中通等必填）")
    parser.add_argument("--from", dest="from_addr", default="", help="出发地，如 广东省深圳市南山区")
    parser.add_argument("--to", dest="to_addr", default="", help="目的地，如 北京市朝阳区；需时效预测时必填")
    parser.add_argument("--resultv2", default="4", help="0/1/4/8，默认 4；8 可返回预计到达时间")
    parser.add_argument("--order", default="desc", choices=["asc", "desc"], help="轨迹排序，默认 desc")
    parser.add_argument("--lang", default="zh", choices=["zh", "en"], help="语言，默认 zh")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON，不格式化")
    args = parser.parse_args()
    result = query(
        com=args.com,
        num=args.num,
        phone=args.phone,
        from_addr=args.from_addr,
        to_addr=args.to_addr,
        resultv2=args.resultv2,
        order=args.order,
        lang=args.lang,
    )
    out = format_result(result, args.json)
    print(out)
    if result.get("_error") or str(result.get("status")) != "200":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
