#!/usr/bin/env python3
"""
飞书文档报告生成脚本
将巡检报告发送到飞书文档
"""

import json
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional


class FeishuReportGenerator:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_access_token = None
    
    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 0:
            self.tenant_access_token = result['tenant_access_token']
            return self.tenant_access_token
        else:
            raise Exception(f"获取令牌失败：{result}")
    
    def create_doc(self, title: str, parent_folder_token: Optional[str] = None) -> str:
        """创建飞书云文档"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()
        
        url = f"{self.base_url}/docx/v1/docs"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": title
        }
        
        if parent_folder_token:
            payload["folder_token"] = parent_folder_token
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 0:
            doc_id = result['data']['doc_id']
            print(f"文档创建成功：{doc_id}")
            return doc_id
        else:
            raise Exception(f"创建文档失败：{result}")
    
    def update_doc_content(self, doc_id: str, markdown_content: str) -> bool:
        """更新文档内容"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()
        
        url = f"{self.base_url}/docx/v1/docs/{doc_id}/content"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        # 将 Markdown 转换为飞书文档格式
        # 这里简化处理，实际需要根据飞书文档 API 格式转换
        payload = {
            "content": markdown_content
        }
        
        response = requests.patch(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') == 0:
            print("文档内容更新成功")
            return True
        else:
            print(f"文档内容更新失败：{result}")
            return False
    
    def send_report(
        self,
        inspection_results: Dict[str, Any],
        report_markdown: str,
        title: Optional[str] = None,
        parent_folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送巡检报告到飞书文档"""
        
        if title is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            title = f"📊 Grafana 自动化巡检报告 - {timestamp}"
        
        # 1. 创建文档
        doc_id = self.create_doc(title, parent_folder_token)
        
        # 2. 更新文档内容
        success = self.update_doc_content(doc_id, report_markdown)
        
        # 3. 返回结果
        return {
            "doc_id": doc_id,
            "title": title,
            "success": success,
            "url": f"https://your-company.feishu.cn/docx/{doc_id}",
            "timestamp": datetime.now().isoformat(),
            "inspection_summary": {
                "status": inspection_results.get('status', 'unknown'),
                "score": inspection_results.get('score', 0),
                "issues_count": len(inspection_results.get('issues', [])),
                "alerts_count": len(inspection_results.get('alerts', []))
            }
        }


def main():
    if len(sys.argv) < 3:
        print("用法：python feishu_report.py <app_id> <app_secret> <report_json_file>")
        sys.exit(1)
    
    app_id = sys.argv[1]
    app_secret = sys.argv[2]
    report_file = sys.argv[3]
    
    # 读取巡检结果
    with open(report_file, 'r', encoding='utf-8') as f:
        inspection_results = json.load(f)
    
    # 生成报告
    generator = FeishuReportGenerator(app_id, app_secret)
    result = generator.send_report(
        inspection_results=inspection_results,
        report_markdown=inspection_results.get('report_markdown', '')
    )
    
    print("\n报告发送结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
