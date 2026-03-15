#!/usr/bin/env python3
"""
Exchange rate skill for OpenClaw.
基于极速数据汇率查询 API：
https://www.jisuapi.com/api/exchange/
"""

import sys
import json
import os
import requests


EXCHANGE_CONVERT_URL = "https://api.jisuapi.com/exchange/convert"
EXCHANGE_SINGLE_URL = "https://api.jisuapi.com/exchange/single"
EXCHANGE_CURRENCY_URL = "https://api.jisuapi.com/exchange/currency"
EXCHANGE_BANK_URL = "https://api.jisuapi.com/exchange/bank"


def convert_exchange(appkey: str, req: dict):
    """
    调用 /exchange/convert 接口，进行货币间汇率换算。

    请求 JSON 示例：
    {
        "from": "CNY",
        "to": "USD",
        "amount": 10
    }
    """
    params = {"appkey": appkey}

    from_currency = req.get("from")
    to_currency = req.get("to")
    amount = req.get("amount", 1)

    if not from_currency:
        return {"error": "missing_param", "message": "from is required"}
    if not to_currency:
        return {"error": "missing_param", "message": "to is required"}

    params["from"] = from_currency
    params["to"] = to_currency
    params["amount"] = amount

    try:
        resp = requests.get(EXCHANGE_CONVERT_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def single_currency(appkey: str, currency: str):
    """
    调用 /exchange/single 接口，查询单个货币相对热门货币的汇率列表。
    """
    params = {
        "appkey": appkey,
        "currency": currency,
    }

    try:
        resp = requests.get(EXCHANGE_SINGLE_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def list_currencies(appkey: str):
    """
    调用 /exchange/currency 接口，查询所有支持的货币列表。
    """
    params = {"appkey": appkey}

    try:
        resp = requests.get(EXCHANGE_CURRENCY_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", [])


def bank_rates(appkey: str, bank: str | None = None):
    """
    调用 /exchange/bank 接口，查询指定银行的外汇牌价（十大银行）。

    bank 编码（可选，不传则默认为 BOC）：
      - ICBC: 工商银行
      - BOC: 中国银行
      - ABCHINA: 农业银行
      - BANKCOMM: 交通银行
      - CCB: 建设银行
      - CMBCHINA: 招商银行
      - CEBBANK: 光大银行
      - SPDB: 浦发银行
      - CIB: 兴业银行
      - ECITIC: 中信银行
    """
    params = {"appkey": appkey}
    if bank:
        params["bank"] = bank

    try:
        resp = requests.get(EXCHANGE_BANK_URL, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  exchange.py '{\"from\":\"CNY\",\"to\":\"USD\",\"amount\":10}'   # 汇率换算\n"
            "  exchange.py single CNY                                          # 单个货币相对热门货币汇率\n"
            "  exchange.py currency                                            # 所有货币列表\n"
            "  exchange.py bank BOC                                            # 银行外汇牌价（默认 BOC）",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    # 单个货币
    if cmd == "single":
        if len(sys.argv) < 3:
            print("Error: currency code is required for 'single'.", file=sys.stderr)
            sys.exit(1)
        currency = sys.argv[2]
        result = single_currency(appkey, currency)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 所有货币
    if cmd in ("currency", "currencies", "list"):
        result = list_currencies(appkey)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 银行外汇牌价
    if cmd == "bank":
        bank_code = sys.argv[2] if len(sys.argv) >= 3 else None
        result = bank_rates(appkey, bank_code)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认：汇率换算，参数为 JSON
    raw = sys.argv[1]
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "from" not in req or "to" not in req:
        print("Error: 'from' and 'to' are required in request JSON.", file=sys.stderr)
        sys.exit(1)

    result = convert_exchange(appkey, req)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

