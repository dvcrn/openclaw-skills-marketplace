"""
改进版内容扫描模块 - 减少误报
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


class ImprovedContentScanner:
    """改进版内容扫描器 - 减少误报"""
    
    # 官方 Skill 白名单（来自 openclaw-bundled 和 openclaw-extra)
    OFFICIAL_SKILLS = {
        # 内置 Skills
        "weather", "healthcheck", "skill-creator", "session-logs",
        "github", "discord", "slack", "notion", "trello", "obsidian",
        "bear-notes", "apple-notes", "apple-reminders", "things-mac",
        "openai-whisper", "openai-whisper-api", "openai-image-gen",
        "gemini", "sag", "sherpa-onnx-tts", "summarize",
        "himalaya", "gog", "mcporter", "peekaboo", "tmux",
        "video-frames", "gifgrep", "songsee", "spotify-player",
        "sonoscli", "openhue", "eightctl", "blucli", "camsnap",
        "voice-call", "bluebubbles", "imsg", "wacli",
        "xurl", "gh-issues", "oracle", "nano-pdf", "nano-banana-pro",
        "coding-agent", "blogwatcher", "clawhub", "1password",
        "goplaces", "ordercli", "canvas",
        # 扩展 Skills
        "feishu-doc", "feishu-drive", "feishu-wiki", "feishu-perm",
    }
    
    # 高可信 API 域名白名单
    TRUSTED_API_DOMAINS = {
        # 官方 API
        "api.github.com",
        "api.openai.com", 
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "openrouter.ai",
        "api.moonshot.cn",
        "api.deepseek.com",
        "api.trello.com",
        "api.notion.com",
        "api.twitter.com",
        "api.x.com",
        "discord.com",
        "slack.com",
        "api.slack.com",
        # 本地服务
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
    }
    
    # 改进后的检测规则 - 更精确，减少误报
    MALICIOUS_PATTERNS = {
        # ==================== 高危：真正需要关注 ====================
        
        "reverse_shell": {
            "patterns": [
                r"nc\s+-[elp]\s+\d+\.\d+\.\d+\.\d+",  # nc -e IP
                r"bash\s+-i\s*>\s*&\s*\d",            # bash -i >&
                r"/dev/tcp/\d+\.\d+\.\d+\.\d+/\d+",   # /dev/tcp/IP/PORT
                r"python.*socket\.connect.*\d+\.\d+\.\d+\.\d+",  # python socket
            ],
            "severity": Severity.CRITICAL,
            "description": "检测到反向 Shell 特征",
            "check_context": False,  # 任何上下文都要检测
        },
        
        "malicious_download_exec": {
            "patterns": [
                r"curl\s+.*\|\s*base64",  # base64 编码后执行
                r"wget\s+.*\|\s*bash",  # wget 后执行
                r"eval\s*\(",  # eval 执行
                r"exec\s*\(",  # exec 执行
            ],
            "severity": Severity.CRITICAL,
            "description": "检测到可疑的动态执行代码",
            "check_context": False,
        },
        
        # ==================== 中危：需要确认 ====================
        
        "suspicious_network": {
            "patterns": [
                r"curl\s+.*(?:http|https)://(?!.*(?:github|openai|anthropic|googleapis|trello|notion|twitter|x\.com|discord|slack|localhost|127\.0.0.1).*)(?!.*format=json)",  # curl 到非白名单域名
            ],
            "severity": Severity.HIGH,
            "description": "尝试向非白名单域名发送请求",
            "check_context": True,  # 需要上下文检测
        },
        
        "private_key_exfil": {
            "patterns": [
                r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
                r"cat\s+.*id_rsa",
                r"cat\s+.*\.pem",
            ],
            "severity": Severity.HIGH,
            "description": "尝试读取私钥文件",
            "check_context": False,
        },
        
        # ==================== 低危：仅提示 ====================
        
        "env_file_read": {
            "patterns": [
                r"cat\s+.*\.env\b",  # 读取 .env 文件内容
                r"source\s+.*\.env\b",  # source .env
            ],
            "severity": Severity.LOW,
            "description": "尝试读取 .env 文件",
            "check_context": True,
        },
        
        "external_api_call": {
            "patterns": [
                r"curl\s+.*(?:http|https)://",  # curl 调用
                r"fetch\s*\(",  # fetch API
                r"requests\.(?:get|post)\s*\(",  # requests 库
                r"httpx\.(?:get|post)\s*\(",  # httpx 库
            ],
            "severity": Severity.INFO,
            "description": "包含外部 API 调用",
            "check_context": True,
            "skip_if_official": True,  # 官方 Skill 跳过
        },
        
        "config_reference": {
            "patterns": [
                r"\.env",  # 引用 .env
                r"credentials",  # credentials 关键词
                r"(?:api_key|apikey|api-key)",  # api_key 关键词
                r"(?:token|secret)\s*[=:]",  # token/secret 关键词
            ],
            "severity": Severity.INFO,
            "description": "包含配置相关关键词",
            "check_context": True,
            "skip_if_official": True,  # 官方 Skill 跳过
        },
    }
    
    def __init__(
        self,
        enable_llm: bool = False,
        llm_provider: str = "openai",
        skip_official: bool = True,  # 默认跳过官方 Skill
    ):
        self.enable_llm = enable_llm
        self.llm_provider = llm_provider
        self.skip_official = skip_official
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
                    # 跳过官方 Skill
                    if self.skip_official and skill.name in self.OFFICIAL_SKILLS:
                        console.print(f"[dim]跳过官方 Skill: {skill.name}[/dim]")
                        continue
                    
                    findings = self.scan_skill(skill)
                    skill.findings.extend(findings)
                    all_findings.extend(findings)
                
                # 扫描记忆文件
                for memory_file in asset.memory_files:
                    findings = self.scan_memory_file(memory_file)
                    all_findings.extend(findings)
                
                # 扫描日志文件
                for log_file in asset.log_files[:10]:
                    findings = self.scan_log_file(log_file)
                    all_findings.extend(findings)
        
        return all_findings
    
    def scan_skill(self, skill: Skill) -> list[Finding]:
        """扫描单个 Skill"""
        findings = []
        
        skill_file = skill.path / "SKILL.md"
        if not skill_file.exists():
            return findings
        
        content = skill_file.read_text(encoding='utf-8', errors='ignore')
        
        # 解析上下文
        context_blocks = self._parse_content_with_context(content)
        
        # 检查恶意模式
        for rule_name, rule_config in self.MALICIOUS_PATTERNS.items():
            # 跳过官方 Skill 的某些规则
            if rule_config.get("skip_if_official") and skill.name in self.OFFICIAL_SKILLS:
                continue
            
            for pattern in rule_config["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    # 检查上下文
                    if rule_config.get("check_context"):
                        line_num = content[:match.start()].count('\n') + 1
                        # 检查是否在代码块中
                        in_code_block = self._is_in_code_block(context_blocks, line_num)
                        if in_code_block:
                            # 在代码块中，降低严重等级
                            severity = Severity.INFO
                        else:
                            severity = rule_config["severity"]
                    else:
                        severity = rule_config["severity"]
                        line_num = content[:match.start()].count('\n') + 1
                    
                    finding = Finding(
                        id=f"content-{rule_name}-{skill.name}-{line_num}",
                        type=self._get_finding_type(rule_name),
                        severity=severity,
                        title=f"Skill '{skill.name}': {rule_config['description']}",
                        description=f"发现可疑模式: {rule_name}",
                        location=str(skill_file),
                        line_number=line_num,
                        evidence=match.group()[:100] if match.group() else match.group(),
                        recommendation=self._get_recommendation(rule_name, match.group()),
                        metadata={
                            "rule": rule_name,
                            "pattern": pattern,
                            "is_official": skill.name in self.OFFICIAL_SKILLS,
                        }
                    )
                    findings.append(finding)
        
        # LLM 分析（如果启用）
        if self.enable_llm and self.llm_analyzer:
            llm_findings = self.llm_analyzer.analyze_skill(skill.name, content)
            findings.extend(llm_findings)
        
        return findings
    
    def _parse_content_with_context(self, content: str) -> list:
        """解析内容
        提取上下文信息（是否在代码块中）
        """
        lines = content.split('\n')
        in_code_block = False
        context_blocks = []
        
        for i, line in enumerate(lines):
            if '```' in line:
                if in_code_block:
                    in_code_block = False
                else:
                    in_code_block = True
            context_blocks.append({
                'line_num': i + 1,
                'content': line,
                'in_code_block': in_code_block
            })
        
        return context_blocks
    
    def _is_in_code_block(self, context_blocks: list, line_num: int) -> bool:
        """检查指定行是否在代码块中"""
        for block in context_blocks:
            if block['line_num'] == line_num:
                return block['in_code_block']
        return False
    
    def scan_memory_file(self, memory_file: Path) -> list[Finding]:
        """扫描记忆文件"""
        findings = []
        
        if not memory_file.exists():
            return findings
        
        try:
            content = memory_file.read_text(encoding='utf-8', errors='ignore')
            
            # 检测敏感信息（降低敏感度）
            sensitive_patterns = {
                "private_key": (r"-----BEGIN.*PRIVATE KEY-----", Severity.HIGH),
                "api_key": (r"sk-[a-zA-Z0-9]{20,}", Severity.MEDIUM),
                "password": (r"password\s*[=:].{8,}", Severity.MEDIUM),
            }
            
            for info_type, (pattern, severity) in sensitive_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append(Finding(
                        id=f"memory-sensitive-{info_type}-{memory_file.name}",
                        type=FindingType.SENSITIVE_DATA,
                        severity=severity,
                        title=f"记忆文件包含敏感信息: {info_type}",
                        description=f"在 {memory_file.name} 中发现 {info_type}",
                        location=str(memory_file),
                        recommendation="检查是否需要保留该信息，考虑脱敏或加密",
                        metadata={"info_type": info_type},
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
            content = self._read_last_lines(log_file, 1000)
            
            # 日志中只检测真正的敏感信息
            if re.search(r"sk-[a-zA-Z0-9]{20,}", content):
                findings.append(Finding(
                    id=f"log-apikey-{log_file.name}",
                    type=FindingType.SENSITIVE_DATA,
                    severity=Severity.HIGH,
                    title="日志文件包含 API Key",
                    description=f"在 {log_file.name} 中发现 API Key",
                    location=str(log_file),
                    recommendation="配置日志脱敏规则",
                ))
        
        except Exception as e:
            console.print(f"[yellow]警告: 扫描日志文件失败 {log_file}: {e}[/yellow]")
        
        return findings
    
    def _read_last_lines(self, file_path: Path, n: int) -> str:
        """读取文件最后 n 行"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                return ''.join(lines[-n:])
        except Exception:
            return ""
    
    def _get_finding_type(self, rule_name: str) -> FindingType:
        """获取发现类型"""
        mapping = {
            "reverse_shell": FindingType.SKILL_MALICIOUS_CODE,
            "malicious_download_exec": FindingType.SKILL_MALICIOUS_CODE,
            "suspicious_network": FindingType.SKILL_DATA_EXFIL,
            "private_key_exfil": FindingType.CREDENTIAL_LEAK,
            "env_file_read": FindingType.SENSITIVE_DATA,
            "external_api_call": FindingType.SKILL_DATA_EXFIL,
            "config_reference": FindingType.SENSITIVE_DATA,
        }
        return mapping.get(rule_name, FindingType.SKILL_MALICIOUS)
    
    def _get_recommendation(self, rule_name: str, match: Optional[re.Match]) -> str:
        """获取修复建议"""
        recommendations = {
            "reverse_shell": "立即删除该 Skill，这是明确的恶意行为",
            "malicious_download_exec": "检查动态执行的目的和来源",
            "suspicious_network": "检查请求目标是否可信",
            "private_key_exfil": "检查私钥文件的访问权限",
            "env_file_read": "检查 .env 文件的权限和内容",
            "external_api_call": "确认 API 调用目标是否为官方端点",
            "config_reference": "检查配置示例是否包含真实凭证",
        }
        return recommendations.get(rule_name, "检查并修复该风险")
