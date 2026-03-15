"""
今日投资数据市场 - 通用 API 调用脚本

大模型直接调用此脚本获取金融数据，无需编写任何代码。

用法：
  python skills/scripts/call_api.py <接口路径> [参数名=参数值 ...] [--method GET|POST]

示例：
  # GET 接口（默认）
  python skills/scripts/call_api.py stock/basic-info stockCode=600519
  python skills/scripts/call_api.py stock/adjusted-quotes stockCode=600519 beginDate=2024-01-01 endDate=2024-12-31
  python skills/scripts/call_api.py trade-calender/special-date

  # POST 接口（参数以 JSON body 发送）
  python skills/scripts/call_api.py fund/daily-quotes --method POST fundCode=000001 beginDate=2024-01-01
  python skills/scripts/call_api.py entity-recognition --method POST

  # array 类型参数：同一 key 重复传入，自动合并为列表
  python skills/scripts/call_api.py index-quote/realtime --method POST indexCodes=000001 indexCodes=399006

环境变量：
  INVESTODAY_API_KEY  API Key（必须）

输出：
  JSON 格式的 data 字段内容，调用失败时输出错误信息并以非零退出码退出
"""

import sys
import os
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 缺少依赖，请执行 pip install requests", file=sys.stderr)
    sys.exit(1)

# ─── 配置 ──────────────────────────────────────────────────────────────────────

BASE_URL        = "https://data-api.investoday.net/data"
REQUEST_TIMEOUT = 30

# ─── API Key 加载 ──────────────────────────────────────────────────────────────

def load_api_key() -> str:
    # 1. 环境变量
    key = os.environ.get("INVESTODAY_API_KEY", "").strip()
    if key:
        return key

    # 2. .env 文件（向上查找）
    search_dir = Path(__file__).parent
    for _ in range(5):
        env_file = search_dir / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == "INVESTODAY_API_KEY":
                    val = v.strip().strip('"').strip("'")
                    if val:
                        return val
        search_dir = search_dir.parent

    print("ERROR: 请配置apikey后请求", file=sys.stderr)
    sys.exit(1)

# ─── 参数解析 ──────────────────────────────────────────────────────────────────

def parse_args(argv: list[str]) -> tuple[str, str, dict]:
    """
    解析命令行参数
    返回: (api_path, method, params_dict)

    支持格式：
      key=value          字符串（所有值均保持字符串，避免前导零等问题）
      --method GET|POST  指定 HTTP 方法（默认 GET）
    """
    if not argv:
        print("用法: python call_api.py <接口路径> [key=value ...] [--method GET|POST]", file=sys.stderr)
        print("示例: python call_api.py stock/basic-info stockCode=600519", file=sys.stderr)
        sys.exit(1)

    api_path = argv[0].lstrip("/")
    method   = "GET"
    params: dict = {}

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--method":
            i += 1
            if i >= len(argv):
                print("ERROR: --method 后需指定 GET 或 POST", file=sys.stderr)
                sys.exit(1)
            method = argv[i].upper()
            if method not in ("GET", "POST"):
                print(f"ERROR: 不支持的 HTTP 方法 '{method}'，仅支持 GET 或 POST", file=sys.stderr)
                sys.exit(1)
        elif "=" not in arg:
            print(f"ERROR: 参数格式错误 '{arg}'，应为 key=value", file=sys.stderr)
            sys.exit(1)
        else:
            k, _, v = arg.partition("=")
            if not k:
                print(f"ERROR: 参数格式错误 '{arg}'，key 不能为空", file=sys.stderr)
                sys.exit(1)
            # 同一 key 出现多次 → 收集为 list（用于 array 类型参数）
            if k in params:
                existing = params[k]
                if isinstance(existing, list):
                    existing.append(v)
                else:
                    params[k] = [existing, v]
            else:
                params[k] = v
        i += 1

    return api_path, method, params

# ─── API 调用 ──────────────────────────────────────────────────────────────────

def call_api(api_path: str, method: str, params: dict, api_key: str) -> None:
    url     = f"{BASE_URL}/{api_path}"
    headers = {"apiKey": api_key}

    try:
        if method == "POST":
            # POST：参数以 JSON body 发送，requests 会自动设置 Content-Type: application/json
            resp = requests.post(
                url,
                headers=headers,
                json=params,
                timeout=REQUEST_TIMEOUT,
            )
        else:
            # GET：参数以 query string 发送
            resp = requests.get(
                url,
                headers=headers,
                params=params if params else None,
                timeout=REQUEST_TIMEOUT,
            )
        if not resp.ok:
            print(f"ERROR: HTTP {resp.status_code}: {url}\n{resp.text[:500]}", file=sys.stderr)
            sys.exit(1)
    except requests.Timeout:
        print(f"ERROR: 请求超时（{REQUEST_TIMEOUT}s）: {url}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"ERROR: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = resp.json()
    except ValueError:
        print(f"ERROR: 响应不是合法 JSON\n{resp.text[:500]}", file=sys.stderr)
        sys.exit(1)

    code = result.get("code")
    if code != 0:
        msg = result.get("message", "未知错误")
        print(f"ERROR: API 返回错误 [{code}]: {msg}", file=sys.stderr)
        sys.exit(1)

    # 只输出 data 字段，方便大模型直接消费
    data = result.get("data")
    if data is None:
        print("ERROR: API 响应中无 data 字段", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(data, ensure_ascii=False, indent=2))

# ─── 入口 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    api_path, method, params = parse_args(sys.argv[1:])
    api_key = load_api_key()
    call_api(api_path, method, params, api_key)
