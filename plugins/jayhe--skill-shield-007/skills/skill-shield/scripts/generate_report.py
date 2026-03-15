#!/usr/bin/env python3
"""
生成skill-shield扫描报告的格式化版本
"""

import json
import os
import sys
from datetime import datetime

def load_risk_report():
    """加载风险报告"""
    report_path = os.path.expanduser("~/.openclaw/workspace/memory/shield-risks.json")
    if not os.path.exists(report_path):
        return None
    
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_formatted_report(report):
    """生成格式化的报告"""
    if not report:
        return "⚠️ 未找到风险报告，请先运行skill-shield扫描"
    
    last_scan = report.get('lastScanTime', '未知时间')
    skills = report.get('skills', {})
    
    # 统计风险等级
    severity_counts = {
        'severe': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for skill_data in skills.values():
        severity = skill_data.get('severity', 'low')
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    # 生成报告
    report_lines = []
    report_lines.append("🛡️ **Skill Shield 安全扫描报告**")
    report_lines.append("")
    report_lines.append(f"**扫描时间**: {last_scan}")
    report_lines.append(f"**扫描技能数**: {len(skills)}")
    report_lines.append("")
    report_lines.append("**风险统计**:")
    report_lines.append(f"  🔴 严重风险: {severity_counts['severe']}")
    report_lines.append(f"  🟠 高风险: {severity_counts['high']}")
    report_lines.append(f"  🟡 中风险: {severity_counts['medium']}")
    report_lines.append(f"  🟢 低风险/安全: {severity_counts['low']}")
    report_lines.append("")
    
    # 高风险技能列表
    high_risk_skills = []
    for skill_name, skill_data in skills.items():
        severity = skill_data.get('severity', 'low')
        if severity in ['severe', 'high']:
            risks = skill_data.get('risks', [])
            risk_count = len(risks)
            high_risk_skills.append((skill_name, severity, risk_count))
    
    if high_risk_skills:
        report_lines.append("**高风险技能列表**:")
        for skill_name, severity, risk_count in sorted(high_risk_skills, key=lambda x: x[1], reverse=True):
            severity_emoji = "🔴" if severity == 'severe' else "🟠"
            report_lines.append(f"  {severity_emoji} {skill_name} ({risk_count}个风险项)")
    
    report_lines.append("")
    report_lines.append("**建议**:")
    report_lines.append("1. 定期审查高风险技能")
    report_lines.append("2. 将信任的技能添加到allowlist")
    report_lines.append("3. 及时更新技能到最新版本")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*由 Skill Shield 安全管理系统自动生成*")
    
    return "\n".join(report_lines)

def main():
    """主函数"""
    report = load_risk_report()
    formatted_report = generate_formatted_report(report)
    print(formatted_report)

if __name__ == "__main__":
    main()