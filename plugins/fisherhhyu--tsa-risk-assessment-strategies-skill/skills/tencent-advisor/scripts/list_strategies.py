#!/usr/bin/env python3
"""
腾讯云智能顾问评估项查询脚本
用法:
  python3 list_strategies.py                    # 列出所有评估项
  python3 list_strategies.py --product cos      # 按产品筛选
  python3 list_strategies.py --group 安全       # 按分组筛选
  python3 list_strategies.py --level 3          # 按风险等级筛选(1/2/3)
  python3 list_strategies.py --product cos --level 3  # 组合筛选
"""
import subprocess, json, sys, urllib.parse, os

def get_credentials():
    """从环境变量或 .env 文件读取凭证"""
    secret_id = os.environ.get("TENCENT_SECRET_ID") or os.environ.get("SECRETID")
    secret_key = os.environ.get("TENCENT_SECRET_KEY") or os.environ.get("SECRETKEY")
    
    if not secret_id:
        env_path = "/root/.openclaw/workspace/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"\'')
                    # 支持多种 key 名
                    if k in ("TENCENT_SECRET_ID", "TENCENT_COS_SECRET_ID", "SECRETID"):
                        secret_id = secret_id or v
                    elif k in ("TENCENT_SECRET_KEY", "TENCENT_COS_SECRET_KEY", "SECRETKEY"):
                        secret_key = secret_key or v
    return secret_id, secret_key

def configure_tccli(secret_id, secret_key):
    subprocess.run([
        "tccli", "configure", "set",
        "secretId", secret_id,
        "secretKey", secret_key,
        "region", "ap-guangzhou"
    ], capture_output=True)

def fetch_strategies():
    result = subprocess.run(
        ["tccli", "advisor", "DescribeStrategies", "--version", "2020-07-21"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"错误: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    # tccli 返回格式：直接是 {"Strategies": [...]} 或带 Response 包装
    if "Strategies" in data:
        return data["Strategies"]
    return data.get("Response", {}).get("Strategies", [])

def make_url(name):
    return f"https://console.cloud.tencent.com/advisor/assess?strategyName={urllib.parse.quote(name)}"

def level_icon(level):
    return {3: "🔴 高危", 2: "🟡 中危", 1: "🟢 低危"}.get(level, f"⚪ L{level}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="查询腾讯云智能顾问评估项")
    parser.add_argument("--product", help="按产品筛选，如 cos/cvm/mysql/redis")
    parser.add_argument("--group", help="按分组筛选，如 安全/可靠/费用/性能")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], help="按风险等级筛选 1/2/3")
    parser.add_argument("--json", action="store_true", help="输出原始JSON")
    args = parser.parse_args()

    secret_id, secret_key = get_credentials()
    if not secret_id or not secret_key:
        print("❌ 未找到 TENCENT_SECRET_ID / TENCENT_SECRET_KEY，请配置 .env 文件")
        sys.exit(1)

    configure_tccli(secret_id, secret_key)
    strategies = fetch_strategies()

    # 筛选
    filtered = []
    for s in strategies:
        if args.product and s.get("Product", "").lower() != args.product.lower():
            continue
        if args.group and args.group not in s.get("GroupName", ""):
            continue
        if args.level:
            # 只保留含目标等级条件的策略
            has_level = any(c.get("Level") == args.level for c in s.get("Conditions", []))
            if not has_level:
                continue
        filtered.append(s)

    if args.json:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
        return

    print(f"共找到 {len(filtered)} 个评估项\n")
    
    # 按 ProductDesc 分组输出
    products = {}
    for s in filtered:
        pd = s.get("ProductDesc", s.get("Product", "其他"))
        products.setdefault(pd, []).append(s)

    for prod, items in sorted(products.items()):
        print(f"【{prod}】")
        for s in items:
            conditions = s.get("Conditions", [])
            max_level = max((c.get("Level", 0) for c in conditions), default=0)
            icon = level_icon(max_level)
            name = s.get("Name", "")
            print(f"  {icon}  {name}")
            print(f"  分组：{s.get('GroupName', '')}  |  StrategyId：{s.get('StrategyId', '')}")
            print(f"  👉 {make_url(name)}")
            print()

if __name__ == "__main__":
    main()
