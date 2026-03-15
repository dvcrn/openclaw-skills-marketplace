#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iTick 实时数据配置
"""

# iTick API 配置
ITICK_API_KEY = "67e368d8f1b4493582b2323a9da48ef9708755b5e7c9497ca30c8a8756c0d46b"
ITICK_BASE_URL = "https://api.itick.org"

# 请求头
HEADERS = {
    "Authorization": f"Bearer {ITICK_API_KEY}",
    "Content-Type": "application/json"
}
