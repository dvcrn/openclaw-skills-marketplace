#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计分析工具 - 分析自动回复效果和用户互动数据
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class Analytics:
    """数据分析器"""
    
    def __init__(self, stats_path='stats.json', logs_path='douyin_bot.log'):
        self.stats_path = Path(stats_path)
        self.logs_path = Path(logs_path)
    
    def load_stats(self):
        """加载统计数据"""
        if not self.stats_path.exists():
            print("⚠️  统计数据文件不存在")
            return {}
        
        with open(self.stats_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_logs(self):
        """解析日志文件"""
        if not self.logs_path.exists():
            print("⚠️  日志文件不存在")
            return []
        
        entries = []
        with open(self.logs_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # 解析日志格式：2024-01-01 12:00:00 - LEVEL - message
                    parts = line.split(' - ', 2)
                    if len(parts) == 3:
                        timestamp_str = parts[0]
                        level = parts[1]
                        message = parts[2]
                        
                        timestamp = datetime.strptime(
                            timestamp_str, 
                            '%Y-%m-%d %H:%M:%S'
                        )
                        
                        entries.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })
                except Exception:
                    continue
        
        return entries
    
    def daily_report(self, days=7):
        """生成每日报告"""
        stats = self.load_stats()
        logs = self.parse_logs()
        
        print("\n" + "=" * 60)
        print("📈 抖音自动回复助手 - 数据分析报告")
        print("=" * 60)
        
        # 总体统计
        print("\n📊 总体数据:")
        print(f"  总回复数：{stats.get('total_replies', 0)}")
        print(f"  今日回复：{stats.get('today_replies', 0)}")
        print(f"  最后更新：{stats.get('last_reset', 'N/A')}")
        
        # 关键词统计
        keywords = stats.get('keywords_triggered', {})
        if keywords:
            print("\n🔑 热门关键词 TOP 10:")
            sorted_keywords = sorted(
                keywords.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            for i, (keyword, count) in enumerate(sorted_keywords, 1):
                bar = '█' * min(count, 50)
                print(f"  {i:2d}. {keyword:15s} {count:4d} 次 {bar}")
        
        # 日志分析
        if logs:
            print("\n📝 最近活动:")
            reply_logs = [
                log for log in logs 
                if '回复成功' in log['message']
            ][-10:]
            
            for log in reply_logs:
                time_str = log['timestamp'].strftime('%m-%d %H:%M')
                print(f"  {time_str} - {log['message'][:50]}")
        
        # 回复成功率分析
        if logs:
            total_attempts = len([
                log for log in logs 
                if '回复评论' in log['message']
            ])
            successful = len([
                log for log in logs 
                if '回复成功' in log['message']
            ])
            
            if total_attempts > 0:
                success_rate = (successful / total_attempts) * 100
                print("\n✅ 回复成功率:")
                print(f"  总尝试：{total_attempts}")
                print(f"  成功：{successful}")
                print(f"  成功率：{success_rate:.1f}%")
        
        print("\n" + "=" * 60 + "\n")
    
    def export_report(self, output_path='report.json'):
        """导出报告为 JSON"""
        stats = self.load_stats()
        logs = self.parse_logs()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_replies': stats.get('total_replies', 0),
                'today_replies': stats.get('today_replies', 0),
                'last_reset': stats.get('last_reset', 'N/A')
            },
            'keywords': stats.get('keywords_triggered', {}),
            'recent_activity': [
                {
                    'timestamp': log['timestamp'].isoformat(),
                    'message': log['message']
                }
                for log in logs[-100:]
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 报告已导出到：{output_path}")
    
    def clear_stats(self):
        """清空统计数据"""
        if self.stats_path.exists():
            confirm = input("确定要清空所有统计数据吗？(y/N): ")
            if confirm.lower() == 'y':
                default_stats = {
                    'total_replies': 0,
                    'today_replies': 0,
                    'last_reset': datetime.now().strftime('%Y-%m-%d'),
                    'keywords_triggered': {}
                }
                
                with open(self.stats_path, 'w', encoding='utf-8') as f:
                    json.dump(default_stats, f, ensure_ascii=False, indent=2)
                
                print("✓ 统计数据已清空")
        else:
            print("⚠️  统计数据文件不存在")


def main():
    analytics = Analytics()
    
    if len(sys.argv) < 2:
        print("用法：python analytics.py <command>")
        print("\n命令:")
        print("  report        - 生成数据分析报告")
        print("  export        - 导出报告为 JSON")
        print("  clear         - 清空统计数据")
        return
    
    command = sys.argv[1]
    
    if command == 'report':
        analytics.daily_report()
    
    elif command == 'export':
        output = sys.argv[2] if len(sys.argv) > 2 else 'report.json'
        analytics.export_report(output)
    
    elif command == 'clear':
        analytics.clear_stats()
    
    else:
        print(f"未知命令：{command}")


if __name__ == '__main__':
    import sys
    main()
