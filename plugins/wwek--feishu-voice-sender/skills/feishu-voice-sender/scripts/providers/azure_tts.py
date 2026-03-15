"""
Azure TTS 供应商实现（预留）
需要 Azure Speech Service 订阅
"""
from .base import TTSProvider

class AzureTTSProvider(TTSProvider):
    """
    Azure TTS 供应商
    
    使用说明：
    1. 在 Azure 创建 Speech Service 资源
    2. 获取 Key 和 Region
    3. 设置环境变量：
       - AZURE_SPEECH_KEY
       - AZURE_SPEECH_REGION
    """
    
    name = "azure"
    
    VOICES = {
        "xiaochen": "zh-CN-XiaochenNeural",
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",
        "xiaoyan": "zh-CN-XiaoyanNeural",
        "yunfeng": "zh-CN-YunfengNeural",
    }
    
    def __init__(self):
        self.key = None
        self.region = None
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        import os
        self.key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION")
    
    def synthesize(self, text: str, voice: str = None):
        """生成语音（需要安装 azure-cognitiveservices-speech）"""
        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError:
            print("❌ Azure SDK 未安装，请运行: pip install azure-cognitiveservices-speech")
            return None, None
        
        if not self.key or not self.region:
            print("❌ Azure 配置缺失，请设置 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION")
            return None, None
        
        # TODO: 实现 Azure TTS 调用
        print("⚠️ Azure TTS 实现待完成")
        return None, None
    
    def get_voices(self) -> list:
        return list(self.VOICES.keys())
    
    def is_available(self) -> bool:
        """检查 Azure 配置是否完整"""
        return bool(self.key and self.region)
