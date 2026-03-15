"""
飞书语音发送器配置
"""
import os

# 默认 TTS 供应商
DEFAULT_PROVIDER = os.getenv("FEISHU_VOICE_PROVIDER", "edge")

# 供应商配置
PROVIDER_CONFIG = {
    "edge": {
        "name": "Microsoft Edge TTS",
        "description": "免费在线 TTS，无需注册",
        "requires_key": False,
    },
    "azure": {
        "name": "Azure Speech Service",
        "description": "微软 Azure 语音服务，质量高",
        "requires_key": True,
        "env_keys": ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"],
    },
}

# 默认语音（按供应商）
DEFAULT_VOICES = {
    "edge": "xiaoxiao",      # 温暖女声
    "azure": "xiaochen",     # 自然女声
}
