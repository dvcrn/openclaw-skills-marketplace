# 模型选择指南

## 选择思路
根据应用场景在速度、精度和资源消耗之间平衡。

## YOLO26系列模型
| 模型 | 特点 | 适用场景 |
|------|------|----------|
| **yolo26n** | 最快，最小 | 实时应用，移动端 |
| **yolo26s** | 平衡性能 | 通用应用 |
| **yolo26m** | 中等精度 | 服务器应用 |
| **yolo26l** | 高精度 | 精度优先场景 |
| **yolo26x** | 最高精度 | 研究/极限需求 |

## 按场景选择

### 实时视频分析
```python
model = YOLO('yolo26n.pt')  # 最快模型
config = {'imgsz': 320, 'conf': 0.25, 'half': True}
```

### 高精度图像分析
```python
model = YOLO('yolo26l.pt')  # 高精度模型
config = {'imgsz': 1280, 'conf': 0.1, 'augment': True}
```

### 边缘设备部署
```python
model = YOLO('yolo26n.pt')  # 最小模型
config = {'imgsz': 320, 'conf': 0.3, 'device': 'cpu', 'workers': 1}
```

## 任务类型模型
```python
# 目标检测（默认）
model = YOLO('yolo26n.pt')

# 实例分割
model = YOLO('yolo26n-seg.pt')

# 图像分类
model = YOLO('yolo26n-cls.pt')

# 姿态估计
model = YOLO('yolo26n-pose.pt')
```

## 选择策略
1. **确定优先级**：
   - 速度优先 → yolo26n
   - 平衡性能 → yolo26s
   - 精度优先 → yolo26l

2. **调整参数**：
   - 速度优化：减小imgsz，提高conf
   - 精度优化：增大imgsz，降低conf

3. **设备适配**：
   - GPU：默认配置，可启用half=True
   - CPU：yolo26n，workers=1
   - 移动端：yolo26n，imgsz=320

## 实用建议
- 从yolo26s开始如果不确定
- 根据结果微调模型和参数
- 在实际数据上测试不同配置
- 关注内存使用和推理时间