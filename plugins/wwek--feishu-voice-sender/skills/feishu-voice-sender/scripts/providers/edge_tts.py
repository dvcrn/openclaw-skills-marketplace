"""
Edge TTS 供应商实现
基于 Microsoft Edge 在线 TTS 服务（免费）
"""
import subprocess
import tempfile
import os
from .base import TTSProvider

class EdgeTTSProvider(TTSProvider):
    """Edge TTS 供应商 - 免费在线 TTS"""
    
    name = "edge"
    
    # 推荐的语音列表
    VOICES = {
        # 女声
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 温暖、专业 ⭐推荐
        "xiaoyi": "zh-CN-XiaoyiNeural",          # 活泼、卡通
        "xiaochen": "zh-CN-XiaochenNeural",      # 自然、温柔
        "xiaohan": "zh-CN-XiaohanNeural",        # 甜美
        # 男声
        "yunyang": "zh-CN-YunyangNeural",        # 专业、可靠 ⭐推荐
        "yunxi": "zh-CN-YunxiNeural",            # 活泼、阳光
        "yunjian": "zh-CN-YunjianNeural",        # 新闻播报
        "yunfeng": "zh-CN-YunfengNeural",        # 成熟
        # 方言
        "xiaobei": "zh-CN-liaoning-XiaobeiNeural",   # 辽宁话
        "xiaoni": "zh-CN-shaanxi-XiaoniNeural",      # 陕西话
    }
    
    def __init__(self):
        self._check_dependency()
    
    def _check_dependency(self):
        """检查 edge-tts 是否已安装"""
        result = subprocess.run(["which", "edge-tts"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("edge-tts 未安装，请运行: pip install edge-tts")
    
    def synthesize(self, text: str, voice: str = None) -> tuple:
        """
        使用 Edge TTS 生成语音
        
        Args:
            text: 要转换的文字
            voice: 语音名称（如 xiaoxiao, yunyang）或完整 voice ID
            
        Returns:
            (mp3_bytes, duration_seconds) 或 (None, None)
        """
        # 解析 voice
        if voice is None:
            voice_id = self.VOICES["xiaoxiao"]
        elif voice in self.VOICES:
            voice_id = self.VOICES[voice]
        else:
            # 假设传入的是完整 voice ID
            voice_id = voice
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            mp3_file = f.name
        
        try:
            # 调用 edge-tts
            cmd = [
                "edge-tts",
                "--voice", voice_id,
                "--text", text,
                "--write-media", mp3_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Edge TTS 失败: {result.stderr}")
                return None, None
            
            # 读取 MP3 数据
            with open(mp3_file, "rb") as f:
                mp3_bytes = f.read()
            
            # 获取时长
            duration = self._get_duration(mp3_file)
            
            return mp3_bytes, duration
            
        finally:
            # 清理临时文件
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
    
    def _get_duration(self, audio_file: str) -> int:
        """获取音频时长（秒）"""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return int(float(result.stdout.strip()))
        except:
            # 估算：大约每分钟 150 字
            return 0
    
    def get_voices(self) -> list:
        """返回可用的语音列表"""
        return list(self.VOICES.keys())
    
    def is_available(self) -> bool:
        """检查 edge-tts 是否可用"""
        result = subprocess.run(["which", "edge-tts"], capture_output=True)
        return result.returncode == 0
