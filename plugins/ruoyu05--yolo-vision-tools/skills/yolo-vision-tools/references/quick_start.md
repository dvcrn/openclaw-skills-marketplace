# YOLO快速开始指南

## 核心步骤
1. **安装**: `pip install ultralytics`
2. **使用**: 加载模型 → 预测 → 处理结果
3. **优化**: 根据需求调整参数

## 关键代码

### 基础使用
```python
# 加载模型
model = YOLO('yolo26n.pt')  # 最快
# model = YOLO('yolo26s.pt')  # 平衡
# model = YOLO('yolo26l.pt')  # 最准

# 预测
results = model('image.jpg', conf=0.25)

# 处理结果
results[0].show()  # 显示
results[0].save('result.jpg')  # 保存
```

### 不同任务
```python
# 实例分割
model = YOLO('yolo26n-seg.pt')
# 分类
model = YOLO('yolo26n-cls.pt')
# 姿态估计
model = YOLO('yolo26n-pose.pt')
# 目标跟踪
results = model.track('video.mp4', tracker='bytetrack.yaml')
```

### 关键参数
```python
# 置信度阈值
results = model('image.jpg', conf=0.25)  # 默认
# conf=0.1  # 更敏感
# conf=0.5  # 更严格

# 图像尺寸
results = model('image.jpg', imgsz=640)  # 默认
# imgsz=320  # 更快
# imgsz=1280 # 更准

# 设备选择
results = model('image.jpg', device='cuda')  # GPU
# device='cpu'  # CPU
# device='mps'  # Apple Silicon
```

## 结果处理
```python
results = model('image.jpg')
for box in results[0].boxes:
    xyxy = box.xyxy[0].tolist()  # 边界框
    conf = box.conf[0].item()    # 置信度
    cls = box.cls[0].item()      # 类别ID
    name = results[0].names[int(cls)]  # 类别名称
    print(f"{name}: {conf:.2f} at {xyxy}")
```

## 性能优化
- **速度优先**: yolo26n + imgsz=320 + half=True
- **精度优先**: yolo26l + imgsz=1280
- **内存优化**: workers=1