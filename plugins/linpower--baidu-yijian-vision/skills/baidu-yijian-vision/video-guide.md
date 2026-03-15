# 视频帧提取和处理指南

## 概述

虽然易见技能使用单个图像，视频内容需要帧提取。本指南解释如何从视频中提取帧、正确识别它们，以及将它们传递给易见技能。

## 帧提取

### 使用 FFmpeg 提取帧

```bash
# 将所有帧提取为 JPEG 图像
ffmpeg -i video.mp4 -q:v 2 frame_%04d.jpg

# 以特定帧率提取帧（例如 1 FPS）
ffmpeg -i video.mp4 -vf fps=1 frame_%04d.jpg

# 以特定时间间隔提取帧（例如每 2 秒）
ffmpeg -i video.mp4 -vf fps=1/2 frame_%04d.jpg

# 提取特定范围（从 10s 开始，提取 30s 时长）
ffmpeg -i video.mp4 -ss 10 -t 30 -vf fps=1 frame_%04d.jpg
```

**输出示例**：
```
frame_0001.jpg
frame_0002.jpg
frame_0003.jpg
...
```

## 帧识别

每帧都需要唯一标识以进行正确的跟踪和分析。使用三个标识符：

### 1. sourceId - 视频源标识符

识别帧来自哪个视频。每个视频计算一次：

```bash
# 提取视频文件的前 64KB
head -c 65536 video.mp4 > video.tmp

# 计算 MD5 哈希
md5sum video.tmp | awk '{print substr($1, 1, 16)}'
# 输出：abc123def456abcd

# 结果
sourceId = "abc123def456abcd"
```

**对来自同一视频源的所有帧使用相同的 sourceId。**

### 2. imageId - 帧标识符

每帧的唯一标识符，通常基于帧号：

```
imageId = "frame_" + 帧号
# 示例：
imageId = "frame_001"
imageId = "frame_002"
imageId = "frame_003"
```

### 3. timestamp - 帧时间戳

帧被捕获时的时间戳（从 epoch 以来的毫秒数）：

```
// 对于视频提取：
timestamp = 帧索引 * 1000 / 帧率

// 示例（假设 30 FPS 视频）：
帧 0：   timestamp = 0 * 1000 / 30 = 0
帧 1：   timestamp = 1 * 1000 / 30 ≈ 33
帧 30：  timestamp = 30 * 1000 / 30 = 1000
帧 60：  timestamp = 60 * 1000 / 30 = 2000  （2 秒）
```

**对于同步视频**：如果可用，使用实际帧捕获时间。

## 将帧传递给技能

### 图像对象格式

```json
{
  "file": "path/to/frame_001.jpg",
  "sourceId": "abc123def456abcd",
  "imageId": "frame_001",
  "timestamp": 33
}
```

**字段**：
- `file` - 帧文件的路径（必需）
- `sourceId` - 视频源标识符（可选，如果省略则自动生成）
- `imageId` - 帧标识符（可选）
- `timestamp` - 帧时间戳，单位毫秒（可选）

### 自动 ID 生成

如果未提供，ID 会自动生成：

```javascript
// 如果未提供 sourceId：
sourceId = MD5(文件的前 64KB) → 16 字符十六进制

// 如果未提供 imageId：
imageId = "img_" + 随机ID

// 如果未提供 timestamp：
timestamp = Date.now()
```

## 使用示例

### 示例 1：提取并处理单个帧

```bash
# 提取帧 0
ffmpeg -i video.mp4 -vf "fps=1,select='eq(n\,0)'" frame_single.jpg

# 计算 sourceId
sourceId=$(head -c 65536 video.mp4 | md5sum | awk '{print substr($1, 1, 16)}')

# 使用易见技能处理
echo "{
  \"input0\": {
    \"image\": {
      \"file\": \"frame_single.jpg\",
      \"sourceId\": \"$sourceId\",
      \"imageId\": \"frame_0\",
      \"timestamp\": 0
    }
  }
}" | node invoke.mjs ep-public-2403um2p
```

### 示例 2：批处理帧

```bash
#!/bin/bash

VIDEO="video.mp4"
OUTPUT_DIR="frames"
FPS=30

# 获取视频信息
frame_rate=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate \
  -of default=noprint_wrappers=1:nokey=1:noesc=1 "$VIDEO")

# 提取帧
ffmpeg -i "$VIDEO" -vf "fps=$FPS" "$OUTPUT_DIR/frame_%04d.jpg"

# 计算 sourceId
sourceId=$(head -c 65536 "$VIDEO" | md5sum | awk '{print substr($1, 1, 16)}')

# 处理每个帧
for frame in "$OUTPUT_DIR"/frame_*.jpg; do
  frame_num=$(echo "$frame" | grep -oE "[0-9]+" | head -1)
  timestamp=$((frame_num * 1000 / FPS))
  imageId="frame_$(printf '%04d' "$frame_num")"

  echo "处理 $imageId (时间戳：${timestamp}ms)"

  echo "{
    \"input0\": {
      \"image\": {
        \"file\": \"$frame\",
        \"sourceId\": \"$sourceId\",
        \"imageId\": \"$imageId\",
        \"timestamp\": $timestamp
      }
    }
  }" | node invoke.mjs ep-public-2403um2p
done
```

### 示例 3：跟踪帧间的对象

对于时间分析，使用一致的 sourceId 和 imageId：

```bash
# 来自同一视频的所有帧获得相同的 sourceId
# 每帧获得唯一的 imageId

# 帧 0
{
  "file": "frame_0001.jpg",
  "sourceId": "abc123def456abcd",
  "imageId": "frame_001",
  "timestamp": 0
}

# 帧 1
{
  "file": "frame_0002.jpg",
  "sourceId": "abc123def456abcd",  # 相同的 sourceId（相同视频）
  "imageId": "frame_002",           # 不同的 imageId（不同帧）
  "timestamp": 33
}

# 技能现在可以使用 sourceId + imageId 跟踪帧间的对象
```

## 最佳实践

### 1. 帧率选择

- **实时处理**（10-30 FPS）：平滑跟踪，更高精度
- **关键帧仅**（1 FPS）：快速处理，检测重大变化
- **高速分析**（60+ FPS）：详细的运动分析

```bash
# 10 FPS 用于典型监视
ffmpeg -i video.mp4 -vf fps=10 frame_%04d.jpg

# 1 FPS 用于场景检测
ffmpeg -i video.mp4 -vf fps=1 frame_%04d.jpg

# 30 FPS 用于平滑跟踪
ffmpeg -i video.mp4 -vf fps=30 frame_%04d.jpg
```

### 2. 图像质量

在文件大小和检测精度之间平衡：

```bash
# 高质量（大文件，更慢）
ffmpeg -i video.mp4 -q:v 2 frame_%04d.jpg

# 中等质量（均衡）
ffmpeg -i video.mp4 -q:v 5 frame_%04d.jpg

# 较低质量（较小文件，更快）
ffmpeg -i video.mp4 -q:v 8 frame_%04d.jpg
```

### 3. 一致的 sourceId

始终从同一源文件重新计算 sourceId：

```bash
# ✅ 好的：所有帧的 sourceId 相同
ffmpeg -i video.mp4 frame_%04d.jpg
sourceId=$(head -c 65536 video.mp4 | md5sum | awk '{print substr($1, 1, 16)}')
# 对所有提取的帧使用相同的 sourceId

# ❌ 错误：同一视频的不同 sourceId
# 重新编码或修改视频会改变 sourceId
ffmpeg -i video.mp4 -c:v libx264 video_new.mp4
# 现在 sourceId 不同 - 破坏跟踪
```

### 4. 时间戳精度

确保时间戳与帧提取匹配：

```bash
# 如果使用 fps=30（每 1/30 秒提取）
timestamp = 帧索引 * 1000 / 30

# 如果使用 fps=1（每 1 秒提取）
timestamp = 帧索引 * 1000 / 1

# 如果使用特定时间间隔（例如每 2 秒）
# fps=1/2
timestamp = 帧索引 * 1000 / 0.5  # = 帧索引 * 2000
```

## 存储和组织

### 目录结构

```
project/
├── videos/
│   ├── surveillance_cam_001.mp4
│   └── surveillance_cam_002.mp4
├── frames/
│   ├── cam_001/
│   │   ├── sourceId_abc123def456abcd.txt  # 存储 sourceId
│   │   ├── frame_0001.jpg
│   │   ├── frame_0002.jpg
│   │   └── ...
│   └── cam_002/
│       ├── sourceId_xyz789abc123def.txt
│       ├── frame_0001.jpg
│       └── ...
└── results/
    ├── cam_001_detections.json
    └── cam_002_detections.json
```

### 存储 sourceId 参考

```bash
# 计算 sourceId 后，保存它
sourceId=$(head -c 65536 video.mp4 | md5sum | awk '{print substr($1, 1, 16)}')
echo "$sourceId" > frames/cam_001/sourceId.txt

# 稍后，检索它
sourceId=$(cat frames/cam_001/sourceId.txt)
```

## 故障排除

**"帧间的跟踪 ID 改变"**
- 确保 sourceId 一致
- 检查每帧的 imageId 是否唯一
- 验证帧提取没有跳过帧

**"时间戳似乎不对"**
- 重新计算：`timestamp = 帧索引 * 1000 / 帧率`
- 检查帧率是否准确
- 验证帧索引与文件名匹配

**"重新提取后 sourceId 不匹配"**
- 不要重新编码视频
- 如果视频被修改，重新计算 sourceId
- 使用相同的 FFmpeg 命令提取帧

**"帧顺序混乱"**
- 确保 frame_%04d 命名格式保持顺序
- 处理前按名称排序文件
- 检查是否有缺失的帧

## 参考

- [类型定义](./types-guide.md) - 图像类型规范
- [SKILL.md](./SKILL.md) - 主技能指南
- FFmpeg 文档：https://ffmpeg.org/documentation.html
