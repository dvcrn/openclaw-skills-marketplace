"""
CLI 工具 - 改进版
命令行接口
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

from scanner.discovery import AssetDiscovery
from scanner.apikey import APIKeyScanner
from scanner.content_v2 import ImprovedContentScanner
from scanner.report import generate_feishu_report
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
    output_feishu: bool = typer.Option(
        False,
        "--feishu",
        help="生成飞书文档报告",
    ),
    feishu_title: Optional[str] = typer.Option(
        None,
        "--feishu-title",
        help="飞书文档标题",
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
    skip_official: bool = typer.Option(
        True,
        "--skip-official",
        help="跳过官方 Skill 扫描（减少误报)",
    ),
):
    """
    执行完整安全扫描
    
    示例:
        aascan scan
        aascan scan -o report.json
        aascan scan --llm --llm-provider zhipu
        aascan scan --no-skip-official  # 扫描所有 Skill
    """
    
    # 创建扫描结果
    scan_result = ScanResult(
        scan_id=str(uuid.uuid4())[:8],
        started_at=datetime.now(),
    )
    
    console.print(Panel.fit(
        "[bold blue]🛡️ AI Agent Security Scanner (改进版)[/bold blue]\n"
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
        task = progress.add_task("[cyan]Phase 3/3: 内容风险扫描(改进版)...", total=100)
        content_scanner = ImprovedContentScanner(
            enable_llm=enable_llm,
            llm_provider=llm_provider,
            skip_official=skip_official,  # 使用参数
        )
        content_findings = content_scanner.scan(assets)
        for finding in content_findings:
            scan_result.add_finding(finding)
        progress.update(task, completed=100)
        
        if content_findings:
            console.print(f"[yellow]⚠[/yellow] 发现 {len(content_findings)} 个内容风险(已过滤误报)")
    
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
    
    # 飞书文档报告
    if output_feishu:
        _save_feishu_report(scan_result, feishu_title)
    
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
    scanner = ImprovedContentScanner(enable_llm=llm, skip_official=False)
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


def _save_html_report(result: ScanResult, output: Path):
    """保存 HTML 报告"""
    # 简化版 HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI Agent Security Scan Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .critical {{ color: #dc3545; }}
        .high {{ color: #fd7e14; }}
        .medium {{ color: #ffc107; }}
        .low {{ color: #6c757d; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        tr:hover {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>🛡️ AI Agent Security Scan Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Scan ID:</strong> {result.scan_id}</p>
        <p><strong>Started:</strong> {result.started_at}</p>
        <p><strong>Duration:</strong> {result.duration_seconds:.2f}s</p>
        <p><strong>Assets Found:</strong> {len(result.assets)}</p>
        <p><strong>Total Findings:</strong> {result.total_findings}</p>
        <p>
            <span class="critical">Critical: {result.findings_by_severity.get('critical', 0)}</span> |
            <span class="high">High: {result.findings_by_severity.get('high', 0)}</span> |
            <span class="medium">Medium: {result.findings_by_severity.get('medium', 0)}</span> |
            <span class="low">Low: {result.findings_by_severity.get('low', 0)}</span>
        </p>
    </div>
    
    <h2>Assets</h2>
    <table>
        <tr>
            <th>Type</th>
            <th>Name</th>
            <th>Path</th>
            <th>Skills</th>
            <th>Findings</th>
        </tr>
        {''.join(f'<tr><td>{a.type.value}</td><td>{a.name}</td><td>{a.path}</td><td>{len(a.skills)}</td><td>{len(a.findings)}</td></tr>' for a in result.assets)}
    </table>
    
    <h2>Findings</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Type</th>
            <th>Title</th>
            <th>Location</th>
            <th>Recommendation</th>
        </tr>
        {''.join(f'<tr><td class="{f.severity.value}">{f.severity.value.upper()}</td><td>{f.type.value}</td><td>{f.title}</td><td>{f.location or "-"}</td><td>{f.recommendation[:100]}...</td></tr>' for a in result.assets for f in a.findings[:50])}
    </table>
    
    <footer style="margin-top: 40px; color: #999; text-align: center;">
        Generated by AI Agent Security Scanner
    </footer>
</body>
</html>
"""
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)


def _save_feishu_report(result: ScanResult, title: Optional[str] = None):
    """保存飞书文档报告"""
    from scanner.report import generate_feishu_report
    
    # 转换为字典
    scan_dict = result.model_dump(mode='json')
    
    # 生成 Markdown
    md_content = generate_feishu_report(scan_dict, title)
    
    # 保存本地文件
    output_path = Path(f"scan-report-{result.scan_id}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    console.print(f"[green]✓[/green] Markdown 报告已保存: {output_path}")
    
    # 创建飞书文档
    try:
        import subprocess
        
        # 使用 feishu_doc 工具创建文档
        doc_title = title or f"AI Agent 安全扫描报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 调用 feishu_doc 创建文档
        cmd = ["feishu_doc", "create", "--title", doc_title]
        result_create = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result_create.returncode == 0:
            # 解析文档 token
            import json
            try:
                doc_info = json.loads(result_create.stdout)
                doc_token = doc_info.get('document_id')
                
                if doc_token:
                    # 写入内容
                    cmd_write = ["feishu_doc", "write", "--doc-token", doc_token, "--content", md_content]
                    subprocess.run(cmd_write, capture_output=True, text=True, timeout=60)
                    
                    # 添加权限
                    _add_feishu_permission(doc_token)
                    
                    doc_url = f"https://feishu.cn/docx/{doc_token}"
                    console.print(f"[green]✓[/green] 飞书文档已创建: {doc_url}")
                    return
            except:
                pass
        
        console.print(f"[yellow]⚠[/yellow] 飞书文档创建失败，请手动上传 Markdown 文件")
        
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] 飞书文档创建失败: {e}")
        console.print(f"[dim]提示: 请手动将 {output_path} 上传到飞书[/dim]")


def _add_feishu_permission(doc_token: str):
    """添加飞书文档权限（需要配置环境变量）"""
    import os

    # 从环境变量获取凭证
    feishu_app_id = os.environ.get("FEISHU_APP_ID")
    feishu_app_secret = os.environ.get("FEISHU_APP_SECRET")
    feishu_user_openid = os.environ.get("FEISHU_USER_OPENID")

    if not all([feishu_app_id, feishu_app_secret, feishu_user_openid]):
        console.print("[dim]提示: 未配置飞书凭证环境变量，跳过权限设置[/dim]")
        console.print("[dim]设置 FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_USER_OPENID 以启用自动权限[/dim]")
        return

    try:
        import subprocess

        # 获取 token
        token_cmd = f'''curl -s "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
            -H "Content-Type: application/json" \
            -d '{{"app_id":"{feishu_app_id}","app_secret":"{feishu_app_secret}"}}' \
            | jq -r '.tenant_access_token'
'''

        result = subprocess.run(
            token_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            token = result.stdout.strip()

            # 添加权限
            perm_cmd = f'''curl -s "https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/members?token={doc_token}&type=docx" \
                -X POST -H "Authorization: Bearer {token}" \
                -H "Content-Type: application/json" \
                -d '{{"member_type":"openid","member_id":"{feishu_user_openid}","perm":"full_access"}}'
'''

            subprocess.run(
                perm_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
    except Exception:
        pass


@app.command()
def version():
    """显示版本信息"""
    from scanner import __version__
    console.print(f"AI Agent Security Scanner v{__version__}")


if __name__ == "__main__":
    app()
