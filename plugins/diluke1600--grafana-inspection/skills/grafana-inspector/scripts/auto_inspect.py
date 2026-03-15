#!/usr/bin/env python3
"""
Grafana 自动化巡检主脚本
整合所有检查功能，生成完整报告
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 导入其他模块
from grafana_check import GrafanaInspector
from capture_dashboard import GrafanaScreenshot


class AutoInspection:
    """自动化巡检主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'score': 0,
            'checks': [],
            'alerts': [],
            'issues': [],
            'screenshots': [],
            'report_url': None
        }
    
    def run_inspection(self) -> Dict[str, Any]:
        """执行完整巡检流程"""
        print("=" * 60)
        print("🚀 Grafana 自动化巡检系统")
        print("=" * 60)
        
        try:
            # 1. 初始化检查器
            grafana_url = self.config.get('grafana_url')
            api_key = self.config.get('api_key')
            
            if not grafana_url or not api_key:
                raise ValueError("缺少 Grafana 配置：grafana_url 或 api_key")
            
            inspector = GrafanaInspector(grafana_url, api_key)
            
            # 2. 执行检查
            print("\n📋 步骤 1: 检查主机和中间件状态...")
            inspection_results = inspector.run_full_inspection()
            self.results['checks'] = inspection_results['checks']
            self.results['alerts'] = inspection_results.get('alerts', [])
            self.results['issues'] = inspection_results.get('issues', [])
            self.results['score'] = inspection_results['score']
            self.results['status'] = inspection_results['status']
            
            # 3. 捕获监控截图
            print("\n📸 步骤 2: 捕获监控面板截图...")
            dashboard_uid = self.config.get('dashboard_uid')
            if dashboard_uid:
                capturer = GrafanaScreenshot(grafana_url, api_key)
                panel_ids = self.config.get('panel_ids', [])
                
                if panel_ids:
                    screenshot_paths = capturer.capture_multiple_panels(
                        dashboard_uid,
                        panel_ids,
                        output_dir=self.config.get('screenshot_dir', './screenshots')
                    )
                    self.results['screenshots'] = [p for p in screenshot_paths if p]
                else:
                    screenshot_path = capturer.capture_dashboard(dashboard_uid)
                    self.results['screenshots'] = [screenshot_path]
            
            # 4. 生成报告
            print("\n📝 步骤 3: 生成巡检报告...")
            report_markdown = inspector.generate_report()
            self.results['report_markdown'] = report_markdown
            
            # 5. 发送到飞书（如果配置了）
            print("\n📤 步骤 4: 发送报告到飞书文档...")
            app_id = self.config.get('feishu_app_id')
            app_secret = self.config.get('feishu_app_secret')
            
            if app_id and app_secret:
                from feishu_report import FeishuReportGenerator
                generator = FeishuReportGenerator(app_id, app_secret)
                send_result = generator.send_report(
                    inspection_results=self.results,
                    report_markdown=report_markdown,
                    parent_folder_token=self.config.get('feishu_folder_token')
                )
                self.results['report_url'] = send_result.get('url')
                self.results['feishu_doc_id'] = send_result.get('doc_id')
            else:
                print("⚠️  未配置飞书参数，跳过发送步骤")
            
            # 6. 保存本地报告
            self._save_local_report()
            
            print("\n" + "=" * 60)
            print("✅ 巡检完成!")
            print("=" * 60)
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            print(f"\n❌ 巡检失败：{str(e)}")
            return self.results
    
    def _save_local_report(self):
        """保存本地报告文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.config.get('output_dir', './reports')
        # 使用绝对路径
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存 JSON 结果
        json_path = os.path.join(output_dir, f"inspection_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 保存 Markdown 报告
        md_path = os.path.join(output_dir, f"inspection_{timestamp}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.results.get('report_markdown', ''))
        
        print(f"📁 本地报告已保存:")
        print(f"   JSON: {json_path}")
        print(f"   Markdown: {md_path}")
    
    def _print_summary(self):
        """打印巡检摘要"""
        print(f"\n📊 巡检摘要:")
        print(f"   状态：{self.results['status'].upper()}")
        print(f"   健康评分：{self.results['score']}/100")
        print(f"   检查项：{len(self.results['checks'])}")
        print(f"   告警数：{len(self.results['alerts'])}")
        print(f"   异常数：{len(self.results['issues'])}")
        print(f"   截图数：{len(self.results['screenshots'])}")
        
        if self.results.get('report_url'):
            print(f"\n🔗 飞书报告：{self.results['report_url']}")


def load_config(config_file: str) -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # 默认配置
    default_config = {
        "grafana_url": "http://localhost:3000",
        "api_key": "your_api_key",
        "dashboard_uid": "your_dashboard_uid",
        "panel_ids": [],  # 可选，指定要截图的面板 ID
        "screenshot_dir": "./screenshots",
        "output_dir": "./reports",
        "feishu_app_id": None,
        "feishu_app_secret": None,
        "feishu_folder_token": None
    }
    
    # 从命令行或配置文件加载
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config = load_config(config_file)
    else:
        config = default_config
    
    # 合并配置
    final_config = {**default_config, **config}
    
    # 执行巡检
    inspection = AutoInspection(final_config)
    results = inspection.run_inspection()
    
    # 返回退出码
    if results['status'] == 'failed':
        sys.exit(1)
    elif results['score'] < 50:
        sys.exit(2)  # 严重警告
    elif results['score'] < 70:
        sys.exit(3)  # 警告
    else:
        sys.exit(0)  # 正常


if __name__ == "__main__":
    main()
