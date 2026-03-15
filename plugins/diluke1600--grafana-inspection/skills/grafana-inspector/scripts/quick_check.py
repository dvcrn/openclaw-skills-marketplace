#!/usr/bin/env python3
"""
Grafana 快速巡检脚本
"""

import requests
import json
from datetime import datetime

# 配置
GRAFANA_URL = "http://192.168.31.103:13000"
API_KEY = "sa-openclaw-0f320944-fcaa-4719-b880-d314cfe3c43a"

# 尝试多种认证方式
headers_bearer = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

headers_basic = {
    'Authorization': f'Basic {API_KEY}',
    'Content-Type': 'application/json'
}

headers_apikey = {
    'Authorization': f'ApiKey {API_KEY}',
    'Content-Type': 'application/json'
}

print("=" * 60)
print("🚀 Grafana 系统巡检")
print("=" * 60)
print(f"时间：{datetime.now().isoformat()}")
print(f"地址：{GRAFANA_URL}")
print()

# 1. 测试连接 - 尝试多种认证方式
print("📋 检查 Grafana 连接...")

auth_methods = [
    ("Bearer", headers_bearer),
    ("ApiKey", headers_apikey),
    ("Basic", headers_basic)
]

connected = False
auth_success = None

for auth_name, hdrs in auth_methods:
    try:
        response = requests.get(f"{GRAFANA_URL}/api/org", headers=hdrs, timeout=10, verify=False)
        if response.status_code == 200:
            org = response.json()
            print(f"✅ 连接成功 ({auth_name}) - 组织：{org.get('name', 'Unknown')}")
            connected = True
            auth_success = hdrs
            break
        elif response.status_code == 401:
            print(f"⚠️  认证失败 ({auth_name})")
        else:
            print(f"❌ 连接失败 ({auth_name}) - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 连接异常 ({auth_name}): {str(e)}")

if not connected:
    print("\n💡 提示：请检查 API Key 是否正确，或使用账号密码认证")
    # 尝试基本认证（账号密码）
    print("\n📋 尝试账号密码认证...")
    try:
        import base64
        creds = base64.b64encode(b"inspection:inspection").decode()
        headers_passwd = {
            'Authorization': f'Basic {creds}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{GRAFANA_URL}/api/org", headers=headers_passwd, timeout=10, verify=False)
        if response.status_code == 200:
            org = response.json()
            print(f"✅ 账号密码认证成功 - 组织：{org.get('name', 'Unknown')}")
            auth_success = headers_passwd
            connected = True
        else:
            print(f"❌ 账号密码认证失败 - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 账号密码认证异常：{str(e)}")

if not connected:
    print("\n❌ 无法连接到 Grafana，请检查：")
    print("   1. Grafana 服务是否运行")
    print("   2. API Key 或账号密码是否正确")
    print("   3. 网络连接是否正常")
    exit(1)

headers = auth_success

print()

# 2. 检查数据源
print("📋 检查数据源状态...")
try:
    response = requests.get(f"{GRAFANA_URL}/api/datasources", headers=headers, timeout=10)
    if response.status_code == 200:
        datasources = response.json()
        print(f"✅ 数据源数量：{len(datasources)}")
        for ds in datasources:
            print(f"   - {ds.get('name', 'Unknown')} ({ds.get('type', 'Unknown')})")
    else:
        print(f"❌ 获取失败 - HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 异常：{str(e)}")

print()

# 3. 检查仪表盘
print("📋 检查仪表盘...")
try:
    response = requests.get(f"{GRAFANA_URL}/api/search?type=dash-db", headers=headers, timeout=10)
    if response.status_code == 200:
        dashboards = response.json()
        print(f"✅ 仪表盘数量：{len(dashboards)}")
        for db in dashboards[:10]:  # 显示前 10 个
            print(f"   - {db.get('title', 'Unknown')} (UID: {db.get('uid', 'N/A')})")
        if len(dashboards) > 10:
            print(f"   ... 还有 {len(dashboards) - 10} 个")
    else:
        print(f"❌ 获取失败 - HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 异常：{str(e)}")

print()

# 4. 检查告警
print("📋 检查告警状态...")
try:
    response = requests.get(f"{GRAFANA_URL}/api/v1/alerts/state", headers=headers, timeout=10)
    if response.status_code == 200:
        alerts = response.json()
        firing = [a for a in alerts if a.get('state') == 'firing']
        pending = [a for a in alerts if a.get('state') == 'pending']
        normal = [a for a in alerts if a.get('state') == 'normal']
        
        print(f"✅ 告警统计:")
        print(f"   🔴 活跃告警：{len(firing)}")
        print(f"   🟡 待处理：{len(pending)}")
        print(f"   🟢 正常：{len(normal)}")
        
        if firing:
            print("\n⚠️  活跃告警列表:")
            for alert in firing:
                print(f"   - {alert.get('name', 'Unknown')} - {alert.get('valueString', 'N/A')}")
    else:
        print(f"❌ 获取失败 - HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 异常：{str(e)}")

print()

# 5. 健康评分
print("📊 计算健康评分...")
score = 100
issues = []

# 初始化变量
firing = firing if 'firing' in locals() else []

# 如果有活跃告警，扣分
if firing:
    score -= len(firing) * 10
    issues.append(f"发现 {len(firing)} 个活跃告警")

# 确保分数在 0-100
score = max(0, min(100, score))

if score >= 90:
    status = "EXCELLENT"
elif score >= 70:
    status = "GOOD"
elif score >= 50:
    status = "WARNING"
else:
    status = "CRITICAL"

print(f"✅ 健康评分：{score}/100")
print(f"✅ 系统状态：{status}")

if issues:
    print("\n📝 异常信息:")
    for issue in issues:
        print(f"   - {issue}")

print()
print("=" * 60)
print("✅ 巡检完成")
print("=" * 60)

# 保存报告
report = {
    "timestamp": datetime.now().isoformat(),
    "grafana_url": GRAFANA_URL,
    "status": status,
    "score": score,
    "datasources_count": len(datasources) if 'datasources' in locals() else 0,
    "dashboards_count": len(dashboards) if 'dashboards' in locals() else 0,
    "alerts": {
        "firing": len(firing) if 'firing' in locals() else 0,
        "pending": len(pending) if 'pending' in locals() else 0,
        "normal": len(normal) if 'normal' in locals() else 0
    },
    "issues": issues
}

report_file = "inspection_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n📁 报告已保存：{report_file}")
