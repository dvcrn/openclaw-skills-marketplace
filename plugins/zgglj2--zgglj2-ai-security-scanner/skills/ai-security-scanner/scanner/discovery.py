"""
资产发现模块
自动检测系统中的 AI Agent 安装
"""
import json
import re
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scanner.models import (
    AgentConfig,
    Asset,
    AssetType,
    Finding,
    FindingType,
    Plugin,
    Severity,
    Skill,
)

console = Console()


class AssetDiscovery:
    """AI Agent 资产发现"""
    
    # 已知的 Agent 安装路径
    OPENCLAW_PATHS = [
        Path.home() / ".openclaw",
        Path("/usr/local/bin/openclaw"),
        Path("/usr/bin/openclaw"),
    ]
    
    CURSOR_PATHS = [
        Path.home() / ".cursor",
        Path.home() / ".vscode" / "extensions",  # Cursor 基于 VSCode
    ]
    
    CLAUDE_CODE_PATHS = [
        Path.home() / ".claude",
        Path.home() / ".config" / "claude-code",
    ]
    
    def __init__(self, scan_memory: bool = True, scan_logs: bool = True):
        self.scan_memory = scan_memory
        self.scan_logs = scan_logs
        self.findings: list[Finding] = []
    
    def discover_all(self) -> list[Asset]:
        """发现所有 AI Agent 资产"""
        assets = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # 检测 OpenClaw
            task = progress.add_task("检测 OpenClaw...", total=None)
            if openclaw := self.discover_openclaw():
                assets.append(openclaw)
                console.print(f"[green]✓[/green] 发现 OpenClaw: {openclaw.path}")
            
            # 检测 Cursor
            progress.update(task, description="检测 Cursor...")
            if cursor := self.discover_cursor():
                assets.append(cursor)
                console.print(f"[green]✓[/green] 发现 Cursor: {cursor.path}")
            
            # 检测 Claude Code
            progress.update(task, description="检测 Claude Code...")
            if claude := self.discover_claude_code():
                assets.append(claude)
                console.print(f"[green]✓[/green] 发现 Claude Code: {claude.path}")
        
        return assets
    
    def discover_openclaw(self) -> Optional[Asset]:
        """检测 OpenClaw 安装"""
        openclaw_dir = None
        
        for path in self.OPENCLAW_PATHS:
            if path.exists():
                openclaw_dir = path if path.is_dir() else path.parent
                break
        
        if not openclaw_dir:
            # 尝试通过 which 查找
            try:
                result = subprocess.run(
                    ["which", "openclaw"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    openclaw_path = Path(result.stdout.strip())
                    openclaw_dir = Path.home() / ".openclaw"
            except Exception:
                pass
        
        if not openclaw_dir or not openclaw_dir.exists():
            return None
        
        # 解析配置
        config = self._parse_openclaw_config(openclaw_dir)
        
        # 采集 Skills
        skills = self._collect_openclaw_skills(openclaw_dir)
        
        # 采集 Plugins
        plugins = self._collect_openclaw_plugins(openclaw_dir)
        
        # 采集记忆文件
        memory_files = self._collect_memory_files(openclaw_dir / "workspace")
        
        # 采集日志文件
        log_files = self._collect_log_files(openclaw_dir)
        
        # 检查配置风险
        config_findings = self._check_config_risks(config)
        
        asset = Asset(
            type=AssetType.OPENCLAW,
            name="OpenClaw",
            path=openclaw_dir,
            version=config.version if config else None,
            config=config,
            skills=skills,
            plugins=plugins,
            memory_files=memory_files,
            log_files=log_files,
            findings=config_findings,
        )
        
        return asset
    
    def _parse_openclaw_config(self, openclaw_dir: Path) -> Optional[AgentConfig]:
        """解析 OpenClaw 配置"""
        config_file = openclaw_dir / "openclaw.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 移除 JSON 注释（简单处理）
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                data = json.loads(content)
            
            config = AgentConfig(
                version=self._get_openclaw_version(),
                model=data.get("agents", {}).get("defaults", {}).get("model", {}).get("primary"),
                workspace=Path(data.get("agents", {}).get("defaults", {}).get("workspace", "")),
                gateway_port=data.get("gateway", {}).get("port"),
                gateway_bind=data.get("gateway", {}).get("bind"),
                auth_mode=data.get("gateway", {}).get("auth", {}).get("mode"),
                enabled_channels=list(data.get("channels", {}).keys()),
            )
            
            return config
            
        except Exception as e:
            console.print(f"[yellow]警告: 解析配置失败: {e}[/yellow]")
            return None
    
    def _get_openclaw_version(self) -> Optional[str]:
        """获取 OpenClaw 版本"""
        try:
            result = subprocess.run(
                ["openclaw", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 解析版本号
                match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    def _collect_openclaw_skills(self, openclaw_dir: Path) -> list[Skill]:
        """采集 OpenClaw Skills"""
        skills = []
        
        # Skills 可能的位置
        skill_dirs = [
            openclaw_dir / "workspace" / "skills",
            openclaw_dir / "skills",
            Path.home() / ".openclaw" / "skills",
        ]
        
        # 内置 skills（从 node_modules）
        try:
            result = subprocess.run(
                ["npm", "root", "-g"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                npm_root = Path(result.stdout.strip())
                openclaw_node = npm_root / "openclaw"
                if openclaw_node.exists():
                    skill_dirs.append(openclaw_node / "skills")
        except Exception:
            pass
        
        for skill_dir in skill_dirs:
            if not skill_dir.exists():
                continue
            
            for skill_path in skill_dir.iterdir():
                if not skill_path.is_dir():
                    continue
                
                skill_file = skill_path / "SKILL.md"
                if not skill_file.exists():
                    continue
                
                # 解析 Skill 信息
                skill = self._parse_skill(skill_path, skill_file)
                if skill:
                    skills.append(skill)
        
        return skills
    
    def _parse_skill(self, skill_path: Path, skill_file: Path) -> Optional[Skill]:
        """解析 Skill 文件"""
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # 提取描述（第一段非空内容）
            lines = content.split('\n')
            description = ""
            for line in lines[1:]:  # 跳过标题
                line = line.strip()
                if line and not line.startswith('#'):
                    description = line[:200]
                    break
            
            # 检查是否有脚本文件
            script_files = []
            for ext in ['*.sh', '*.py', '*.js']:
                script_files.extend(skill_path.glob(ext))
            
            # 判断来源
            source = "custom"
            if "openclaw-bundled" in str(skill_path):
                source = "bundled"
            elif "openclaw-extra" in str(skill_path):
                source = "extra"
            
            return Skill(
                name=skill_path.name,
                path=skill_path,
                source=source,
                description=description,
                has_scripts=len(script_files) > 0,
                script_files=[str(s) for s in script_files],
            )
            
        except Exception as e:
            console.print(f"[yellow]警告: 解析 Skill 失败 {skill_path}: {e}[/yellow]")
            return None
    
    def _collect_openclaw_plugins(self, openclaw_dir: Path) -> list[Plugin]:
        """采集 OpenClaw Plugins"""
        plugins = []
        
        config_file = openclaw_dir / "openclaw.json"
        if not config_file.exists():
            return plugins
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                data = json.loads(content)
            
            plugin_config = data.get("plugins", {})
            entries = plugin_config.get("entries", {})
            
            for name, info in entries.items():
                if isinstance(info, dict):
                    enabled = info.get("enabled", False)
                else:
                    enabled = bool(info)
                
                plugins.append(Plugin(
                    name=name,
                    path=openclaw_dir / "plugins" / name,
                    enabled=enabled,
                ))
        
        except Exception as e:
            console.print(f"[yellow]警告: 解析 Plugins 失败: {e}[/yellow]")
        
        return plugins
    
    def _collect_memory_files(self, workspace: Path) -> list[Path]:
        """采集记忆文件"""
        memory_files = []
        
        if not workspace.exists():
            return memory_files
        
        # MEMORY.md
        memory_md = workspace / "MEMORY.md"
        if memory_md.exists():
            memory_files.append(memory_md)
        
        # memory/ 目录
        memory_dir = workspace / "memory"
        if memory_dir.exists():
            memory_files.extend(memory_dir.glob("*.md"))
        
        return memory_files
    
    def _collect_log_files(self, openclaw_dir: Path) -> list[Path]:
        """采集日志文件"""
        log_files = []
        
        # 常见日志位置
        log_paths = [
            openclaw_dir / "logs",
            Path("/var/log/openclaw"),
            Path.home() / ".openclaw" / "logs",
        ]
        
        for log_dir in log_paths:
            if log_dir.exists():
                log_files.extend(log_dir.glob("*.log"))
                log_files.extend(log_dir.glob("*.jsonl"))
        
        return log_files[:100]  # 限制数量
    
    def _check_config_risks(self, config: Optional[AgentConfig]) -> list[Finding]:
        """检查配置风险"""
        findings = []
        
        if not config:
            return findings
        
        # 检查网络暴露
        if config.gateway_bind and config.gateway_bind not in ["127.0.0.1", "localhost", "loopback"]:
            findings.append(Finding(
                id=f"config-bind-{config.gateway_bind}",
                type=FindingType.CONFIG_NETWORK_EXPOSED,
                severity=Severity.HIGH,
                title="Gateway 绑定非本地地址",
                description=f"OpenClaw Gateway 绑定在 {config.gateway_bind}，可能暴露到网络",
                evidence=f"bind: {config.gateway_bind}",
                recommendation="将 gateway.bind 设置为 'loopback' 或 '127.0.0.1'",
            ))
        
        # 检查认证模式
        if config.auth_mode == "none" or not config.auth_mode:
            findings.append(Finding(
                id="config-auth-none",
                type=FindingType.CONFIG_WEAK_AUTH,
                severity=Severity.HIGH,
                title="Gateway 未启用认证",
                description="OpenClaw Gateway 未配置认证，任何人都可以访问",
                recommendation="在 gateway.auth.mode 中设置 'token' 认证",
            ))
        
        # 检查端口
        if config.gateway_port and config.gateway_port < 1024:
            findings.append(Finding(
                id=f"config-port-{config.gateway_port}",
                type=FindingType.CONFIG_INSECURE,
                severity=Severity.LOW,
                title="使用特权端口",
                description=f"Gateway 使用特权端口 {config.gateway_port}",
                recommendation="使用非特权端口（>1024）",
            ))
        
        return findings
    
    def discover_cursor(self) -> Optional[Asset]:
        """检测 Cursor IDE"""
        cursor_dir = None
        
        for path in self.CURSOR_PATHS:
            if path.exists():
                cursor_dir = path
                break
        
        if not cursor_dir:
            return None
        
        # TODO: 实现 Cursor 详细检测
        return Asset(
            type=AssetType.CURSOR,
            name="Cursor",
            path=cursor_dir,
        )
    
    def discover_claude_code(self) -> Optional[Asset]:
        """检测 Claude Code"""
        claude_dir = None
        
        for path in self.CLAUDE_CODE_PATHS:
            if path.exists():
                claude_dir = path
                break
        
        if not claude_dir:
            return None
        
        # TODO: 实现 Claude Code 详细检测
        return Asset(
            type=AssetType.CLAUDE_CODE,
            name="Claude Code",
            path=claude_dir,
        )
