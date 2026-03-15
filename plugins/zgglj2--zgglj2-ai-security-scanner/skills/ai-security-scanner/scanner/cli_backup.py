"""
CLI 工具
命令行接口
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

from scanner.discovery import AssetDiscovery
from scanner.apikey import APIKeyScanner
from scanner.content import ContentScanner
from scanner.content_v2 import ImprovedContentScanner  # 使用改进版
from scanner.models import ScanResult, Severity

app = typer.Typer(
    name="aascan",
    help="AI Agent Security Scanner - 检测 AI Agent 中的安全风险",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="输出报告路径（JSON 格式）",
    ),
    output_html: Optional[Path] = typer.Option(
        None,
        "--html",
        help="输出 HTML 报告路径",
    ),
    verify_keys: bool = typer.Option(
        False,
        "--verify-keys",
        help="验证 API Key 有效性",
    ),
    enable_llm: bool = typer.Option(
        False,
        "--llm",
        help="启用 LLM 语义分析",
    ),
    llm_provider: str = typer.Option(
        "openai",
        "--llm-provider",
        help="LLM 提供商 (openai, zhipu)",
    ),
    verbose: bool = typer.Option(
        False,
        "-v", "--verbose",
        help="详细输出",
    ),
):
    """
    执行完整安全扫描
    
    示例:
        aascan scan
        aascan scan -o report.json
        aascan scan --llm --llm-provider zhipu
    """
    
    # 创建扫描结果
    scan_result = ScanResult(
        scan_id=str(uuid.uuid4())[:8],
        started_at=datetime.now(),
    )
    
    console.print(Panel.fit(
        "[bold blue]🛡️ AI Agent Security Scanner[/bold blue]\n"
        f"Scan ID: {scan_result.scan_id}",
        border_style="blue",
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        
        # 1. 资产发现
        task = progress.add_task("[cyan]Phase 1/3: 资产发现...", total=100)
        discovery = AssetDiscovery()
        assets = discovery.discover_all()
        scan_result.assets = assets
        progress.update(task, completed=100)
        
        if not assets:
            console.print("[yellow]未发现 AI Agent 安装[/yellow]")
            raise typer.Exit(0)
        
        console.print(f"[green]✓[/green] 发现 {len(assets)} 个 AI Agent")
        
        # 2. API Key 检测
        task = progress.add_task("[cyan]Phase 2/3: API Key 检测...", total=100)
        key_scanner = APIKeyScanner(verify_keys=verify_keys)
        all_keys = key_scanner.scan(assets)
        for key in all_keys:
            for finding in key.findings:
                scan_result.add_finding(finding)
        progress.update(task, completed=100)
        
        if all_keys:
            console.print(f"[yellow]⚠[/yellow] 发现 {len(all_keys)} 个 API Key")
        
        # 3. 内容扫描（使用改进版）
        task = progress.add_task("[cyan]Phase 3/3: 内容风险扫描（改进版）...", total=100)
        content_scanner = ImprovedContentScanner(
            enable_llm=enable_llm,
            llm_provider=llm_provider,
            skip_official=True,  # 跳过官方 Skill
        )
        content_findings = content_scanner.scan(assets)
        for finding in content_findings:
            scan_result.add_finding(finding)
        progress.update(task, completed=100)
    
    # 完成
    scan_result.completed_at = datetime.now()
    scan_result.duration_seconds = (
        scan_result.completed_at - scan_result.started_at
    ).total_seconds()
    
    # 显示结果
    _display_results(scan_result, verbose)
    
    # 输出报告
    if output:
        _save_json_report(scan_result, output)
        console.print(f"[green]✓[/green] JSON 报告已保存: {output}")
    
    if output_html:
        _save_html_report(scan_result, output_html)
        console.print(f"[green]✓[/green] HTML 报告已保存: {output_html}")
    
    # 返回码
    if scan_result.findings_by_severity.get("critical", 0) > 0:
        raise typer.Exit(2)  # 严重风险
    elif scan_result.total_findings > 0:
        raise typer.Exit(1)  # 有风险
    else:
        raise typer.Exit(0)  # 无风险


@app.command()
def discover():
    """
    仅执行资产发现（不扫描风险）
    """
    console.print("[cyan]🔍 正在发现 AI Agent 资产...[/cyan]")
    
    discovery = AssetDiscovery()
    assets = discovery.discover_all()
    
    if not assets:
        console.print("[yellow]未发现 AI Agent 安装[/yellow]")
        return
    
    table = Table(title="发现的 AI Agent")
    table.add_column("类型", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("路径", style="dim")
    table.add_column("版本")
    table.add_column("Skills")
    table.add_column("Plugins")
    
    for asset in assets:
        table.add_row(
            asset.type.value,
            asset.name,
            str(asset.path),
            asset.version or "-",
            str(len(asset.skills)),
            str(len(asset.plugins)),
        )
    
    console.print(table)
    
    # Skills 详情
    if any(asset.skills for asset in assets):
        skill_table = Table(title="Skills 列表")
        skill_table.add_column("名称", style="cyan")
        skill_table.add_column("来源")
        skill_table.add_column("有脚本")
        skill_table.add_column("来源 Agent")
        
        for asset in assets:
            for skill in asset.skills:
                skill_table.add_row(
                    skill.name,
                    skill.source,
                    "✓" if skill.has_scripts else "-",
                    asset.name,
                )
        
        console.print(skill_table)


@app.command()
def check_apikey(
    path: Optional[Path] = typer.Argument(
        None,
        help="要扫描的路径（默认为当前目录）",
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        help="验证 Key 有效性",
    ),
):
    """
    检测 API Key 泄露
    
    示例:
        aascan check-apikey
        aascan check-apikey /path/to/project
    """
    scan_path = path or Path.cwd()
    
    console.print(f"[cyan]🔍 扫描路径: {scan_path}[/cyan]")
    
    scanner = APIKeyScanner(verify_keys=verify)
    
    # 扫描目录
    findings = scanner.scan_directory(scan_path)
    
    if not findings:
        console.print("[green]✓ 未发现 API Key 泄露[/green]")
        return
    
    table = Table(title=f"发现的 API Key ({len(findings)})")
    table.add_column("Provider", style="cyan")
    table.add_column("严重等级", style="red")
    table.add_column("位置")
    table.add_column("建议")
    
    for finding in findings[:20]:  # 限制显示数量
        table.add_row(
            finding.metadata.get("provider", "-"),
            finding.severity.value,
            finding.location,
            finding.recommendation[:50] + "...",
        )
    
    console.print(table)
    
    if len(findings) > 20:
        console.print(f"[yellow]... 还有 {len(findings) - 20} 个发现[/yellow]")


@app.command()
def check_skill(
    skill_path: Path = typer.Argument(
        ...,
        help="Skill 目录路径",
    ),
    llm: bool = typer.Option(
        False,
        "--llm",
        help="启用 LLM 分析",
    ),
):
    """
    检测单个 Skill 风险
    
    示例:
        aascan check-skill /path/to/skill
    """
    if not skill_path.exists():
        console.print(f"[red]错误: 路径不存在: {skill_path}[/red]")
        raise typer.Exit(1)
    
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        console.print(f"[red]错误: 未找到 SKILL.md: {skill_file}[/red]")
        raise typer.Exit(1)
    
    from scanner.models import Skill
    
    console.print(f"[cyan]🔍 扫描 Skill: {skill_path.name}[/cyan]")
    
    # 创建 Skill 对象
    skill = Skill(
        name=skill_path.name,
        path=skill_path,
        source="custom",
    )
    
    # 扫描脚本
    for ext in ['*.sh', '*.py', '*.js']:
        skill.script_files.extend([str(s) for s in skill_path.glob(ext)])
    skill.has_scripts = len(skill.script_files) > 0
    
    # 扫描
    scanner = ContentScanner(enable_llm=llm)
    findings = scanner.scan_skill(skill)
    
    if not findings:
        console.print("[green]✓ 未发现风险[/green]")
        return
    
    table = Table(title=f"发现的风险 ({len(findings)})")
    table.add_column("类型", style="cyan")
    table.add_column("严重等级", style="red")
    table.add_column("描述")
    table.add_column("位置")
    
    for finding in findings:
        table.add_row(
            finding.type.value,
            finding.severity.value,
            finding.description[:50],
            finding.location or "-",
        )
    
    console.print(table)


def _display_results(result: ScanResult, verbose: bool = False):
    """显示扫描结果"""
    console.print()
    
    # 摘要
    summary = result.summarize()
    
    summary_table = Table(title="扫描摘要", show_header=False)
    summary_table.add_column("指标", style="cyan")
    summary_table.add_column("值", style="bold")
    
    summary_table.add_row("扫描 ID", summary["scan_id"])
    summary_table.add_row("发现资产", str(summary["assets_found"]))
    summary_table.add_row("总发现", str(summary["total_findings"]))
    summary_table.add_row("Critical", f"[red]{summary['critical']}[/red]")
    summary_table.add_row("High", f"[orange]{summary['high']}[/orange]")
    summary_table.add_row("Medium", f"[yellow]{summary['medium']}[/yellow]")
    summary_table.add_row("Low", f"[dim]{summary['low']}[/dim]")
    
    console.print(summary_table)
    
    # 风险列表
    if result.total_findings > 0:
        console.print()
        
        findings_table = Table(title="风险发现")
        findings_table.add_column("ID", style="dim")
        findings_table.add_column("类型", style="cyan")
        findings_table.add_column("等级", style="red")
        findings_table.add_column("标题")
        findings_table.add_column("位置")
        
        # 收集所有发现
        all_findings = []
        for asset in result.assets:
            all_findings.extend(asset.findings)
            for skill in asset.skills:
                all_findings.extend(skill.findings)
            for key in asset.api_keys:
                all_findings.extend(key.findings)
        
        # 按严重等级排序
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        all_findings.sort(key=lambda f: severity_order.get(f.severity.value, 5))
        
        for finding in all_findings[:50]:  # 限制显示
            severity_style = {
                "critical": "[red]CRITICAL[/red]",
                "high": "[orange]HIGH[/orange]",
                "medium": "[yellow]MEDIUM[/yellow]",
                "low": "[dim]LOW[/dim]",
                "info": "[dim]INFO[/dim]",
            }.get(finding.severity.value, finding.severity.value)
            
            findings_table.add_row(
                finding.id[:20],
                finding.type.value,
                severity_style,
                finding.title[:40],
                (finding.location or "-")[:30],
            )
        
        console.print(findings_table)
        
        if len(all_findings) > 50:
            console.print(f"[dim]... 还有 {len(all_findings) - 50} 个发现[/dim]")
    
    # 详细输出
    if verbose:
        console.print()
        for asset in result.assets:
            console.print(f"[bold]Asset: {asset.name}[/bold]")
            console.print(f"  Path: {asset.path}")
            console.print(f"  Skills: {len(asset.skills)}")
            console.print(f"  Plugins: {len(asset.plugins)}")
            console.print(f"  API Keys: {len(asset.api_keys)}")


def _save_json_report(result: ScanResult, output: Path):
    """保存 JSON 报告"""
    data = result.model_dump(mode='json')
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _collect_all_findings(result: ScanResult) -> list:
    """收集所有 findings"""
    all_findings = []
    for asset in result.assets:
        # Asset 级别的 findings
        all_findings.extend(asset.findings)
        
        # Skills 的 findings
        for skill in asset.skills:
            all_findings.extend(skill.findings)
        
        # API Keys 的 findings
        for key in asset.api_keys:
            all_findings.extend(key.findings)
    
    # 按严重等级排序
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    all_findings.sort(key=lambda f: severity_order.get(f.severity.value, 5))
    
    return all_findings


def _save_html_report(result: ScanResult, output: Path):
    """保存 HTML 报告"""
    # 收集所有 findings
    all_findings = _collect_all_findings(result)
    
    # 生成 findings 表格行
    findings_rows = ""
    for f in all_findings[:100]:  # 限制 100 条
        severity_class = f.severity.value
        severity_badge = {
            "critical": "🔴 CRITICAL",
            "high": "🟠 HIGH", 
            "medium": "🟡 MEDIUM",
            "low": "⚪ LOW",
            "info": "ℹ️ INFO",
        }.get(f.severity.value, f.severity.value.upper())
        
        # 转义 HTML
        title = f.title.replace("<", "&lt;").replace(">", "&gt;")
        location = (f.location or "-").replace("<", "&lt;").replace(">", "&gt;")
        evidence = (f.evidence or "-").replace("<", "&lt;").replace(">", "&gt;") if f.evidence else "-"
        description = f.description.replace("<", "&lt;").replace(">", "&gt;")
        recommendation = f.recommendation.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        
        findings_rows += f"""
        <tr class="finding-row {severity_class}">
            <td><span class="badge {severity_class}">{severity_badge}</span></td>
            <td><code>{f.type.value}</code></td>
            <td><strong>{title}</strong></td>
            <td>{description}</td>
            <td><code>{location}</code></td>
            <td><pre>{evidence}</pre></td>
            <td>{recommendation}</td>
        </tr>
        """
    
    # 生成 Skills 表格
    skills_rows = ""
    for asset in result.assets:
        for skill in asset.skills:
            risk_count = len(skill.findings)
            risk_badge = f'<span class="badge {"critical" if risk_count > 0 else "low"}">{risk_count} risks</span>' if risk_count > 0 else '<span class="badge info">0 risks</span>'
            skills_rows += f"""
            <tr>
                <td><strong>{skill.name}</strong></td>
                <td>{skill.source}</td>
                <td>{"✅" if skill.has_scripts else "❌"}</td>
                <td>{risk_badge}</td>
                <td>{asset.name}</td>
            </tr>
            """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Agent Security Scan Report - {result.scan_id}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
            margin: 0;
            padding: 0;
            background: #f8f9fa;
            color: #333;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header .scan-id {{ opacity: 0.8; font-size: 14px; }}
        
        /* Summary Cards */
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #666; }}
        .card .value {{ font-size: 32px; font-weight: bold; }}
        .card.critical .value {{ color: #dc3545; }}
        .card.high .value {{ color: #fd7e14; }}
        .card.medium .value {{ color: #ffc107; }}
        .card.low .value {{ color: #6c757d; }}
        
        /* Sections */
        .section {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .section h2 {{ margin: 0 0 20px 0; font-size: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        
        /* Tables */
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        
        /* Findings Table */
        .findings-table th {{ position: sticky; top: 0; background: #f8f9fa; z-index: 10; }}
        .findings-table pre {{
            margin: 0;
            padding: 4px 8px;
            background: #f5f5f5;
            border-radius: 4px;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-all;
            max-width: 300px;
        }}
        .findings-table td {{ vertical-align: top; }}
        .findings-table tr.critical {{ background: #fff5f5; }}
        .findings-table tr.high {{ background: #fff8f0; }}
        
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge.critical {{ background: #dc3545; color: white; }}
        .badge.high {{ background: #fd7e14; color: white; }}
        .badge.medium {{ background: #ffc107; color: #333; }}
        .badge.low {{ background: #6c757d; color: white; }}
        .badge.info {{ background: #17a2b8; color: white; }}
        
        /* Code */
        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        /* Footer */
        .footer {{ text-align: center; padding: 40px 20px; color: #999; }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .findings-table {{ font-size: 12px; }}
            .findings-table pre {{ max-width: 150px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🛡️ AI Agent Security Scan Report</h1>
            <div class="scan-id">Scan ID: {result.scan_id}</div>
        </div>
    </div>
    
    <div class="container">
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="card">
                <h3>🔍 Assets Found</h3>
                <div class="value">{len(result.assets)}</div>
            </div>
            <div class="card critical">
                <h3>🔴 Critical</h3>
                <div class="value">{result.findings_by_severity.get('critical', 0)}</div>
            </div>
            <div class="card high">
                <h3>🟠 High</h3>
                <div class="value">{result.findings_by_severity.get('high', 0)}</div>
            </div>
            <div class="card medium">
                <h3>🟡 Medium</h3>
                <div class="value">{result.findings_by_severity.get('medium', 0)}</div>
            </div>
            <div class="card low">
                <h3>⚪ Low</h3>
                <div class="value">{result.findings_by_severity.get('low', 0)}</div>
            </div>
        </div>
        
        <!-- Scan Info -->
        <div class="section">
            <h2>📋 Scan Information</h2>
            <table>
                <tr><th>Scan ID</th><td>{result.scan_id}</td></tr>
                <tr><th>Started At</th><td>{result.started_at}</td></tr>
                <tr><th>Completed At</th><td>{result.completed_at or 'N/A'}</td></tr>
                <tr><th>Duration</th><td>{result.duration_seconds:.2f} seconds</td></tr>
                <tr><th>Total Findings</th><td><strong>{result.total_findings}</strong></td></tr>
            </table>
        </div>
        
        <!-- Assets -->
        <div class="section">
            <h2>🖥️ Discovered Assets</h2>
            <table>
                <tr>
                    <th>Type</th>
                    <th>Name</th>
                    <th>Path</th>
                    <th>Version</th>
                    <th>Skills</th>
                    <th>API Keys</th>
                </tr>
                {''.join(f'<tr><td><span class="badge info">{a.type.value}</span></td><td><strong>{a.name}</strong></td><td><code>{a.path}</code></td><td>{a.version or "-"}</td><td>{len(a.skills)}</td><td>{len(a.api_keys)}</td></tr>' for a in result.assets)}
            </table>
        </div>
        
        <!-- Skills -->
        <div class="section">
            <h2>📦 Skills ({sum(len(a.skills) for a in result.assets)} total)</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Source</th>
                    <th>Has Scripts</th>
                    <th>Risks</th>
                    <th>Asset</th>
                </tr>
                {skills_rows}
            </table>
        </div>
        
        <!-- Findings -->
        <div class="section">
            <h2>⚠️ Security Findings ({len(all_findings)} total)</h2>
            <div style="overflow-x: auto;">
                <table class="findings-table">
                    <tr>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Title</th>
                        <th>Description</th>
                        <th>Location</th>
                        <th>Evidence</th>
                        <th>Recommendation</th>
                    </tr>
                    {findings_rows}
                </table>
            </div>
            {f'<p style="color: #999; margin-top: 10px;">Showing 100 of {len(all_findings)} findings.</p>' if len(all_findings) > 100 else ''}
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by <strong>AI Agent Security Scanner</strong> v0.1.0</p>
        <p>Scan completed at {result.completed_at or result.started_at}</p>
    </div>
</body>
</html>
"""
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)


@app.command()
def version():
    """显示版本信息"""
    from scanner import __version__
    console.print(f"AI Agent Security Scanner v{__version__}")


if __name__ == "__main__":
    app()
