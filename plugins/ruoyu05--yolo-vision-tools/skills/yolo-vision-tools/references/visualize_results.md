# 结果可视化指南

## 核心思路
将检测结果直观展示，便于分析和验证。

## 基础可视化

### 一键可视化
```python
results = model('image.jpg')
annotated = results[0].plot()  # 自动绘制边界框和标签

# 显示
cv2.imshow('Result', annotated)
cv2.waitKey(0)

# 保存
cv2.imwrite('result.jpg', annotated)
```

### 不同任务
```python
# 实例分割
annotated = results[0].plot()  # 自动绘制掩码

# 姿态估计
annotated = results[0].plot()  # 自动绘制关键点

# 分类结果
top5 = results[0].probs.top5  # 获取top-5类别
```

## 自定义可视化

### 样式定制
```python
annotated = results[0].plot(
    line_width=2,      # 边界框线宽
    font_size=0.5,     # 字体大小
    labels=True,       # 显示标签
    conf=True,         # 显示置信度
    boxes=True         # 显示边界框
)
```

## 结果提取

### 检测信息
```python
results = model('image.jpg')
for box in results[0].boxes:
    xyxy = box.xyxy[0].tolist()  # 边界框坐标
    conf = box.conf[0].item()    # 置信度
    cls = box.cls[0].item()      # 类别ID
    name = results[0].names[int(cls)]  # 类别名称
    print(f"{name}: {conf:.2f} at {xyxy}")
```

## 高级技巧

### 置信度过滤
```python
# 只显示高置信度结果
high_conf_boxes = [box for box in results[0].boxes if box.conf[0] > 0.5]
results[0].boxes = high_conf_boxes
annotated = results[0].plot()
```

### 类别过滤
```python
# 只显示特定类别
target_classes = ['person', 'car']
filtered_boxes = []
for box in results[0].boxes:
    cls_name = results[0].names[int(box.cls[0])]
    if cls_name in target_classes:
        filtered_boxes.append(box)
results[0].boxes = filtered_boxes
annotated = results[0].plot()
```

## 批量可视化
```python
image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = model(image_paths)
for i, result in enumerate(results):
    annotated = result.plot()
    cv2.imwrite(f'result_{i}.jpg', annotated)
```

## 实用建议
1. 先使用默认`result.plot()`满足大部分需求
2. 根据需要调整样式参数
3. 可视化帮助验证检测准确性
4. 实时应用简化可视化