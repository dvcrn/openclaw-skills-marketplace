---
name: Pencil Component Generator
description: "从 UI 截图生成 Pencil 设计文件组件（.pen 格式）"
---

# Pencil Component Generator

从 UI 截图识别设计元素，生成可编辑的 Pencil 组件文件。

## 流程概述

```
截图 → ASCII结构分析 → 提取设计Token → 生成.pen文件
```

## 详细步骤

### 1. 分析截图
识别 UI 截图中的：
- 层级结构（容器、子元素）
- 文字内容
- 图标类型
- 颜色、间距、圆角等视觉属性

### 2. 生成 ASCII 结构图
用 ASCII 文本描述组件层级：

```
Card (卡片容器)
├── Header Row (标题行)
│   ├── Icon (图标)
│   └── Title (标题文字)
├── Divider (分隔线)
└── Content Row (内容区)
    ├── Item 1
    ├── Item 2
    └── Item 3
```

### 3. 提取设计 Token
分析截图提取精确的设计参数：

| Token | 说明 | 示例值 |
|-------|------|--------|
| 颜色 | 背景、文字、图标、边框 | `#ffffff`, `#333333` |
| 字号 | 标题、标签、数值 | `15px`, `13px`, `30px` |
| 字重 | normal, 500, 700 | `"500"`, `"700"` |
| 字体 | 中文、数字字体 | `PingFang SC`, `DIN Alternate` |
| 圆角 | 卡片圆角 | `8px` |
| 间距 | padding, gap | `[20, 24]`, `8` |

### 4. 生成 .pen 文件

#### 文件结构
```json
{
  "version": "2.6",
  "children": [...],
  "variables": {...}
}
```

#### 关键规则

1. **变量只用于颜色**
   ```json
   "fill": "$--card-bg"        // ✅ 正确
   "fontSize": "$--title-size" // ❌ 错误
   "fontSize": 15              // ✅ 正确
   ```

2. **尺寸使用硬编码数字**
   ```json
   "width": 560,
   "height": 48,
   "cornerRadius": 8,
   "gap": 8,
   "padding": [20, 24]
   ```

3. **frame 节点基本结构**
   ```json
   {
     "type": "frame",
     "id": "unique-id",
     "name": "Component Name",
     "reusable": true,          // 可复用组件设为true
     "width": 560,
     "fill": "$--card-bg",
     "cornerRadius": 8,
     "layout": "vertical",      // vertical | horizontal | none
     "gap": 8,
     "padding": [top, right, bottom, left] // 或单个值
   }
   ```

4. **text 节点结构**
   ```json
   {
     "type": "text",
     "id": "title",
     "name": "Title",
     "fill": "$--title-color",
     "content": "标题文字",
     "lineHeight": 1.5,
     "fontFamily": "PingFang SC",
     "fontSize": 15,
     "fontWeight": "500"
   }
   ```

5. **icon_font 节点结构**
   ```json
   {
     "type": "icon_font",
     "id": "icon",
     "width": 20,
     "height": 20,
     "iconFontName": "chevrons-right",  // lucide 图标名
     "iconFontFamily": "lucide",
     "fill": "$--icon-color"
   }
   ```

6. **布局属性**
   - `layout`: `"vertical"` | `"horizontal"` | `"none"`
   - `justifyContent`: `"space_between"` | `"center"` | `"flex_start"` | `"flex_end"`
   - `alignItems`: `"center"` | `"flex_start"` | `"flex_end"`
   - `width`: 数字 | `"fill_container"`

7. **variables 定义**
   ```json
   "variables": {
     "--card-bg": {
       "type": "color",
       "value": "#ffffff"
     }
   }
   ```

## 常用设计 Token 模板

```json
"variables": {
  "--card-bg": { "type": "color", "value": "#ffffff" },
  "--header-bg": { "type": "color", "value": "#fafbfc" },
  "--divider-color": { "type": "color", "value": "#f0f0f0" },
  "--icon-color": { "type": "color", "value": "#4285f4" },
  "--title-color": { "type": "color", "value": "#333333" },
  "--label-color": { "type": "color", "value": "#8c8c8c" },
  "--value-color": { "type": "color", "value": "#333333" },
  "--value-danger": { "type": "color", "value": "#fa5151" }
}
```

## 参考文件

- 目标文件: `pencil-new.pen`

## 验证清单

- [ ] 层级结构与原图一致
- [ ] 变量只用于颜色属性
- [ ] 尺寸值为硬编码数字
- [ ] 颜色值精确匹配原图
- [ ] 字体、字号、字重正确
- [ ] 间距和圆角正确
- [ ] 组件可在 Pencil 中正常显示
