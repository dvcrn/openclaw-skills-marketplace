# 可视化操作指南

**导航：** 返回 [SKILL.md](./SKILL.md)

> 技能调用后的结果可视化，包括检测结果展示、网格参考生成。

## 显示检测结果

在调用返回检测结果的技能后，进行可视化：

```bash
node scripts/visualize.mjs photo.jpg '<detection-json>'
```

**输出：** `photo-detection.png`
- 在原图上绘制bounding box
- 添加置信度和类别标签
- 颜色编码不同的类别

### 检测JSON格式

```json
[
  {
    "bbox": [x, y, width, height],
    "confidence": 0.94,
    "category": { "id": "person", "name": "人体" },
    "track_id": 1
  }
]
```

---

## 生成网格参考图

用于ROI/Tripwire的交互式坐标输入：

```bash
node scripts/show-grid.mjs photo.jpg output-grid.png
```

**输出：** `output-grid.png`
- 网格线标记列（A, B, C, ...）和行（0, 1, 2, ...）
- 每个交点标记一个点
- 便于用户指定坐标

---

## 叠加层 (Overlays)

在`visualize.mjs`输出上绘制额外的注释元素（ROI、Tripwire等）：

```bash
node scripts/visualize.mjs photo.jpg '[]' output.png \
  --overlays '[
    {"kind":"ROI","name":"entrance","points":[x1,y1,x2,y2,x3,y3,x4,y4]},
    {"kind":"TripWire","name":"door","direction":"Forward","points":[...]}
  ]'
```

### ROI叠加
```json
{
  "kind": "ROI",
  "name": "监控区域",
  "points": [x1, y1, x2, y2, x3, y3, ...]
}
```
- 绘制为蓝色多边形，半透明填充

### Tripwire叠加
```json
{
  "kind": "TripWire",
  "name": "入口绊线",
  "direction": "Forward",
  "points": [p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y]
}
```
- 主线虚线 + A-B标记虚线 + 方向箭头
- Forward=🟢 Backward=🔴 TwoWay=🔵

---

## 工作流示例

**完整的预览-验证工作流：**

```bash
# 1. 生成网格参考
node scripts/show-grid.mjs photo.jpg grid.png

# 2. 用户指定ROI顶点后，预览
ROI="[100,100,300,100,300,300,100,300]"
node scripts/visualize.mjs photo.jpg '[]' roi-preview.png \
  --overlays "[{\"kind\":\"ROI\",\"name\":\"test\",\"points\":$ROI}]"

# 3. 用户确认后调用技能
echo "{\"input0\":{\"image\":\"photo.jpg\",\"roi\":{\"kind\":\"ROI\",\"points\":$ROI}}}" | \
  node scripts/invoke.mjs ep-public-2403um2p
```

---

**提示：**
- 始终在调用前预览
- ROI和Tripwire都支持可视化验证
