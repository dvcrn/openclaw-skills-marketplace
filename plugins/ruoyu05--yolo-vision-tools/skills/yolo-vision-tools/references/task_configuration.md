# 任务配置指南

## 配置思路
根据任务需求调整参数，平衡速度、精度和资源使用。

## 关键参数
```python
# 置信度阈值
conf = 0.25  # 默认
# conf=0.1  # 检测更多目标
# conf=0.5  # 减少误报

# IoU阈值
iou = 0.45  # 默认
# iou=0.3   # 宽松合并
# iou=0.6   # 严格合并

# 图像尺寸
imgsz = 640  # 默认
# imgsz=320  # 更快
# imgsz=1280 # 更准
```

## 场景配置模板

### 小目标检测
```python
config = {
    'model': 'yolo26l',    # 大模型提高精度
    'imgsz': 1280,        # 大尺寸保留细节
    'conf': 0.1           # 低置信度
}
```

### 密集目标检测
```python
config = {
    'model': 'yolo26s',    # 平衡性能
    'conf': 0.3,          # 较高置信度
    'max_det': 1000       # 增加最大检测数
}
```

### 实时检测
```python
config = {
    'model': 'yolo26n',    # 最快模型
    'imgsz': 320,         # 小尺寸提高速度
    'half': True          # 半精度加速
}
```

## 任务类型配置

### 实例分割
```python
config = {
    'model': 'yolo26n-seg',  # 分割模型
    'retina_masks': True     # 高分辨率掩码
}
```

### 目标跟踪
```python
config = {
    'model': 'yolo26n',
    'persist': True,        # 保持跟踪ID
    'tracker': 'bytetrack.yaml'
}
```

## 设备优化
```python
# 设备选择
device = 'cuda'  # GPU
# device='cpu'   # CPU
# device='mps'   # Apple Silicon

# 性能优化
config = {
    'half': True,      # 半精度
    'workers': 1,      # 数据加载线程
    'batch': 4         # 批量大小
}
```

## 配置策略
- **速度优先**: yolo26n + imgsz=320 + half=True
- **精度优先**: yolo26l + imgsz=1280 + augment=True
- **内存受限**: yolo26n + batch=1 + workers=1

## 实用技巧
1. 从默认值开始，逐步调整
2. 一次只调整1-2个参数
3. 根据场景选择配置模板
4. 监控推理时间优化性能