# YOLO与SAM模型集成指南

## 核心思路
- YOLO用于快速目标检测，SAM用于精细分割
- 级联处理：先用YOLO检测，再用SAM分割检测到的目标
- 互补优势：YOLO的速度 + SAM的精度

## 关键代码

### 级联处理示例
```python
# 1. YOLO快速检测
yolo_model = YOLO('yolo26n.pt')
detections = yolo_model('image.jpg', conf=0.25)

# 2. 提取检测框
boxes = detections[0].boxes.xyxy.cpu().numpy()

# 3. SAM精细分割（如果可用）
if sam_available:
    sam_results = sam_model(boxes, 'image.jpg')
```

### 集成策略
1. **实时应用**: 主要使用YOLO，SAM仅用于关键帧
2. **离线分析**: YOLO初筛 + SAM精分割
3. **混合模式**: 根据置信度动态选择模型

## 模型对比
| 特性 | YOLO26系列 | SAM 3 | 集成优势 |
|------|------------|-------|----------|
| 速度 | 极快(2-8ms) | 较慢(30ms) | YOLO初筛加速 |
| 精度 | 良好 | 优秀 | SAM提升分割质量 |
| 大小 | 小(5-6MB) | 大(3.4GB) | 按需加载 |

## 使用建议
- **生产环境**: 优先使用YOLO，SAM作为可选增强
- **研究场景**: 可深度集成两者
- **资源有限**: 仅使用YOLO，保持实时性