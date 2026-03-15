#!/usr/bin/env python3
"""
Grafana 监控面板截图脚本
使用 Grafana 渲染 API 获取面板截图
"""

import requests
import base64
import sys
import os
from datetime import datetime
from typing import Optional


class GrafanaScreenshot:
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def capture_dashboard(
        self,
        dashboard_uid: str,
        panel_id: Optional[int] = None,
        time_from: str = "now-6h",
        time_to: str = "now",
        width: int = 1920,
        height: int = 1080,
        output_path: Optional[str] = None
    ) -> str:
        """
        捕获 Grafana 面板截图
        
        Args:
            dashboard_uid: 面板 UID
            panel_id: 面板 ID（可选，不传则截取整个仪表盘）
            time_from: 开始时间
            time_to: 结束时间
            width: 截图宽度
            height: 截图高度
            output_path: 输出文件路径
        
        Returns:
            截图文件路径
        """
        try:
            # 构建渲染 URL
            if panel_id:
                render_url = f"{self.grafana_url}/render/d-solo/{dashboard_uid}"
                params = {
                    'panelId': str(panel_id),
                    'from': time_from,
                    'to': time_to,
                    'width': str(width),
                    'height': str(height),
                    'tz': 'Asia/Shanghai'
                }
            else:
                render_url = f"{self.grafana_url}/render/d/{dashboard_uid}"
                params = {
                    'from': time_from,
                    'to': time_to,
                    'width': str(width),
                    'height': str(height),
                    'tz': 'Asia/Shanghai'
                }
            
            # 使用浏览器渲染（需要 Grafana 配置渲染服务）
            # 或者使用 Puppeteer/Playwright 直接访问页面截图
            
            print(f"正在捕获仪表盘：{dashboard_uid}")
            print(f"渲染 URL: {render_url}")
            print(f"参数：{params}")
            
            # 注意：Grafana 渲染服务需要单独配置
            # 这里返回一个占位说明，实际使用时需要配置 Grafana Image Renderer
            
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"grafana_screenshot_{timestamp}.png"
            
            # 使用 requests 下载（需要 Grafana 配置了渲染插件）
            try:
                response = requests.get(render_url, params=params, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"截图已保存：{output_path}")
                    return output_path
                else:
                    print(f"渲染服务返回错误：HTTP {response.status_code}")
                    print("提示：请确保 Grafana 已安装并配置 Image Renderer 插件")
            except Exception as e:
                print(f"渲染服务不可用：{str(e)}")
            
            # 备用方案：返回说明文档
            placeholder_content = f"""Grafana 监控截图
================
时间：{datetime.now().isoformat()}
仪表盘：{dashboard_uid}
面板 ID: {panel_id or '整个仪表盘'}
时间范围：{time_from} - {time_to}

注意：需要配置 Grafana Image Renderer 插件才能自动生成截图。
配置方法：
1. 在 Grafana 中安装 grafana-image-renderer 插件
2. 或在 docker-compose 中添加渲染服务
3. 配置 grafana.ini 中的 [rendering] 部分

或者直接访问：{render_url}
"""
            
            output_path = output_path.replace('.png', '.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            print(f"说明文档已保存：{output_path}")
            return output_path
            
        except Exception as e:
            print(f"截图失败：{str(e)}")
            raise
    
    def capture_multiple_panels(
        self,
        dashboard_uid: str,
        panel_ids: list,
        output_dir: str = "./screenshots"
    ) -> list:
        """捕获多个面板截图"""
        os.makedirs(output_dir, exist_ok=True)
        screenshot_paths = []
        
        for panel_id in panel_ids:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"panel_{panel_id}_{timestamp}.png")
                path = self.capture_dashboard(dashboard_uid, panel_id=panel_id, output_path=output_path)
                screenshot_paths.append(path)
            except Exception as e:
                print(f"面板 {panel_id} 截图失败：{str(e)}")
                screenshot_paths.append(None)
        
        return screenshot_paths


def main():
    if len(sys.argv) < 3:
        print("用法：python capture_dashboard.py <grafana_url> <api_key> <dashboard_uid> [panel_id]")
        sys.exit(1)
    
    grafana_url = sys.argv[1]
    api_key = sys.argv[2]
    dashboard_uid = sys.argv[3]
    panel_id = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    capturer = GrafanaScreenshot(grafana_url, api_key)
    
    if panel_id:
        output_path = capturer.capture_dashboard(dashboard_uid, panel_id=panel_id)
    else:
        output_path = capturer.capture_dashboard(dashboard_uid)
    
    print(f"\n截图完成：{output_path}")


if __name__ == "__main__":
    main()
