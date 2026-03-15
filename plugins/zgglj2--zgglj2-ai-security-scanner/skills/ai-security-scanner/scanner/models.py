"""
数据模型定义
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """风险等级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(str, Enum):
    """发现类型"""
    # API Key 相关
    API_KEY_EXPOSED = "api_key_exposed"
    API_KEY_VALID = "api_key_valid"
    API_KEY_PERMISSION = "api_key_permission"
    
    # Skill 风险
    SKILL_MALICIOUS = "skill_malicious"
    SKILL_DATA_EXFIL = "skill_data_exfiltration"
    SKILL_PRIVILEGE_ESC = "skill_privilege_escalation"
    SKILL_PROMPT_INJECTION = "skill_prompt_injection"
    SKILL_MALICIOUS_CODE = "skill_malicious_code"
    SKILL_TYPOSQUATTING = "skill_typosquatting"
    
    # 敏感信息
    SENSITIVE_DATA = "sensitive_data"
    CREDENTIAL_LEAK = "credential_leak"
    PII_EXPOSED = "pii_exposed"
    
    # 配置风险
    CONFIG_WEAK_AUTH = "config_weak_auth"
    CONFIG_NETWORK_EXPOSED = "config_network_exposed"
    CONFIG_INSECURE = "config_insecure"


class Finding(BaseModel):
    """单个发现"""
    id: str = Field(..., description="发现ID")
    type: FindingType = Field(..., description="发现类型")
    severity: Severity = Field(..., description="风险等级")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    evidence: Optional[str] = Field(None, description="证据/代码片段")
    location: Optional[str] = Field(None, description="位置（文件路径等）")
    line_number: Optional[int] = Field(None, description="行号")
    recommendation: str = Field(..., description="修复建议")
    references: list[str] = Field(default_factory=list, description="参考链接")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetType(str, Enum):
    """资产类型"""
    OPENCLAW = "openclaw"
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    COPILOT = "copilot"
    OTHER = "other"


class Skill(BaseModel):
    """Skill 信息"""
    name: str
    path: Path
    source: str = "unknown"  # bundled, extra, custom
    description: Optional[str] = None
    has_scripts: bool = False
    script_files: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class Plugin(BaseModel):
    """Plugin 信息"""
    name: str
    path: Path
    version: Optional[str] = None
    enabled: bool = False
    findings: list[Finding] = Field(default_factory=list)


class APIKey(BaseModel):
    """API Key 信息"""
    provider: str
    key_preview: str  # 只显示前几位
    key_hash: str  # 完整 key 的 hash
    location: str  # 发现位置
    is_valid: Optional[bool] = None
    permissions: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class AgentConfig(BaseModel):
    """Agent 配置信息"""
    version: Optional[str] = None
    model: Optional[str] = None
    workspace: Optional[Path] = None
    gateway_port: Optional[int] = None
    gateway_bind: Optional[str] = None
    auth_mode: Optional[str] = None
    enabled_channels: list[str] = Field(default_factory=list)
    enabled_skills: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class Asset(BaseModel):
    """资产信息"""
    type: AssetType
    name: str
    path: Path
    version: Optional[str] = None
    config: Optional[AgentConfig] = None
    skills: list[Skill] = Field(default_factory=list)
    plugins: list[Plugin] = Field(default_factory=list)
    api_keys: list[APIKey] = Field(default_factory=list)
    memory_files: list[Path] = Field(default_factory=list)
    log_files: list[Path] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    scanned_at: datetime = Field(default_factory=datetime.now)


class ScanResult(BaseModel):
    """扫描结果"""
    scan_id: str = Field(..., description="扫描ID")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # 资产
    assets: list[Asset] = Field(default_factory=list)
    
    # 汇总
    total_findings: int = 0
    findings_by_severity: dict[str, int] = Field(default_factory=dict)
    findings_by_type: dict[str, int] = Field(default_factory=dict)
    
    # 统计
    stats: dict[str, Any] = Field(default_factory=dict)
    
    # 报告
    report_path: Optional[str] = None
    
    def add_finding(self, finding: Finding):
        """添加发现"""
        self.total_findings += 1
        self.findings_by_severity[finding.severity.value] = \
            self.findings_by_severity.get(finding.severity.value, 0) + 1
        self.findings_by_type[finding.type.value] = \
            self.findings_by_type.get(finding.type.value, 0) + 1
    
    def summarize(self) -> dict:
        """生成摘要"""
        return {
            "scan_id": self.scan_id,
            "assets_found": len(self.assets),
            "total_findings": self.total_findings,
            "critical": self.findings_by_severity.get("critical", 0),
            "high": self.findings_by_severity.get("high", 0),
            "medium": self.findings_by_severity.get("medium", 0),
            "low": self.findings_by_severity.get("low", 0),
            "info": self.findings_by_severity.get("info", 0),
        }
