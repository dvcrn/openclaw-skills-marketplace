#!/usr/bin/env python3
"""温度控制模块"""

from datetime import datetime
from typing import Dict, Optional
from config import ConfigManager


class TemperatureController:
    """温度控制器"""
    
    # 温度预设
    PRESETS = {
        "code": {
            "temperature": 0.0,
            "description": "高度确定性（代码/配置生成）",
            "range": "0.0-0.3"
        },
        "balance": {
            "temperature": 0.5,
            "description": "平衡模式（常规对话）",
            "range": "0.3-0.7"
        },
        "creative": {
            "temperature": 0.8,
            "description": "创造性模式（创意写作）",
            "range": "0.7-1.0"
        },
        "brainstorm": {
            "temperature": 1.5,
            "description": "高创造性模式（头脑风暴）",
            "range": "1.0-2.0"
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
    
    def set_temperature(self, temp: float) -> Dict:
        """设置温度参数
        
        Args:
            temp: 温度值（0.0-2.0）
        
        Returns:
            配置确认信息
        
        Raises:
            ValueError: 温度超出范围
        """
        if not 0.0 <= temp <= 2.0:
            raise ValueError(f"温度必须在0.0-2.0之间，当前: {temp}")
        
        # 精度控制（保留1位小数）
        temp = round(temp, 1)
        
        # 更新配置
        self.config_manager.set("temperature", temp)
        self.config["temperature"] = temp
        
        return {
            "temperature": temp,
            "mode": self._get_mode(temp),
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    
    def get_preset(self, preset_name: str) -> Dict:
        """获取预设配置
        
        Args:
            preset_name: 预设名称（code/balance/creative/brainstorm）
        
        Returns:
            预设配置
        
        Raises:
            ValueError: 未知预设
        """
        if preset_name not in self.PRESETS:
            available = ", ".join(self.PRESETS.keys())
            raise ValueError(f"未知预设: {preset_name}。可用预设: {available}")
        
        return self.PRESETS[preset_name].copy()
    
    def use_preset(self, preset_name: str) -> Dict:
        """使用预设配置
        
        Args:
            preset_name: 预设名称
        
        Returns:
            配置确认信息
        """
        preset = self.get_preset(preset_name)
        return self.set_temperature(preset["temperature"])
    
    def get_current(self) -> float:
        """获取当前温度"""
        return self.config.get("temperature", 0.5)
    
    def _get_mode(self, temp: float) -> str:
        """根据温度判断模式"""
        if temp <= 0.3:
            return "高度确定性"
        elif temp <= 0.7:
            return "平衡模式"
        elif temp <= 1.0:
            return "创造性模式"
        else:
            return "高创造性模式"
    
    def list_presets(self) -> Dict[str, Dict]:
        """列出所有预设"""
        return self.PRESETS.copy()
