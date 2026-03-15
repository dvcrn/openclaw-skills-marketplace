# 性能优化指南

## 优化思路
在速度、精度和资源消耗之间找到最佳平衡。

## 关键配置

### 速度优化（推理加速）
```python
config = {
    'model': 'yolo26n',    # 最小最快模型
    'imgsz': 320,         # 小尺寸输入
    'half': True,         # 半精度（GPU）
    'batch': 4,           # 批量处理
    'conf': 0.3           # 较高置信度
}
```

### 精度优化（质量提升）
```python
config = {
    'model': 'yolo26l',    # 高精度模型
    'imgsz': 1280,        # 大尺寸保留细节
    'conf': 0.1,          # 低置信度捕获更多
    'augment': True       # 测试时增强
}
```

### 内存优化（资源受限）
```python
config = {
    'model': 'yolo26n',    # 最小模型
    'imgsz': 320,         # 小尺寸
    'batch': 1,           # 单张处理
    'device': 'cpu'       # CPU推理
}
```

## 参数调整指南
| 参数 | 速度优化 | 精度优化 | 说明 |
|------|----------|----------|------|
| **imgsz** | 320 | 1280 | 影响最大 |
| **conf** | 0.3-0.5 | 0.05-0.1 | 控制检测数量 |
| **half** | True | False | GPU半精度加速 |
| **batch** | 8-16 | 1-4 | 批量大小 |

## 设备优化

### GPU优化
```python
config = {'device': 'cuda', 'half': True, 'batch': 8}
```

### CPU优化  
```python
config = {'device': 'cpu', 'workers': 1, 'batch': 1}
```

### Apple Silicon
```python
config = {'device': 'mps', 'half': True}
```

## 性能监控
```python
import time
start = time.time()
results = model('image.jpg', **config)
print(f"推理时间: {time.time()-start:.3f}s")
```

## 实用建议
1. 先测量默认配置性能
2. 一次调整1-2个参数
3. 根据实际需求选择优化方向
4. 关注内存、显存使用情况