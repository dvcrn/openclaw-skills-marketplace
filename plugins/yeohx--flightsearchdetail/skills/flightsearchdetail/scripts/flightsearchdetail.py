#!/usr/bin/env python3

import sys
import requests
import json

# 使用方法: python flightsearch.py <tripStartDate> <startCityName> <endCityName> <userId> <limitSize>
# 示例: python flightsearch.py "2026-03-08" "北京市" "上海市" "65979bcc3fef3041109d878e" 1

# 获取命令行参数，如果没有提供则使用默认值
start_code = sys.argv[1] if len(sys.argv) > 1 else "PEK"
end_code = sys.argv[2] if len(sys.argv) > 2 else "SHA"
date = sys.argv[3] if len(sys.argv) > 3 else "2026-03-08"
flight_no = sys.argv[4] if len(sys.argv) > 1 else "HU7601"
openId = os.getenv('FEISHU_SENDER_ID') if os.getenv('FEISHU_SENDER_ID') else (sys.argv[4] if len(sys.argv) > 4 else "")

# 准备请求数据
url = "https://1253227307-52pfqg68mo-bj.scf.tencentcs.com/aiTrip/noAuth/getAirDetail"
headers = {
    "Content-Type": "application/json"
}
data = {
    "start_code": start_code,
    "end_code": end_code,
    "date": date,
    "flight_no": flight_no,
    "openId": openId
}

# 发送请求
response = requests.post(url, headers=headers, json=data)

# 输出响应
print(response.text)
