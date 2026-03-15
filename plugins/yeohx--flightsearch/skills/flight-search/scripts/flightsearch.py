#!/usr/bin/env python3

import sys
import requests
import json

# 使用方法: python flightsearch.py <tripStartDate> <startCityName> <endCityName> <userId> <limitSize>
# 示例: python flightsearch.py "2026-03-08" "北京市" "上海市" "65979bcc3fef3041109d878e" 1

# 获取命令行参数，如果没有提供则使用默认值
tripStartDate = sys.argv[1] if len(sys.argv) > 1 else "2026-03-08"
startCityName = sys.argv[2] if len(sys.argv) > 2 else "北京市"
endCityName = sys.argv[3] if len(sys.argv) > 3 else "上海市"
openId = os.getenv('FEISHU_SENDER_ID') if os.getenv('FEISHU_SENDER_ID') else (sys.argv[4] if len(sys.argv) > 4 else "")
limitSize = int(sys.argv[5]) if len(sys.argv) > 5 else 5

# 准备请求数据
url = "https://webapp-gate-fat.fenbeijinfu.com/trip/recommend/flight/recommendOnceV2"
headers = {
    "Content-Type": "application/json"
}
data = {
    "tripStartDate": tripStartDate,
    "startCityName": startCityName,
    "endCityName": endCityName,
    "openId": openId,
    "limitSize": limitSize
}

# 发送请求
response = requests.post(url, headers=headers, json=data)

# 输出响应
print(response.text)
