---
name: image_gen_coze
description: "Image Generation via Coze | 基于 Coze 的图像生成技能。Generate images using Coze workflows. 使用 Seedream 4.5 model. Handles parameter building and result parsing. 负责参数构建和结果解析。Requires coze-workflow skill. 需要 coze-workflow 技能。"
homepage: https://www.coze.cn
---

# Image Gen Coze | 图像生成技能

**English**: Image generation skill based on Coze workflow. Uses Seedream 4.5 model. **Requires**: `coze-workflow` skill (base layer).

**中文**: 基于 Coze 工作流的图像生成技能。使用 Seedream 4.5 模型。**依赖**: `coze-workflow` 技能（基础层）。

## Dependencies | 依赖关系

**Required**: | **必需**：
- `coze-workflow` v1.1.1+ - Base skill for Coze workflow execution | Coze 工作流执行的基础技能

**Architecture**: | **架构**：
- `coze-workflow` (base) → `image-gen-coze` (business layer) | `coze-workflow`（基础层）→ `image-gen-coze`（业务层）

基于 Coze 工作流的图像生成。

**模型**: Seedream 4.5  
**输入**: 单一 Prompt  
**输出**: 图片 URL  
**限制**: 30秒/次

## 配置

`~/.openclaw/skills/image_gen_coze/config.json`：

```json
{
  "workflow_id": "7613773741864550434"
}
```

依赖技能配置：`~/.openclaw/skills/coze_workflow/config.json`

## 使用方式

### 输入

```json
{
  "prompt": "一只可爱的橘猫在窗台上晒太阳，温暖的光线，写实摄影风格 --ar 1:1"
}
```

### 完整调用流程

```bash
#!/bin/bash

# 1. 读取配置
WORKFLOW_ID=$(jq -r '.workflow_id' ~/.openclaw/skills/image_gen_coze/config.json)
COZE_CONFIG=~/.openclaw/skills/coze_workflow/config.json
API_KEY=$(jq -r '.api_key' "$COZE_CONFIG")
BASE_URL=$(jq -r '.base_url // "https://api.coze.cn"' "$COZE_CONFIG")

# 2. 构建 prompt（本技能负责参数构建）
PROMPT="一只可爱的橘猫在窗台上晒太阳，温暖的光线，写实摄影风格 --ar 1:1"

# 3. 调用 coze_workflow 执行
echo "🎨 生成图片..."

result=$(curl -s -X POST "${BASE_URL}/v1/workflow/stream_run" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"workflow_id\": \"${WORKFLOW_ID}\",
    \"parameters\": {
      \"prompt\": \"${PROMPT}\"
    }
  }" | grep -E "^event: Message$" -A1 | tail -1)

# 4. 解析结果（提取 content 字段中的 output）
data=$(echo "$result" | sed 's/^data: //')
content=$(echo "$data" | jq -r '.content')
image_url=$(echo "$content" | jq -r '.output // empty')

echo "🖼️ 图片 URL: $image_url"
echo "🆔 Execute ID: $(echo "$data" | jq -r '.execute_id // empty')"

# 5. 下载并保存到 workspace（本技能负责文件管理）
if [ -n "$image_url" ]; then
  # 创建保存目录（相对于 agent workspace）
  SAVE_DIR="./generated_images"
  mkdir -p "$SAVE_DIR"
  
  # 生成文件名：时间戳_前缀.png
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  # 从 prompt 提取前10个字符作为前缀（去除特殊字符）
  PREFIX=$(echo "$PROMPT" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5]//g' | cut -c1-10)
  FILENAME="${TIMESTAMP}_${PREFIX}.png"
  FILEPATH="${SAVE_DIR}/${FILENAME}"
  
  echo "💾 下载图片..."
  curl -s -L "$image_url" -o "$FILEPATH"
  
  if [ -f "$FILEPATH" ]; then
    echo "✅ 已保存: $FILEPATH"
  else
    echo "❌ 下载失败"
  fi
fi
```

---

## 文件保存约定

生成的图片自动保存到 **agent 自身 workspace** 下：

### 保存路径

```
./generated_images/
```

**实际路径示例**:
- Agent A: `~/.openclaw/workspace-agentA/generated_images/`
- Agent B: `~/.openclaw/workspace-agentB/generated_images/`

每个 agent 独立存储，互不干扰。

### 命名规则

```
{时间戳}_{prompt前缀}.png

示例：
20260305_233045_一只可爱的橘猫.png
```

### 命名参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `TIMESTAMP` | 生成时间 `YYYYMMDD_HHMMSS` | 20260305_233045 |
| `PREFIX` | Prompt 前10字符（去除特殊符号） | 一只可爱的橘猫 |

### 自定义文件名

如需自定义文件名，修改调用脚本：

```bash
# 自定义文件名
CUSTOM_NAME="my_cat.png"
FILEPATH="${SAVE_DIR}/${CUSTOM_NAME}"

curl -s -L "$image_url" -o "$FILEPATH"
```

## 提示词写法

### 尺寸

在 prompt 末尾添加 `--ar 比例`：

| 标签 | 尺寸 |
|------|------|
| `--ar 1:1` | 1024×1024 |
| `--ar 16:9` | 1024×576 |
| `--ar 9:16` | 576×1024 |

### 风格关键词

- `写实摄影风格` - 照片级真实
- `动漫风格` - 日式动漫
- `3D渲染` - 三维立体
- `赛博朋克` - 科幻霓虹

## 速率限制

**30秒/次** - 建议实现调用间隔检查。

## 版本

- v1.1.1: 明确职责，负责参数构建和结果解析
- v1.1.0: Seedream 4.5 模型
- v1.0.0: 初始版本