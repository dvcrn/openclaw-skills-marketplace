# YOLO批量处理指南

## 核心思路
- 使用文件夹路径或文件列表进行批量处理，避免单文件循环
- 合理配置批处理参数以优化性能
- 添加错误处理和进度跟踪

## 关键代码

### 基础批量处理
```python
# 批量图像处理
model = YOLO('yolo26n.pt')
results = model('path/to/images/')  # 处理整个文件夹
results = model('path/to/images/*.jpg')  # 使用通配符
results = model(['img1.jpg', 'img2.jpg'])  # 文件列表

# 批量视频处理
results = model('path/to/videos/*.mp4', save=True)
```

### 带进度和错误处理的批量函数
```python
def batch_process(folder_path, model_name='yolo26n.pt', conf=0.25):
    """批量处理文件夹内所有图像"""
    model = YOLO(model_name)
    image_files = list(Path(folder_path).glob('*.jpg')) + list(Path(folder_path).glob('*.png'))
    
    for img_path in tqdm(image_files, desc="处理进度"):
        try:
            results = model(str(img_path), conf=conf, save=True)
        except Exception as e:
            print(f"处理 {img_path.name} 失败: {e}")
```

## 性能优化建议
1. **批处理大小**: 根据GPU内存调整batch参数
2. **多线程**: 使用多进程处理大量文件
3. **缓存**: 对重复处理的数据进行缓存
4. **格式优化**: 统一输入图像格式和尺寸

## 错误处理要点
- 捕获并记录处理失败的图像
- 提供清晰的错误信息
- 支持断点续处理功能