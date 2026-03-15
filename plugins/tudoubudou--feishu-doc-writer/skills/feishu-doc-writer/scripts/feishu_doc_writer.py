#!/usr/bin/env python3
"""
飞书文档写入工具
解决 feishu_doc 工具 create 后内容为空的问题
正确流程：先 create 创建文档，再用 append 追加内容
"""

import sys
import json
import urllib.request
import urllib.parse

# 飞书配置
APP_ID = "cli_a92ae73480f89bc8"
APP_SECRET = "ilCqHkbr5DysHuq7ZPlA6e23eP2010uR"

def get_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"获取token失败: {result}")
        return result["data"]["tenant_access_token"]

def create_doc(token, title):
    """创建文档（只创建标题）"""
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    data = json.dumps({"document_style": {"title": title}, "title": title}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"创建文档失败: {result}")
        return result["data"]["document"]["document_id"]

def append_content(token, doc_id, content):
    """追加内容到文档（使用 feishu-doc-manager 的 append 格式）"""
    # 调用 OpenClaw 的 feishu_doc append 功能
    # 这里我们直接调用飞书 API 追加块
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
    data = json.dumps({
        "block_id": doc_id,  # 根节点
        "children": [
            {
                "block_type": 2,  # 文本
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            raise Exception(f"追加内容失败: {result}")
        return result["data"]

def main():
    if len(sys.argv) < 3:
        print("用法: python3 feishu_doc_writer.py <标题> <内容文件>")
        print("示例: python3 feishu_doc_writer.py 我的报告 report.md")
        sys.exit(1)
    
    title = sys.argv[1]
    content_file = sys.argv[2]
    
    # 读取内容
    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"1. 获取 token...")
    token = get_token()
    print(f"   Token 获取成功")
    
    print(f"2. 创建文档: {title}")
    doc_id = create_doc(token, title)
    print(f"   文档创建成功, ID: {doc_id}")
    
    print(f"3. 追加内容...")
    append_content(token, doc_id, content)
    print(f"   内容追加成功")
    
    print(f"\n✅ 完成！文档ID: {doc_id}")

if __name__ == "__main__":
    main()
