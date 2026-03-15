# 硬件加速指南

## 核心思路
利用GPU、半精度和批处理提升推理速度。

## 关键代码

### GPU加速
```python
# 检查CUDA
import torch
print(f"CUDA可用: {torch.cuda.is_available()}")

# YOLO GPU使用
model = YOLO('yolo26n.pt', device='cuda')
results = model('image.jpg', device='cuda')
```

### 性能优化技巧
```python
# 半精度推理（FP16）
results = model('image.jpg', half=True)

# 批处理优化
results = model(['img1.jpg', 'img2.jpg'], batch=4)

# 显存管理
torch.cuda.empty_cache()
```

## 设备配置

### NVIDIA GPU
```python
config = {
    'device': 'cuda',
    'half': True,    # 半精度加速
    'batch': 8       # 批量大小
}
```

### Apple Silicon
```python
config = {
    'device': 'mps',  # Metal Performance Shaders
    'half': True
}
```

### CPU优化
```python
config = {
    'device': 'cpu',
    'workers': 1,     # 减少线程竞争
    'batch': 1        # 单张处理
}
```

## 性能监控
```python
import time
start = time.time()
results = model('image.jpg', **config)
print(f"推理时间: {time.time()-start:.3f}s")
```

## 实用建议
1. 先测试CPU确保代码正确
2. 逐步启用GPU优化
3. 根据显存调整批量大小
4. 监控显存避免OOM