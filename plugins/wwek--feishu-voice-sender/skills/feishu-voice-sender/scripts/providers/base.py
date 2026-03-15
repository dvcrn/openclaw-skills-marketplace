"""
TTS 供应商基类
所有 TTS 供应商必须继承此类并实现接口
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional

class TTSProvider(ABC):
    """TTS 供应商抽象基类"""
    
    name = "base"
    
    @abstractmethod
    def synthesize(self, text: str, voice: str = None) -> Tuple[Optional[bytes], Optional[int]]:
        """
        将文字转换为语音
        
        Args:
            text: 要转换的文字
            voice: 语音类型/音色
            
        Returns:
            (音频字节数据, 时长秒数) 或 (None, None) 失败
        """
        pass
    
    @abstractmethod
    def get_voices(self) -> list:
        """返回可用的语音列表"""
        pass
    
    def is_available(self) -> bool:
        """检查供应商是否可用"""
        return True
