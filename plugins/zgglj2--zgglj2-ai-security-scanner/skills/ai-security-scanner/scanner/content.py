"""
内容扫描模块
扫描 Skill、Prompt、文档中的安全风险
"""
import re
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scanner.models import (
    Asset,
    Finding,
    FindingType,
    Severity,
    Skill,
)

console = Console()


class ContentScanner:
    """Skill/Prompt/文档 风险扫描"""
    
    # 恶意特征正则
    MALICIOUS_PATTERNS = {
        # 数据外传
        "data_exfil": {
            "patterns": [
                r"curl\s+.*(?:http|https)://",
                r"wget\s+.*(?:http|https)://",
                r"fetch\s+.*(?:http|https)://",
                r"requests\.(?:get|post)\s*\(",
                r"httpx\.(?:get|post)\s*\(",
                r"\.fetch\s*\(",
            ],
            "severity": Severity.HIGH,
            "description": "尝试向外部发送请求",
        },
        
        # 凭证窃取
        "credential_theft": {
            "patterns": [
                r"\.env",
                r"credentials",
                r"(?:password|passwd|pwd)\s*[=:]",
                r"(?:api_key|apikey|api-key)\s*[=:]",
                r"(?:token|secret)\s*[=:]",
                r"cat\s+.*(?:id_rsa|\.pem|\.key)",
                r"cat\s+.*\.env",
            ],
            "severity": Severity.CRITICAL,
            "description": "尝试读取凭证文件",
        },
        
        # 权限提升
        "privilege_escalation": {
            "patterns": [
                r"sudo\s+",
                r"chmod\s+(?:777|a\+rwx)",
                r"chown\s+root",
                r"setuid",
                r"setgid",
            ],
            "severity": Severity.HIGH,
            "description": "尝试提升权限",
        },
        
        # 反向 Shell
        "reverse_shell": {
            "patterns": [
                r"nc\s+-[elp]",
                r"bash\s+-i",
                r"/dev/tcp/",
                r"socket\.connect",
                r"subprocess.*sh\s+-c",
            ],
            "severity": Severity.CRITICAL,
            "description": "尝试建立反向 Shell",
        },
        
        # 数据编码（混淆）
        "obfuscation": {
            "patterns": [
                r"base64(?:\.b64encode|\.encode|\.decode)",
                r"hex\(",
                r"eval\s*\(",
                r"exec\s*\(",
                r"compile\s*\(",
            ],
            "severity": Severity.MEDIUM,
            "description": "使用编码或动态执行混淆",
        },
        
        # 文件操作
        "file_manipulation": {
            "patterns": [
                r"rm\s+-rf\s+/",
                r"rm\s+-rf\s+~",
                r"dd\s+if=",
                r">\s*/dev/sd",
                r"mkfs\.",
            ],
            "severity": Severity.CRITICAL,
            "description": "危险文件操作",
        },
        
        # 网络扫描
        "network_scan": {
            "patterns": [
                r"nmap\s+",
                r"masscan\s+",
                r"zmap\s+",
                r"nc\s+-z",
            ],
            "severity": Severity.MEDIUM,
            "description": "尝试进行网络扫描",
        },
    }
    
    # 已知恶意 Skill 名称（碰瓷）
    TYPOSQUATTING_PATTERNS = [
        r"clawhubb",
        r"cllawhub",
        r"clawhub1",
        r"clawhub-",
        r"clwahub",
    ]
    
    # 敏感信息正则
    SENSITIVE_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone_cn": r"1[3-9]\d{9}",
        "id_card_cn": r"\d{17}[\dXx]",
        "credit_card": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
        "ip_address": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
    }
    
    def __init__(
        self,
        enable_llm: bool = False,
        llm_provider: str = "openai",
    ):
        self.enable_llm = enable_llm
        self.llm_provider = llm_provider
        self.llm_analyzer = None
        
        if enable_llm:
            self._init_llm()
    
    def _init_llm(self):
        """初始化 LLM 分析器"""
        try:
            from scanner.llm import LLMAnalyzer
            self.llm_analyzer = LLMAnalyzer(provider=self.llm_provider)
        except ImportError:
            console.print("[yellow]警告: LLM 模块未安装，跳过 LLM 分析[/yellow]")
            self.enable_llm = False
    
    def scan(self, assets: list[Asset]) -> list[Finding]:
        """扫描所有资产"""
        all_findings = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for asset in assets:
                task = progress.add_task(
                    f"扫描 {asset.name} 的内容...",
                    total=None
                )
                
                # 扫描 Skills
                for skill in asset.skills:
                    findings = self.scan_skill(skill)
                    skill.findings.extend(findings)
                    all_findings.extend(findings)
                
                # 扫描记忆文件
                for memory_file in asset.memory_files:
                    findings = self.scan_memory_file(memory_file)
                    all_findings.extend(findings)
                
                # 扫描日志文件
                for log_file in asset.log_files[:10]:  # 限制数量
                    findings = self.scan_log_file(log_file)
                    all_findings.extend(findings)
        
        return all_findings
    
    def scan_skill(self, skill: Skill) -> list[Finding]:
        """扫描单个 Skill"""
        findings = []
        
        # 1. 检查碰瓷名称
        for pattern in self.TYPOSQUATTING_PATTERNS:
            if re.search(pattern, skill.name, re.IGNORECASE):
                findings.append(Finding(
                    id=f"skill-typosquat-{skill.name}",
                    type=FindingType.SKILL_TYPOSQUATTING,
                    severity=Severity.HIGH,
                    title=f"Skill 名称疑似碰瓷",
                    description=f"Skill '{skill.name}' 名称疑似仿冒官方 Skill",
                    location=str(skill.path),
                    recommendation="删除该 Skill，从官方渠道重新安装",
                    metadata={"skill_name": skill.name},
                ))
        
        # 2. 扫描 SKILL.md
        skill_file = skill.path / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            file_findings = self._scan_content(
                content=content,
                location=str(skill_file),
                context=f"Skill '{skill.name}'",
            )
            findings.extend(file_findings)
        
        # 3. 扫描脚本文件
        for script_file in skill.script_files:
            script_path = Path(script_file)
            if script_path.exists():
                content = script_path.read_text(encoding='utf-8', errors='ignore')
                file_findings = self._scan_content(
                    content=content,
                    location=str(script_path),
                    context=f"Skill '{skill.name}' 脚本",
                )
                findings.extend(file_findings)
        
        # 4. LLM 分析（如果启用）
        if self.enable_llm and self.llm_analyzer and skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            llm_findings = self.llm_analyzer.analyze_skill(skill.name, content)
            findings.extend(llm_findings)
        
        return findings
    
    def scan_memory_file(self, memory_file: Path) -> list[Finding]:
        """扫描记忆文件"""
        findings = []
        
        if not memory_file.exists():
            return findings
        
        try:
            content = memory_file.read_text(encoding='utf-8', errors='ignore')
            
            # 检测敏感信息
            for info_type, pattern in self.SENSITIVE_PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    findings.append(Finding(
                        id=f"memory-sensitive-{info_type}",
                        type=FindingType.SENSITIVE_DATA,
                        severity=Severity.HIGH,
                        title=f"记忆文件包含敏感信息: {info_type}",
                        description=f"在 {memory_file.name} 中发现 {len(matches)} 个 {info_type}",
                        location=str(memory_file),
                        evidence=f"示例: {matches[0] if matches else 'N/A'}",
                        recommendation=(
                            f"1. 检查是否需要保留该信息\n"
                            f"2. 考虑使用脱敏或加密\n"
                            f"3. 定期清理记忆文件"
                        ),
                        metadata={"info_type": info_type, "count": len(matches)},
                    ))
        
        except Exception as e:
            console.print(f"[yellow]警告: 扫描记忆文件失败 {memory_file}: {e}[/yellow]")
        
        return findings
    
    def scan_log_file(self, log_file: Path) -> list[Finding]:
        """扫描日志文件"""
        findings = []
        
        if not log_file.exists():
            return findings
        
        try:
            # 只读取最后 1000 行
            content = self._read_last_lines(log_file, 1000)
            
            # 检测敏感信息
            for info_type, pattern in self.SENSITIVE_PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    findings.append(Finding(
                        id=f"log-sensitive-{info_type}-{log_file.name}",
                        type=FindingType.SENSITIVE_DATA,
                        severity=Severity.MEDIUM,
                        title=f"日志文件包含敏感信息: {info_type}",
                        description=f"在 {log_file.name} 中发现 {len(matches)} 个 {info_type}",
                        location=str(log_file),
                        recommendation="配置日志脱敏规则，避免记录敏感信息",
                        metadata={"info_type": info_type, "count": len(matches)},
                    ))
        
        except Exception as e:
            console.print(f"[yellow]警告: 扫描日志文件失败 {log_file}: {e}[/yellow]")
        
        return findings
    
    def _scan_content(
        self,
        content: str,
        location: str,
        context: str = "",
    ) -> list[Finding]:
        """扫描内容"""
        findings = []
        
        for risk_type, config in self.MALICIOUS_PATTERNS.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    # 查找行号
                    lines = content.split('\n')
                    line_numbers = []
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            line_numbers.append(i)
                    
                    finding_type = self._get_finding_type(risk_type)
                    
                    findings.append(Finding(
                        id=f"content-{risk_type}-{location}",
                        type=finding_type,
                        severity=config["severity"],
                        title=f"{context}: {config['description']}" if context else config["description"],
                        description=f"发现可疑模式: {risk_type}",
                        location=location,
                        line_number=line_numbers[0] if line_numbers else None,
                        evidence=matches[0] if matches else None,
                        recommendation=self._get_recommendation(risk_type),
                        metadata={
                            "risk_type": risk_type,
                            "pattern": pattern,
                            "line_numbers": line_numbers[:5],  # 最多5个
                        },
                    ))
        
        return findings
    
    def _get_finding_type(self, risk_type: str) -> FindingType:
        """获取发现类型"""
        mapping = {
            "data_exfil": FindingType.SKILL_DATA_EXFIL,
            "credential_theft": FindingType.CREDENTIAL_LEAK,
            "privilege_escalation": FindingType.SKILL_PRIVILEGE_ESC,
            "reverse_shell": FindingType.SKILL_MALICIOUS_CODE,
            "obfuscation": FindingType.SKILL_MALICIOUS_CODE,
            "file_manipulation": FindingType.SKILL_MALICIOUS_CODE,
            "network_scan": FindingType.SKILL_MALICIOUS,
        }
        return mapping.get(risk_type, FindingType.SKILL_MALICIOUS)
    
    def _get_recommendation(self, risk_type: str) -> str:
        """获取修复建议"""
        recommendations = {
            "data_exfil": "检查外部请求目标是否可信，考虑添加白名单限制",
            "credential_theft": "移除凭证读取逻辑，使用安全的凭证管理方式",
            "privilege_escalation": "评估是否真的需要提升权限，使用最小权限原则",
            "reverse_shell": "立即删除该 Skill，这是明确的恶意行为",
            "obfuscation": "检查编码/混淆的目的，移除不必要的动态执行",
            "file_manipulation": "评估文件操作的安全性，添加确认机制",
            "network_scan": "评估是否需要网络扫描功能，添加范围限制",
        }
        return recommendations.get(risk_type, "检查并修复该风险")
    
    def _read_last_lines(self, file_path: Path, n: int) -> str:
        """读取文件最后 n 行"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                return ''.join(lines[-n:])
        except Exception:
            return ""
