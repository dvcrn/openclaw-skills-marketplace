"""
TTS 供应商模块
"""
from .base import TTSProvider
from .edge_tts import EdgeTTSProvider
from .azure_tts import AzureTTSProvider

# 供应商注册表
PROVIDERS = {
    "edge": EdgeTTSProvider,
    "azure": AzureTTSProvider,
    # 预留：百度、讯飞、腾讯云等
    # "baidu": BaiduTTSProvider,
    # "xunfei": XunfeiTTSProvider,
}

def get_provider(name: str = "edge") -> TTSProvider:
    """
    获取 TTS 供应商实例
    
    Args:
        name: 供应商名称 (edge, azure, ...)
        
    Returns:
        TTSProvider 实例
        
    Raises:
        ValueError: 未知供应商
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"未知供应商: {name}。可用: {available}")
    
    return PROVIDERS[name]()

def list_providers() -> list:
    """返回所有可用供应商名称"""
    return list(PROVIDERS.keys())

def list_available_providers() -> list:
    """返回当前可用的供应商名称（配置完整）"""
    available = []
    for name, provider_class in PROVIDERS.items():
        try:
            provider = provider_class()
            if provider.is_available():
                available.append(name)
        except:
            pass
    return available

__all__ = [
    "TTSProvider",
    "EdgeTTSProvider",
    "AzureTTSProvider",
    "PROVIDERS",
    "get_provider",
    "list_providers",
    "list_available_providers",
]
