# 视频处理指南

## 核心问题与解决方案
**问题**: MPEG-4编码的视频在对话中发送后上可能卡在第一帧无法播放
**解决方案**: 必须使用H.264编码以确保兼容性

## 工作流程
1. YOLO检测输出AVI格式 → 2. 自动转换为MP4 → 3. 发送到对话

## 质量等级配置
| 等级 | CRF值 | 预设 | 适用场景 |
|------|-------|------|----------|
| high | 18 | slow | 高质量存档（默认） |
| medium | 23 | medium | 平衡质量与大小 |
| low | 28 | fast | 快速分享 |

## 核心代码实现

### 1. 视频编码检查
```python
def is_h264_video(video_path):
    """检查视频是否为H.264编码"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name',
        '-of', 'json',
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    if 'streams' in data and len(data['streams']) > 0:
        codec_name = data['streams'][0].get('codec_name')
        return codec_name in ['h264', 'libx264']
    return False
```

### 2. 视频编码转换
```python
def fix_video(input_path, output_path=None, quality='high'):
    """将视频转换为H.264编码以确保发送时的兼容性"""
    
    # 质量参数配置
    quality_params = {
        'high': {'crf': 18, 'preset': 'slow'},
        'medium': {'crf': 23, 'preset': 'medium'},
        'low': {'crf': 28, 'preset': 'fast'}
    }
    params = quality_params.get(quality, quality_params['high'])
    
    # H.264编码命令
    cmd = [
        'ffmpeg',
        '-y',                     # 覆盖已有文件
        '-i', input_path,
        '-c:v', 'libx264',        # H.264编码
        '-crf', str(params['crf']),
        '-preset', params['preset'],
        '-pix_fmt', 'yuv420p',    # 提高兼容性
        '-movflags', '+faststart',# 优化网页播放
        '-c:a', 'aac',            # 音频编码
        '-b:a', '128k',           # 音频比特率
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"编码失败: {e}")
        return None
```

### 3. YOLO检测后自动转换
```python
# YOLO视频检测
model = YOLO('yolo26n.pt')
results = model('input_video.mp4', save=True)

# 检测后的视频通常是AVI格式
detected_video = 'runs/detect/predict/input_video.avi'

# 自动转换为MP4
mp4_output = str(Path(detected_video).with_suffix(".mp4"))
fix_video(detected_video, mp4_output, quality='high')
```

## 关键参数说明
- `-c:v libx264`: H.264编码，视频发送的兼容性要求
- `-pix_fmt yuv420p`: 标准像素格式，确保广泛兼容
- `-movflags +faststart`: 优化网络播放，快速加载
- `-crf 18-28`: 质量控制（值越小质量越高）

## 注意事项
1. 所有通过对话发送的视频必须使用H.264编码
2. 建议使用`yuv420p`像素格式确保最大兼容性
3. 添加`faststart`标志优化移动端播放体验
4. 清理临时AVI文件以节省存储空间