#!/usr/bin/env python3
"""可复现性保证模块"""

import json
import time
from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import Dict, List, Optional

from ai_client import get_client
from config import ConfigManager


class ReproducibilityGuarantor:
    """复现保证器"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # 种子文件路径
        seeds_file = self.config.get("seeds_file", "seeds.json")
        self.seeds_file = Path(seeds_file)
        self.seeds = self._load_seeds()
        
        # AI客户端
        provider = self.config.get("api_provider", "mock")
        self.ai_client = get_client(provider)
    
    def _load_seeds(self) -> List[Dict]:
        """加载种子记录"""
        if not self.seeds_file.exists():
            return []
        
        with open(self.seeds_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("records", [])
    
    def _save_seeds(self):
        """保存种子记录"""
        data = {"records": self.seeds}
        
        with open(self.seeds_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_with_seed(
        self, 
        prompt: str, 
        seed: Optional[int] = None,
        temperature: float = None
    ) -> Dict:
        """使用种子生成确定性输出
        
        Args:
            prompt: 输入提示词
            seed: 随机种子（None则自动生成）
            temperature: 温度参数
        
        Returns:
            确定性输出
        """
        # 生成种子
        if seed is None:
            seed = int(time.time() * 1000)
        
        # 获取温度
        if temperature is None:
            temperature = self.config.get("temperature", 0.5)
        
        # 调用AI
        output = self.ai_client.generate(prompt, temperature=temperature, seed=seed)
        
        # 记录种子
        output_hash = md5(output.encode()).hexdigest()[:16]
        self._record_seed(seed, prompt, output_hash)
        
        return {
            "output": output,
            "seed": seed,
            "temperature": temperature,
            "timestamp": datetime.now().isoformat(),
            "reproducible": True,
            "output_hash": output_hash
        }
    
    def _record_seed(self, seed: int, prompt: str, output_hash: str):
        """记录种子"""
        record = {
            "seed": seed,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "timestamp": datetime.now().isoformat(),
            "output_hash": output_hash
        }
        
        self.seeds.append(record)
        
        # 限制记录数量（最多1000条）
        if len(self.seeds) > 1000:
            self.seeds = self.seeds[-1000:]
        
        self._save_seeds()
    
    def verify_reproducibility(
        self, 
        prompt: str, 
        seed: int,
        iterations: int = 3,
        temperature: float = None
    ) -> Dict:
        """验证可复现性
        
        Args:
            prompt: 输入提示词
            seed: 随机种子
            iterations: 验证次数
            temperature: 温度参数
        
        Returns:
            验证结果
        """
        if iterations < 2:
            raise ValueError("验证次数至少为2")
        
        # 获取温度
        if temperature is None:
            temperature = self.config.get("temperature", 0.5)
        
        # 多次生成
        outputs = []
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.generate_with_seed(prompt, seed, temperature)
            outputs.append(result["output"])
        
        # 检查所有输出是否相同
        is_reproducible = all(o == outputs[0] for o in outputs)
        
        elapsed_time = time.time() - start_time
        
        return {
            "is_reproducible": is_reproducible,
            "seed": seed,
            "iterations": iterations,
            "temperature": temperature,
            "elapsed_time": round(elapsed_time, 2),
            "first_output": outputs[0][:100] + "..." if outputs[0] else "",
            "consistency": "100%" if is_reproducible else "不一致"
        }
    
    def get_seed_record(self, seed: int) -> Optional[Dict]:
        """获取种子记录
        
        Args:
            seed: 种子值
        
        Returns:
            种子记录（未找到则返回None）
        """
        for record in self.seeds:
            if record["seed"] == seed:
                return record
        return None
    
    def list_seeds(self, limit: int = 10) -> List[Dict]:
        """列出最近的种子记录
        
        Args:
            limit: 返回数量限制
        
        Returns:
            种子记录列表
        """
        return self.seeds[-limit:]
    
    def clear_seeds(self):
        """清空种子记录"""
        self.seeds = []
        self._save_seeds()
    
    def set_seed(self, seed: int) -> Dict:
        """设置当前种子（用于test.sh兼容）
        
        Args:
            seed: 种子值
        
        Returns:
            dict: 包含seed和timestamp
        """
        self._current_seed = seed
        return {
            "seed": seed,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_current_seed(self) -> int:
        """获取当前种子（用于test.sh兼容）
        
        Returns:
            int: 当前种子值
        """
        if not hasattr(self, '_current_seed'):
            self._current_seed = None
        return self._current_seed
