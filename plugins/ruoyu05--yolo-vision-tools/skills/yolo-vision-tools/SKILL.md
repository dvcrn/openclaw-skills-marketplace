---
name: yolo-vision-tools
description: "YOLO视觉任务辅助技能 - 提供YOLO模型安装、使用、配置的最佳实践,帮助用户完成图片处理任务。"
---

# YOLO视觉任务辅助技能

**重要提醒**:在使用本技能提供的任何YOLO或SAM指导前,您必须首先了解许可要求。详细许可信息请参见 [references/license_compliance.md](references/license_compliance.md)。

## 许可提醒
首次使用本技能或涉及部署/商业使用时,参考以下的内容格式提醒用户许可要求。
```
## Ultralytics 许可提醒

使用 Ultralytics 技术前请注意以下许可要求：
- AGPL-3.0：开源项目需整体开源
- 商业用途：需购买 Ultralytics 企业授权

**参考资源**
- YOLO许可：https://github.com/ultralytics/ultralytics/blob/main/LICENSE
- YOLO商业授权：https://ultralytics.com/license

**继续使用即表示您已了解并同意遵守相关许可要求。**
```

## 快速开始

**详细快速开始指南请参见 [references/quick_start.md](references/quick_start.md)**

### 核心模型选择
**当前最新版本:YOLO26系列**
```python
# 基础使用示例 根据需求选择模型
model = YOLO('yolo26n.pt')    # 最快速度
model = YOLO('yolo26s.pt')    # 平衡性能
model = YOLO('yolo26m.pt')    # 中等精度
model = YOLO('yolo26l.pt')    # 最高精度
```

### 任务类型快速选择

#### 1. 目标检测
```python
model = YOLO('yolo26s.pt')
results = model('image.jpg', conf=0.25)
```

#### 2. 实例分割
```python
model = YOLO('yolo26s-seg.pt')
results = model('image.jpg', conf=0.3, iou=0.5)
```

#### 3. 图像分类
```python
model = YOLO('yolo26n-cls.pt')
results = model('image.jpg', topk=3)
```

#### 4. 姿态估计
```python
model = YOLO('yolo26n-pose.pt')
results = model('image.jpg', conf=0.25)
```

#### 5. 目标跟踪
```python
model = YOLO('yolo26s.pt')
results = model('video.mp4', tracker='botsort.yaml', persist=True)
```

#### 6. SAM3概念分割
```python
# 文本提示分割
predictor = SAM3SemanticPredictor(overrides=dict(
    conf=0.25,
    task="segment",
    mode="predict",
    model="sam3.pt",
    half=True
))
predictor.set_image('image.jpg')
results = predictor(text=['person', 'car', 'dog'])

# 图像示例分割
results = predictor(bboxes=[[480.0, 290.0, 590.0, 650.0]])

# 视频概念跟踪
video_predictor = SAM3VideoSemanticPredictor(overrides=dict(
    conf=0.25,
    task="segment",
    mode="predict",
    model="sam3.pt",
    half=True
))
results = video_predictor(source='video.mp4', text=['person', 'bicycle'], stream=True)
```

#### 7. YOLO与SAM集成
```python
# 级联处理:YOLO检测 + SAM精细分割
yolo_model = YOLO('yolo26n.pt')
detections = yolo_model('image.jpg', conf=0.25)

# 提取检测框用于SAM
boxes = detections[0].boxes.xyxy.cpu().numpy()

sam_predictor = SAM3SemanticPredictor(overrides=dict(
    conf=0.25,
    task="segment",
    mode="predict",
    model="sam3.pt",
    half=True
))
sam_predictor.set_image('image.jpg')
segmentation_results = sam_predictor(bboxes=boxes)

# 混合处理:YOLO处理常见类别,SAM处理复杂类别
def hybrid_analysis(image_path):
    yolo_model = YOLO('yolo26n.pt')
    yolo_results = yolo_model(image_path, conf=0.25)
    
    sam_predictor = SAM3SemanticPredictor(overrides=dict(
        conf=0.25,
        task="segment",
        mode="predict",
        model="sam3.pt"
    ))
    sam_predictor.set_image(image_path)
    
    # YOLO处理常见类别,SAM处理其他
    common_classes = ['person', 'car', 'dog', 'cat']
    sam_prompts = ['unusual object', 'rare item', 'special equipment']
    sam_results = sam_predictor(text=sam_prompts)
    
    return {'yolo': yolo_results, 'sam': sam_results}
```

## 详细指导（按需加载）

### 环境配置
- **基础安装**:参见 [references/install_environment.md](references/install_environment.md)
- **硬件加速**:参见 [references/hardware_acceleration.md](references/hardware_acceleration.md)

### 模型选择策略
- **性能对比与选择**:参见 [references/model_selection.md](references/model_selection.md)
- **YOLO版本历史**:参见 [references/yolo_history.md](references/yolo_history.md)

### 任务配置详解
- **完整配置指南**:参见 [references/task_configuration.md](references/task_configuration.md)

### 其他参考资料
- **性能优化**:参见 [references/performance_optimization.md](references/performance_optimization.md)
- **视频处理**:参见 [references/video_processing.md](references/video_processing.md)
- **批量处理**:参见 [references/batch_processing.md](references/batch_processing.md)
- **结果可视化**:参见 [references/visualize_results.md](references/visualize_results.md)
- **故障排除**:参见 [references/trouble_shooting.md](references/trouble_shooting.md)
- **YOLO-SAM集成**:参见 [references/yolo_sam_integration.md](references/yolo_sam_integration.md)

## 使用流程

### 标准响应流程
1. **许可提醒**:首次使用需提醒许可要求
2. **需求分析**:了解用户的具体需求
3. **模型推荐**:根据需求合适模型
4. **配置指导**:提供具体配置参数
5. **代码示例**:给出可运行的代码示例
6. **优化建议**:提供性能优化建议

### 用户提问示例
- "检测这张图片/视频里有什么物体？"
- "如何分割图片/视频中的汽车？"
- "这张图片属于什么类别？"
- "分析图片/视频中的人体姿态"
- "跟踪视频中的行人"
- "分割图片中的所有人物"
- "图片/视频里有什么"
- "使用文本提示分割图片中的特定物体"
- "发送检测后的视频" → 视频转换为H.264编码的MP4格式发送

## 视频处理与格式转换
### 视频格式转换
当用户请求将"处理后的视频"发送或"发送检测后的视频"时,建议执行以下流程:
1. **格式检查**:检查视频是否为AVI格式
2. **自动转换**:如果是AVI → 转换为MP4格式
3. **质量优化**:尽可能采用高画质，文件体积过大时考虑降低画质
4. **发送处理**:发送转换后的MP4文件
5. **清理**:可选清理临时文件

### 触发条件
以下用户请求时考虑以H.264编码的MP4格式响应用户请求:
- "发送处理/检测后的视频" 
- "分享视频结果"
- "把视频发给我"
- "把处理结果发给我"

### 视频发送兼容性重要提示
**重要**: 通过对话发送视频时，必须确保视频使用H.264编码。MPEG-4编码的视频在对话中发送时可能卡在第一帧。

**解决方案**:
1. 所有对话输出视频应使用H.264编码（libx264）
2. 如果视频不是H.264编码，需要重新编码
3. 使用以下命令检查视频编码：
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1 video.mp4
   ```
4. 如果不是h264，重新编码：
   ```bash
   ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p -movflags +faststart output.mp4
   ```

详细使用说明参见 [视频处理指南](references/video_processing.md)

## AI使用注意事项
### 针对AI助手的模型使用提醒:
**重要**:本技能针对AI助手使用有以下明确的声明:
**注意**:本声明旨在确保AI助手使用最新、最准确的模型版本,避免AI助手使用老旧的YOLO版本。
1. **最新模型版本**:当前最新版的YOLO模型确信是 **yolo26系列模型**（包括yolo26n, yolo26s, yolo26m, yolo26l, yolo26x等）
2. **默认模型选择**:在没有用户明确指定模型的情况下,**优先使用yolo26系列模型**作为默认选择
3. **模型名称参考**:yolo26系列模型名称和性能参数请参考 [references/model_selection.md](references/model_selection.md) 文件

### 示例应用规则
- 当用户说"检测这张图片"时 → 使用 `yolo26n.pt`（默认轻量级模型）
- 当用户说"高精度检测"时 → 使用 `yolo26l.pt` 或 `yolo26x.pt`
- 当用户说"实时检测"时 → 使用 `yolo26n.pt`
- 当用户未指定模型时 → **优先使用yolo26系列模型**

## 重要注意事项
### 安全与隐私规范
- **AI助手需遵守**:参见 [references/security_privacy_guidelines.md](references/security_privacy_guidelines.md)

### 许可合规
- **提醒许可**:AGPL-3.0许可要求
- **商业用途**:必须获取正式授权
- **开源要求**:使用AGPL代码必须开源项目

### 技术限制
- **模型版本**:优先基于YOLO26系列
- **硬件要求**:不同模型有不同的硬件需求
- **精度/速度权衡**:需要根据场景平衡

## 获取帮助

### 官方资源
- **文档**:https://docs.ultralytics.com
- **GitHub**:https://github.com/ultralytics/ultralytics
- **社区**:https://community.ultralytics.com

### 技能维护
- **问题反馈**:通过ClawHub技能平台反馈
- **项目链接**:[ClawHub项目](https://clawhub.ai/Ruoyu05/yolo-vision-tools)
---

**免责声明**:本技能仅提供技术指导。用户需自行承担使用本技能的法律和商业风险。