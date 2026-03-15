#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Query stock market data from Tencent Finance API.
Usage: uv run query_stock.py <stock_code1> [stock_code2] ...
Example: uv run query_stock.py sh000001 hkHSI usAAPL
"""

import sys
import io

# 强制 stdout 和 stderr 使用 UTF-8 编码，防止在 Cron 的隔离环境（无 LANG 变量）下报错
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

import urllib.request
import urllib.parse
import re

# Code mapping for common indices and stocks
CODE_MAP = {
    # A股指数
    '上证指数': 'sh000001',
    '深证成指': 'sz399001',
    '深证': 'sz399001',
    '上证': 'sh000001',
    '科创50': 'sh000688',
    '创业板指': 'sz399006',
    '创业板': 'sz399006',
    # 港股指数
    '恒生指数': 'hkHSI',
    '恒生': 'hkHSI',
    '恒生科技': 'hkHSTECH',
    # 美股指数
    '标普500': 'usINX',
    '道琼斯': 'usDJI',
    '标普': 'usINX',
    '纳指100': 'usNDX',
    '纳斯达克': 'usIXIC',
    '纳指': 'usIXIC',
}

def resolve_code(code_or_name):
    """Resolve a name or code to API code."""
    # Check if it's already a valid code format
    if code_or_name.startswith(('sh', 'sz', 'hk', 'us')):
        return code_or_name
    # Check mapping
    if code_or_name in CODE_MAP:
        return CODE_MAP[code_or_name]
    # Return as-is (might be a direct code)
    return code_or_name

def query_stocks(codes):
    """Query stock data from Tencent API."""
    if not codes:
        print("Usage: query_stock.py <code1> [code2] ...")
        print("Examples: query_stock.py 上证指数 hkHSI usAAPL")
        sys.exit(1)
    
    # Resolve all codes
    resolved_codes = [resolve_code(c) for c in codes]
    query = ','.join(resolved_codes)
    
    # Fetch data
    url = f"http://qt.gtimg.cn/q={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            raw_data = response.read()
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    
    # Decode with gb2312 (Tencent uses GB encoding)
    try:
        data = raw_data.decode('gb2312')
    except UnicodeDecodeError:
        try:
            data = raw_data.decode('gbk')
        except UnicodeDecodeError:
            data = raw_data.decode('utf-8', errors='ignore')
    
    # Parse results
    results = []
    for line in data.split(';'):
        line = line.strip()
        if not line.startswith('v_'):
            continue
        
        match = re.match(r'v_(\w+)=[\"\'](.+)[\"\']', line)
        if not match:
            continue
        
        code, values = match.groups()
        parts = values.split('~')
        if len(parts) < 34:
            continue
        
        name = parts[1]
        price = parts[3]
        change = parts[31]
        pct = parts[32]
        
        # Format output
        try:
            pct_float = float(pct)
            emoji = "🟢" if pct_float >= 0 else "🔴"
        except:
            emoji = "⚪"
        
        results.append({
            'code': code,
            'name': name,
            'price': price,
            'change': change,
            'pct': pct,
            'emoji': emoji
        })
    
    return results

def main():
    if len(sys.argv) < 2:
        print("查询股票/指数行情")
        print("Usage: uv run query_stock.py <code1> [code2] ...")
        print("")
        print("支持的名称:")
        print("  A股: 上证指数, 科创50, 创业板指")
        print("  港股: 恒生指数, 恒生科技")
        print("  美股: 标普500, 纳指100, 纳斯达克")
        print("  个股: sh600519(茅台), hk01810(小米), usAAPL(苹果)")
        print("")
        print("示例:")
        print("  uv run query_stock.py 上证指数 恒生指数")
        print("  uv run query_stock.py sh000001 hkHSI usAAPL")
        sys.exit(1)
    
    codes = sys.argv[1:]
    results = query_stocks(codes)
    
    if not results:
        print("未获取到数据，请检查代码是否正确")
        sys.exit(1)
    
    # Print results in table format
    print(f"{'名称':<12} {'代码':<12} {'价格':<12} {'涨跌':<10} {'涨跌幅':<8}")
    print("-" * 60)
    for r in results:
        print(f"{r['name']:<12} {r['code']:<12} {r['price']:<12} {r['change']:<10} {r['emoji']} {r['pct']}%")

if __name__ == "__main__":
    main()
