#!/usr/bin/env python3
"""AI客户端统一接口"""

import os
import time
from typing import Optional
from abc import ABC, abstractmethod


class AIClient(ABC):
    """AI客户端抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = None, seed: int = None) -> str:
        """生成文本
        
        Args:
            prompt: 输入提示词
            temperature: 温度参数
            seed: 随机种子
        
        Returns:
            生成的文本
        """
        pass


class MockAIClient(AIClient):
    """模拟AI客户端（用于测试）"""
    
    def generate(self, prompt: str, temperature: float = None, seed: int = None) -> str:
        """生成模拟输出"""
        # 使用seed生成确定性输出（模拟）
        if seed is not None:
            import random
            random.seed(seed)
            # 基于prompt和seed生成伪随机但确定的输出
            hash_val = hash(f"{prompt}_{seed}")
            return f"Mock output for '{prompt[:30]}...' (seed={seed}, hash={abs(hash_val) % 10000})"
        
        # 无seed时返回固定输出
        return f"Mock output for '{prompt[:30]}...'"


class ZhipuClient(AIClient):
    """智谱AI客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("智谱API Key未配置")
    
    def generate(self, prompt: str, temperature: float = None, seed: int = None) -> str:
        """调用智谱API"""
        try:
            # 这里应该调用真实的智谱API
            # 暂时返回模拟输出
            return f"智谱输出: {prompt[:50]}... (temp={temperature}, seed={seed})"
        except Exception as e:
            raise RuntimeError(f"智谱API调用失败: {e}")


class DeepSeekClient(AIClient):
    """DeepSeek客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置")
    
    def generate(self, prompt: str, temperature: float = None, seed: int = None) -> str:
        """调用DeepSeek API"""
        try:
            # 这里应该调用真实的DeepSeek API
            # 暂时返回模拟输出
            return f"DeepSeek输出: {prompt[:50]}... (temp={temperature}, seed={seed})"
        except Exception as e:
            raise RuntimeError(f"DeepSeek API调用失败: {e}")


def get_client(provider: str = "mock", api_key: str = None) -> AIClient:
    """获取AI客户端
    
    Args:
        provider: 提供商（mock/zhipu/deepseek）
        api_key: API密钥
    
    Returns:
        AI客户端实例
    """
    clients = {
        "mock": MockAIClient,
        "zhipu": ZhipuClient,
        "deepseek": DeepSeekClient
    }
    
    if provider not in clients:
        raise ValueError(f"未知的AI提供商: {provider}")
    
    client_class = clients[provider]
    return client_class(api_key) if api_key else client_class()
