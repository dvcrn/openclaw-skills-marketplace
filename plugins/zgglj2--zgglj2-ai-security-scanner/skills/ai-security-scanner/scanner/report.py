"""
报告生成模块
生成飞书文档报告和HTML报告
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def generate_feishu_report(
    scan_result: dict,
    doc_title: str = None,
    html_file: Optional[str] = None,
) -> str:
    """生成飞书文档格式的 Markdown 报告"""
    
    if doc_title is None:
        doc_title = f"AI Agent 安全扫描报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 构建报告内容
    sections = []
    
    # 标题和元信息
    sections.append(f"""# {doc_title}

> 扫描时间: {scan_result.get('started_at', 'N/A')}  
> 扫描 ID: {scan_result.get('scan_id', 'N/A')}  
> 耗时: {scan_result.get('duration_seconds', 0):.2f} 秒  
> 扫描引擎: AI Agent Security Scanner v0.1.0 (改进版)

---
""")
    
    # 扫描摘要
    summary = scan_result.get('findings_by_severity', {})
    total = scan_result.get('total_findings', 0)
    assets = scan_result.get('assets', [])
    
    sections.append(f"""## 一、扫描摘要

### 资产发现

| 类型 | 名称 | 路径 | Skills | 状态 |
|------|------|------|--------|------|
{chr(10).join(f"| {a.get('type', 'N/A')} | {a.get('name', 'N/A')} | {a.get('path', 'N/A')} | {len(a.get('skills', []))} | ✅ 已扫描 |" for a in assets)}

### 风险统计

| 严重等级 | 数量 | 占比 |
|---------|------|------|
| 🔴 Critical | {summary.get('critical', 0)} | {summary.get('critical', 0) / total * 100 if total > 0 else 0:.1f}% |
| 🟠 High | {summary.get('high', 0)} | {summary.get('high', 0) / total * 100 if total > 0 else 0:.1f}% |
| 🟡 Medium | {summary.get('medium', 0)} | {summary.get('medium', 0) / total * 100 if total > 0 else 0:.1f}% |
| ⚪ Low/Info | {summary.get('low', 0) + summary.get('info', 0)} | {(summary.get('low', 0) + summary.get('info', 0)) / total * 100 if total > 0 else 0:.1f}% |
| **总计** | **{total}** | **100%** |

---
""")
    
    # 收集所有发现
    all_findings = []
    for asset in assets:
        # Asset 级别的发现
        for finding in asset.get('findings', []):
            finding['asset_name'] = asset.get('name', 'Unknown')
            all_findings.append(finding)
        
        # Skill 级别的发现
        for skill in asset.get('skills', []):
            for finding in skill.get('findings', []):
                finding['skill_name'] = skill.get('name', 'Unknown')
                finding['asset_name'] = asset.get('name', 'Unknown')
                all_findings.append(finding)
        
        # API Key 级别的发现
        for key in asset.get('api_keys', []):
            for finding in key.get('findings', []):
                finding['key_provider'] = key.get('provider', 'Unknown')
                finding['asset_name'] = asset.get('name', 'Unknown')
                all_findings.append(finding)
    
    # 按严重等级排序
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    all_findings.sort(key=lambda f: severity_order.get(f.get('severity', 'info'), 5))
    
    # Critical 风险
    critical_findings = [f for f in all_findings if f.get('severity') == 'critical']
    if critical_findings:
        sections.append(f"""## 二、🔴 Critical 风险详情 ({len(critical_findings)}个)

**这些风险需要立即处理！**

{chr(10).join(_format_finding(f, i+1) for i, f in enumerate(critical_findings[:20]))}

---
""")
    
    # High 风险
    high_findings = [f for f in all_findings if f.get('severity') == 'high']
    if high_findings:
        sections.append(f"""## 三、🟠 High 风险详情 ({len(high_findings)}个)

**这些风险需要尽快处理！**

{chr(10).join(_format_finding(f, i+1) for i, f in enumerate(high_findings[:20]))}

---
""")
    
    # Medium 风险
    medium_findings = [f for f in all_findings if f.get('severity') == 'medium']
    if medium_findings:
        sections.append(f"""## 四、🟡 Medium 风险详情 ({len(medium_findings)}个)

{chr(10).join(_format_finding(f, i+1) for i, f in enumerate(medium_findings[:20]))}

---
""")
    
    # Low/Info 风险
    low_findings = [f for f in all_findings if f.get('severity') in ['low', 'info']]
    if low_findings:
        sections.append(f"""## 五、⚪ Low/Info 提示 ({len(low_findings)}个)

这些是提示性信息，通常无需处理。

{chr(10).join(_format_finding_simple(f, i+1) for i, f in enumerate(low_findings[:30]))}

---
""")
    
    # 误报分析
    sections.append("""## 六、误报分析

### 6.1 扫描器改进

本次扫描使用**改进版扫描器**，已应用以下优化：

| 优化项 | 说明 |
|--------|------|
| 官方 Skill 白名单 | 54 个官方 Skill 跳过扫描 |
| 上下文感知 | 区分代码块和普通文本 |
| 可信域名白名单 | 官方 API 调用不报高风险 |
| 分级报告 | Critical/High/Medium/Low/Info |

### 6.2 进一步减少误报

如需进一步减少误报，可以：

1. **启用 LLM 语义分析**: `aascan scan --llm --llm-provider zhipu`
2. **添加自定义白名单**: 编辑 `config/scanner.yaml`
3. **人工审核**: Critical/High 级别建议人工确认

---
""")
    
    # 修复建议
    sections.append("""## 七、修复建议

### 7.1 短期措施

1. **审核 Critical/High 发现**: 逐一确认是否为真实风险
2. **检查 API Key 存储**: 确保没有硬编码的凭证
3. **审查外部请求目标**: 确认数据流向可信

### 7.2 长期措施

1. **建立 Skill 审计流程**: 安装前检查 Skill 来源和内容
2. **配置 LLM 分析**: 启用语义分析减少误报
3. **定期扫描**: 建立持续监控机制
4. **威胁情报集成**: 对接 VirusTotal 等服务

---
""")
    
    # 附录
    appendix_section = f"""## 八、附录

### 8.1 扫描配置

- 扫描引擎: 规则引擎（正则匹配）+ 上下文分析
- 官方 Skill 跳过: 是
- LLM 分析: 否
- API Key 验证: 否

### 8.2 工具信息

- 工具: AI Agent Security Scanner
- 版本: 0.1.0 (改进版)
- 仓库: ~/.openclaw/skills/ai-security-scanner

### 8.3 相关报告
"""
    
    # 如果有HTML文件，添加引用
    if html_file:
        appendix_section += f"""
**HTML 完整报告**: `{html_file}`

> 📎 HTML 报告包含更详细的风险发现列表和交互式内容，请在本地浏览器中打开查看。

**查看方法**:
```bash
# 在浏览器中打开
open {html_file}

# 或使用 Python HTTP 服务器
python3 -m http.server 8000
# 然后访问 http://localhost:8000/{Path(html_file).name}
```
"""
    
    appendix_section += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*🦐 AI Agent Security Scanner*
"""
    
    sections.append(appendix_section)
    
    return '\n'.join(sections)


def generate_html_report(
    scan_result: dict,
    output_path: Optional[Path] = None,
) -> str:
    """生成 HTML 格式的详细报告"""
    
    scan_id = scan_result.get('scan_id', 'unknown')
    started_at = scan_result.get('started_at', 'N/A')
    duration = scan_result.get('duration_seconds', 0)
    
    summary = scan_result.get('findings_by_severity', {})
    total = scan_result.get('total_findings', 0)
    assets = scan_result.get('assets', [])
    
    # 收集所有发现
    all_findings = []
    for asset in assets:
        for finding in asset.get('findings', []):
            finding['asset_name'] = asset.get('name', 'Unknown')
            all_findings.append(finding)
        
        for skill in asset.get('skills', []):
            for finding in skill.get('findings', []):
                finding['skill_name'] = skill.get('name', 'Unknown')
                finding['asset_name'] = asset.get('name', 'Unknown')
                all_findings.append(finding)
        
        for key in asset.get('api_keys', []):
            for finding in key.get('findings', []):
                finding['key_provider'] = key.get('provider', 'Unknown')
                finding['asset_name'] = asset.get('name', 'Unknown')
                all_findings.append(finding)
    
    # 按严重等级排序
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    all_findings.sort(key=lambda f: severity_order.get(f.get('severity', 'info'), 5))
    
    # 生成资产表格行
    asset_rows = '\n'.join(
        f'<tr><td>{a.get("type", "N/A")}</td><td>{a.get("name", "N/A")}</td>'
        f'<td><code>{a.get("path", "N/A")}</code></td><td>{len(a.get("skills", []))}</td>'
        f'<td>{len(a.get("findings", []))}</td></tr>'
        for a in assets
    )
    
    # 生成发现表格行
    finding_rows = ''
    for f in all_findings[:100]:  # 限制100个
        severity = f.get('severity', 'info')
        severity_class = severity
        severity_text = severity.upper()
        
        finding_rows += f'''
        <tr>
            <td><span class="{severity_class}">{severity_text}</span></td>
            <td>{f.get("type", "N/A")}</td>
            <td>{f.get("title", "N/A")}</td>
            <td><code>{f.get("location", "-")}</code></td>
            <td>{f.get("line_number", "-")}</td>
            <td>{f.get("recommendation", "N/A")[:100]}...</td>
        </tr>'''
    
    # HTML 模板
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Agent Security Scan Report - {scan_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header .meta {{ font-size: 0.9em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h3 {{ font-size: 0.9em; color: #666; margin-bottom: 10px; }}
        .summary-card .value {{ font-size: 2.5em; font-weight: bold; }}
        .summary-card.critical .value {{ color: #dc3545; }}
        .summary-card.high .value {{ color: #fd7e14; }}
        .summary-card.medium .value {{ color: #ffc107; }}
        .summary-card.low .value {{ color: #6c757d; }}
        
        .section {{ margin-bottom: 40px; }}
        .section h2 {{
            color: #333;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        tr:hover {{ background: #f9f9f9; }}
        
        .critical {{ color: #dc3545; font-weight: bold; }}
        .high {{ color: #fd7e14; font-weight: bold; }}
        .medium {{ color: #ffc107; font-weight: bold; }}
        .low {{ color: #6c757d; }}
        .info {{ color: #17a2b8; }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-critical {{ background: #dc3545; color: white; }}
        .badge-high {{ background: #fd7e14; color: white; }}
        .badge-medium {{ background: #ffc107; color: black; }}
        .badge-low {{ background: #6c757d; color: white; }}
        .badge-info {{ background: #17a2b8; color: white; }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Agent Security Scan Report</h1>
            <div class="meta">
                Scan ID: {scan_id} | Started: {started_at} | Duration: {duration:.2f}s
            </div>
        </div>
        
        <div class="content">
            <div class="summary">
                <div class="summary-card critical">
                    <h3>🔴 Critical</h3>
                    <div class="value">{summary.get('critical', 0)}</div>
                </div>
                <div class="summary-card high">
                    <h3>🟠 High</h3>
                    <div class="value">{summary.get('high', 0)}</div>
                </div>
                <div class="summary-card medium">
                    <h3>🟡 Medium</h3>
                    <div class="value">{summary.get('medium', 0)}</div>
                </div>
                <div class="summary-card low">
                    <h3>⚪ Low/Info</h3>
                    <div class="value">{summary.get('low', 0) + summary.get('info', 0)}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Assets Discovered</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Name</th>
                            <th>Path</th>
                            <th>Skills</th>
                            <th>Findings</th>
                        </tr>
                    </thead>
                    <tbody>
                        {asset_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>🔍 Findings Detail</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Type</th>
                                <th>Title</th>
                                <th>Location</th>
                                <th>Line</th>
                                <th>Recommendation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {finding_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h2>📝 Notes</h2>
                <ul>
                    <li>This report was generated by <strong>AI Agent Security Scanner v0.1.0 (Improved)</strong></li>
                    <li>Official skills are skipped to reduce false positives</li>
                    <li>For detailed analysis, consider enabling LLM analysis with <code>--llm</code> flag</li>
                    <li>Custom whitelist can be configured in <code>config/scanner.yaml</code></li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            Generated by AI Agent Security Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🦐
        </div>
    </div>
</body>
</html>'''
    
    # 保存文件
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        console.print(f"[green]✓[/green] HTML 报告已保存: {output_path}")
    
    return html


def _format_finding(finding: dict, index: int) -> str:
    """格式化单个发现（详细版）"""
    lines = []
    lines.append(f"#### {index}. {finding.get('title', 'Unknown')}")
    lines.append("")
    
    if skill_name := finding.get('skill_name'):
        lines.append(f"- **Skill**: {skill_name}")
    if asset_name := finding.get('asset_name'):
        lines.append(f"- **资产**: {asset_name}")
    if location := finding.get('location'):
        lines.append(f"- **位置**: `{location}`")
    if line_num := finding.get('line_number'):
        lines.append(f"- **行号**: {line_num}")
    
    lines.append("")
    lines.append(f"**描述**: {finding.get('description', 'N/A')}")
    
    if evidence := finding.get('evidence'):
        lines.append(f"**证据**:")
        lines.append(f"```")
        lines.append(evidence[:200])
        lines.append(f"```")
    
    lines.append(f"**建议**: {finding.get('recommendation', 'N/A')}")
    lines.append("")
    
    return '\n'.join(lines)


def _format_finding_simple(finding: dict, index: int) -> str:
    """格式化单个发现（简化版）"""
    skill_name = finding.get('skill_name', finding.get('asset_name', 'Unknown'))
    title = finding.get('title', 'Unknown')
    location = finding.get('location', '')
    
    return f"{index}. **{skill_name}**: {title}" + (f" (`{Path(location).name}`)" if location else "")
