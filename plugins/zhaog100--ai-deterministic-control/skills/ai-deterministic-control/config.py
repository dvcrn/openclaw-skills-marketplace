#!/usr/bin/env python3
"""配置管理模块"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认配置文件路径
            config_dir = Path(__file__).parent
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                "temperature": 0.5,
                "default_mode": "balance",
                "api_provider": "mock",  # 默认使用mock（测试模式）
                "api_key": "",
                "history_db": str(self.config_path.parent / "history.db"),
                "seeds_file": str(self.config_path.parent / "seeds.json"),
                "cache_enabled": True,
                "cache_ttl": 300  # 5分钟
            }
            self._save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict[str, Any] = None):
        """保存配置"""
        if config is None:
            config = self.config
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value
        self._save_config()
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        self.config.update(updates)
        self._save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()
