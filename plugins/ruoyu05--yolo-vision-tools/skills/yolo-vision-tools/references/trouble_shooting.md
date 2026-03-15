# 故障排除指南

## 常见问题与解决方案

### 安装问题
```bash
# 使用国内镜像
pip install ultralytics -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建虚拟环境
python -m venv yolo-env
source yolo-env/bin/activate
pip install ultralytics
```

### 导入问题
```python
# 检查安装
import subprocess
subprocess.run(['pip', 'show', 'ultralytics'])

# 重新安装
subprocess.run(['pip', 'install', 'ultralytics', '--no-cache-dir'])
```

### GPU问题
```python
# 检查CUDA
import torch
print(f"CUDA可用: {torch.cuda.is_available()}")

# 显存不足时
results = model(images, batch=1)  # 减少批量
torch.cuda.empty_cache()  # 清理显存
```

### 模型问题
```python
# 模型下载失败时手动下载
import requests
url = "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt"
response = requests.get(url)
with open('yolo26n.pt', 'wb') as f:
    f.write(response.content)
```

### 推理问题
```python
# 检测结果为空
results = model('image.jpg', conf=0.1)  # 降低置信度

# 推理速度慢
results = model('image.jpg', imgsz=320, device='cuda', half=True)
```

### 内存问题
```python
# 内存不足
results = model('image.jpg', workers=1, batch=1, device='cpu')
```

### 视频问题
```python
# 视频处理慢
results = model('video.mp4', vid_stride=2)  # 跳帧处理
```

## 排查步骤
1. 检查安装：`pip show ultralytics`
2. 测试导入：`python -c "from ultralytics import YOLO"`
3. 验证模型：加载简单模型测试
4. 检查设备：确认GPU/CUDA状态

## 获取帮助
- 官方文档：https://docs.ultralytics.com
- GitHub Issues：https://github.com/ultralytics/ultralytics/issues