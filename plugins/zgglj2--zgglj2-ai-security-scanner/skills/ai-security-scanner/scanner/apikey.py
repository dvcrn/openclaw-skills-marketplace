"""
API Key 检测模块
扫描配置文件、环境变量、代码中的 API Key
"""
import hashlib
import os
import re
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scanner.models import APIKey, Asset, Finding, FindingType, Severity

console = Console()


class APIKeyScanner:
    """API Key 泄露检测"""
    
    # 已知 API Key 格式
    PATTERNS = {
        "openai": {
            "pattern": r"sk-[a-zA-Z0-9]{20,}",
            "test_url": "https://api.openai.com/v1/models",
            "description": "OpenAI API Key",
        },
        "anthropic": {
            "pattern": r"sk-ant-api[a-zA-Z0-9-]{20,}",
            "test_url": "https://api.anthropic.com/v1/messages",
            "description": "Anthropic API Key",
        },
        "gemini": {
            "pattern": r"AIza[a-zA-Z0-9_-]{35}",
            "test_url": "https://generativelanguage.googleapis.com/v1/models",
            "description": "Google Gemini API Key",
        },
        "openrouter": {
            "pattern": r"sk-or-[a-zA-Z0-9-]{20,}",
            "test_url": "https://openrouter.ai/api/v1/models",
            "description": "OpenRouter API Key",
        },
        "moonshot": {
            "pattern": r"sk-[a-zA-Z0-9]{20,}",
            "test_url": "https://api.moonshot.cn/v1/models",
            "description": "Moonshot (Kimi) API Key",
        },
        "zhipu": {
            "pattern": r"[a-f0-9]{32}\.[a-f0-9]{32}",
            "test_url": None,
            "description": "智谱 AI API Key",
        },
        "deepseek": {
            "pattern": r"sk-[a-f0-9]{32,}",
            "test_url": "https://api.deepseek.com/v1/models",
            "description": "DeepSeek API Key",
        },
    }
    
    # 扫描文件扩展名
    SCAN_EXTENSIONS = {
        ".env", ".json", ".yaml", ".yml", ".toml",
        ".md", ".txt", ".py", ".js", ".ts", ".sh",
        ".bash", ".zsh", ".fish",
    }
    
    # 排除的目录
    EXCLUDE_DIRS = {
        "node_modules", ".git", "__pycache__", "venv",
        ".venv", "env", ".env", "dist", "build",
    }
    
    def __init__(
        self,
        verify_keys: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
    ):
        self.verify_keys = verify_keys
        self.max_file_size = max_file_size
        self.findings: list[Finding] = []
    
    def scan(self, assets: list[Asset]) -> list[APIKey]:
        """扫描资产中的 API Key"""
        all_keys = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for asset in assets:
                task = progress.add_task(
                    f"扫描 {asset.name} 的 API Key...",
                    total=None
                )
                
                keys = self.scan_asset(asset)
                all_keys.extend(keys)
                
                if keys:
                    console.print(
                        f"[yellow]⚠[/yellow] {asset.name}: 发现 {len(keys)} 个 API Key"
                    )
        
        return all_keys
    
    def scan_asset(self, asset: Asset) -> list[APIKey]:
        """扫描单个资产"""
        keys = []
        
        # 1. 扫描配置文件
        if asset.config and hasattr(asset.config, '__dict__'):
            config_keys = self._scan_config_dict(asset.config.__dict__, str(asset.path))
            keys.extend(config_keys)
        
        # 2. 扫描配置文件（openclaw.json 等）
        config_file = asset.path / "openclaw.json"
        if config_file.exists():
            file_keys = self._scan_file(config_file)
            keys.extend(file_keys)
        
        # 3. 扫描 .env 文件
        env_file = asset.path / ".env"
        if env_file.exists():
            env_keys = self._scan_file(env_file)
            keys.extend(env_keys)
        
        # 4. 扫描环境变量
        env_keys = self._scan_environment()
        keys.extend(env_keys)
        
        # 5. 扫描 Skills 中的脚本
        for skill in asset.skills:
            if skill.has_scripts:
                for script_file in skill.script_files:
                    script_keys = self._scan_file(Path(script_file))
                    for key in script_keys:
                        key.findings.append(Finding(
                            id=f"apikey-skill-{skill.name}",
                            type=FindingType.API_KEY_EXPOSED,
                            severity=Severity.CRITICAL,
                            title=f"Skill '{skill.name}' 中包含 API Key",
                            description=f"在 Skill '{skill.name}' 的脚本中发现 API Key",
                            location=script_file,
                            recommendation="从脚本中移除 API Key，使用环境变量或配置文件",
                        ))
                    keys.extend(script_keys)
        
        # 去重
        seen_hashes = set()
        unique_keys = []
        for key in keys:
            if key.key_hash not in seen_hashes:
                seen_hashes.add(key.key_hash)
                unique_keys.append(key)
        
        # 验证 Key
        if self.verify_keys:
            for key in unique_keys:
                self._verify_key(key)
        
        # 更新资产
        asset.api_keys = unique_keys
        
        return unique_keys
    
    def _scan_config_dict(self, config: dict, location: str) -> list[APIKey]:
        """扫描配置字典"""
        keys = []
        
        def scan_value(value: any, path: str):
            if isinstance(value, str):
                for provider, info in self.PATTERNS.items():
                    matches = re.findall(info["pattern"], value)
                    for match in matches:
                        key = self._create_key(provider, match, f"{location}#{path}")
                        keys.append(key)
            elif isinstance(value, dict):
                for k, v in value.items():
                    scan_value(v, f"{path}.{k}")
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    scan_value(v, f"{path}[{i}]")
        
        scan_value(config, "config")
        return keys
    
    def _scan_file(self, file_path: Path) -> list[APIKey]:
        """扫描文件"""
        keys = []
        
        try:
            # 检查文件大小
            if file_path.stat().st_size > self.max_file_size:
                return keys
            
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            for provider, info in self.PATTERNS.items():
                matches = re.findall(info["pattern"], content)
                for match in matches:
                    key = self._create_key(provider, match, str(file_path))
                    keys.append(key)
        
        except Exception as e:
            console.print(f"[yellow]警告: 扫描文件失败 {file_path}: {e}[/yellow]")
        
        return keys
    
    def _scan_environment(self) -> list[APIKey]:
        """扫描环境变量"""
        keys = []
        
        for env_name, env_value in os.environ.items():
            # 跳过明显的非 Key 环境变量
            if not env_value or len(env_value) < 10:
                continue
            
            for provider, info in self.PATTERNS.items():
                if re.match(info["pattern"], env_value):
                    key = self._create_key(
                        provider,
                        env_value,
                        f"env:{env_name}"
                    )
                    keys.append(key)
        
        return keys
    
    def _create_key(self, provider: str, key_value: str, location: str) -> APIKey:
        """创建 API Key 对象"""
        # 生成预览（只显示前8位）
        preview = key_value[:8] + "..." if len(key_value) > 8 else key_value
        
        # 生成 hash（用于去重）
        key_hash = hashlib.sha256(key_value.encode()).hexdigest()[:16]
        
        key = APIKey(
            provider=provider,
            key_preview=preview,
            key_hash=key_hash,
            location=location,
        )
        
        # 添加发现
        key.findings.append(Finding(
            id=f"apikey-{key_hash}",
            type=FindingType.API_KEY_EXPOSED,
            severity=Severity.CRITICAL,
            title=f"发现 {provider.upper()} API Key",
            description=f"在 {location} 发现 {provider} API Key",
            location=location,
            evidence=f"Key 前缀: {preview}",
            recommendation=(
                f"1. 立即轮换该 API Key\n"
                f"2. 将 Key 移至环境变量或加密配置\n"
                f"3. 审计 Key 的使用记录"
            ),
            metadata={"provider": provider, "key_hash": key_hash},
        ))
        
        return key
    
    def _verify_key(self, key: APIKey) -> bool:
        """验证 API Key 有效性"""
        provider_info = self.PATTERNS.get(key.provider)
        
        if not provider_info or not provider_info.get("test_url"):
            return False
        
        try:
            # 获取完整 Key（从环境变量或文件）
            # 注意：这里只是验证，不会存储完整 Key
            full_key = self._get_full_key(key)
            
            if not full_key:
                return False
            
            # 发送测试请求
            headers = {}
            if key.provider == "openai":
                headers["Authorization"] = f"Bearer {full_key}"
            elif key.provider == "anthropic":
                headers["x-api-key"] = full_key
            elif key.provider == "gemini":
                # Gemini 使用 query parameter
                pass
            else:
                headers["Authorization"] = f"Bearer {full_key}"
            
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    provider_info["test_url"],
                    headers=headers,
                    follow_redirects=True,
                )
                
                key.is_valid = response.status_code in [200, 403]  # 403 也说明 Key 有效
                
                if key.is_valid:
                    key.findings.append(Finding(
                        id=f"apikey-valid-{key.key_hash}",
                        type=FindingType.API_KEY_VALID,
                        severity=Severity.HIGH,
                        title=f"API Key 有效",
                        description=f"{key.provider} API Key 验证有效，存在被滥用风险",
                        recommendation="立即轮换该 Key",
                    ))
                
                return key.is_valid
        
        except Exception as e:
            console.print(f"[yellow]警告: 验证 Key 失败: {e}[/yellow]")
            return False
    
    def _get_full_key(self, key: APIKey) -> Optional[str]:
        """获取完整 Key（从原始位置）"""
        try:
            location = key.location
            
            if location.startswith("env:"):
                env_name = location.split(":")[1]
                return os.environ.get(env_name)
            
            elif "#" in location:
                # 配置文件路径
                file_path, path = location.split("#", 1)
                # TODO: 解析配置路径获取 Key
                return None
            
            else:
                # 文件路径，重新扫描获取
                file_path = Path(location)
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    provider_info = self.PATTERNS.get(key.provider)
                    if provider_info:
                        matches = re.findall(provider_info["pattern"], content)
                        for match in matches:
                            # 验证 hash 匹配
                            if hashlib.sha256(match.encode()).hexdigest()[:16] == key.key_hash:
                                return match
        
        except Exception:
            pass
        
        return None
    
    def scan_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> list[Finding]:
        """扫描目录中的 API Key"""
        findings = []
        
        def scan_dir(dir_path: Path, depth: int = 0):
            if depth > 10:  # 限制递归深度
                return
            
            try:
                for item in dir_path.iterdir():
                    if item.is_dir():
                        if item.name in self.EXCLUDE_DIRS:
                            continue
                        if recursive:
                            scan_dir(item, depth + 1)
                    elif item.is_file():
                        if item.suffix in self.SCAN_EXTENSIONS:
                            keys = self._scan_file(item)
                            for key in keys:
                                findings.extend(key.findings)
            except PermissionError:
                pass
        
        scan_dir(directory)
        return findings
