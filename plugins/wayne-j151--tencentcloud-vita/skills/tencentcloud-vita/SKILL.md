---
name: tencentcloud-vita
description: "腾讯云VITA图像/视频理解技能。当用户需要理解视频内容、分析图像、生成描述、提取体育赛事精彩片段、分析监控录像、理解直播流、新闻视频摘要、分析产品演示视频、进行任何视觉媒体理解任务，或设置、修改视频理解提示词 (vita prompt) 时，应使用此技能。支持单张/多张图像和单个视频URL输入，并可自定义提示信息。"
---

# 腾讯云 VITA 图像/视频理解 Skill

## 功能描述

本 Skill 基于腾讯云 **VITA 图像理解**服务，提供对图片和视频的 AI 理解能力：

| 输入类型 | 说明 | 限制 |
|----------|------|------|
| 单张图片 | 单个图片 URL + prompt | JPG/JPEG/PNG/SVG/WEBP，最大 100MB |
| 多张图片 | 多个图片 URL（按时序分析）+ prompt | 640×360 最多 100 图，448×448 最多 150 图 |
| 单个视频 | 单个视频 URL + prompt | MP4/MOV/AVI/WebM，H.264/H.265，最长 10 分钟，最大 100MB |

> 图片和视频 URL 必须**可公开访问**。推荐使用 COS 上海地域内网域名以节省流量费用：
> `<bucketname-appid>.cos-internal.ap-shanghai.tencentcos.cn`
> 
> 如果传入本地文件路径，Agent 自动上传至腾讯云 COS 并生成预签名 URL 后进行服务调用。

## 环境配置指引

### 获取 VITA API KEY

1. 登录腾讯云控制台(https://console.cloud.tencent.com/tiia/vita-service-management)-图像识别
2. 首次使用需"确认开通服务"
3. 点击"创建 API KEY"生成密钥
4. 点击"查看"复制 API KEY

### 设置环境变量

**Linux / macOS：**
```bash
export VITA_API_KEY="your_api_key_here"
```

如需持久化：
```bash
echo 'export VITA_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell)：**
```powershell
$env:VITA_API_KEY = "your_api_key_here"
```

> ⚠️ **安全提示**：请勿将 API KEY 硬编码在代码中或公开分享。

## Agent 执行指令（必读）

> ℹ️ **本节是 Agent（AI 模型）的核心执行规范。当用户明确请求对图片/视频进行理解分析时，Agent 按照以下步骤执行。**

### 🔑 通用执行规则

1. **触发条件**：用户提供了图片 URL 或视频 URL，且用户意图为视觉内容理解/分析。
2. **⛔ 禁止替代**：VITA 脚本调用失败时，**Agent 严禁自行编造分析结果**，必须返回清晰的错误说明。
3. **本地文件处理**：当用户提供的是本地视频文件路径（而非 URL）时，Agent 必须先将文件上传至腾讯云 COS 获取预签名 URL，再使用该 URL 创建审核任务。具体流程参见下方「Step 0: 本地文件处理」。

---

### 📌 设置自定义 Prompt（持久化）

**触发条件**：用户输入类似以下指令时触发：
- "设置视频理解prompt为..."
- "设置vita prompt: ..."
- "设置视频理解的提示词: ..."
- "更新vita prompt为..."
- 或其他表达「设置/更新 VITA prompt」意图的语句

**执行方式**：Agent 直接将用户指定的 prompt 内容写入以下文件（**无需调用脚本**）：

```
<SKILL_DIR>/prompt/vita_prompt.txt
```

- 如果文件不存在，则创建该文件并写入内容。
- 如果文件已存在，则覆盖写入新的 prompt 内容。
- 写入完成后，Agent 向用户确认 prompt 已保存成功，并展示保存的内容。

> ℹ️ 持久化的 prompt 将在后续所有 VITA 调用中自动生效（当用户未通过 `--prompt` 参数指定时）。

---

### 📌 基本调用

如果用户提供的是本地文件，Agent 需要先完成文件上传（Step 0），然后再执行发起API调用（Step 1）。

#### Step 0: 本地文件处理（仅当用户提供本地文件时执行）

当用户提供的输入是本地文件路径（而非 `http://` 或 `https://` 开头的 URL）时，Agent 必须先将图片或视频上传至腾讯云 COS，获取一个可访问的预签名 URL，然后将该 URL 作为 Step 1 发起API调用的输入。

**具体操作步骤：**

1. **安装腾讯云 COS 相关的 skill**（如尚未安装）：Agent 应搜索并安装腾讯云 COS 文件上传相关的 skill（如 `tencentcloud-cos-upload` 或类似名称的 skill）
2. **使用 COS skill 上传文件**：调用 COS skill 提供的上传功能，将本地视频文件上传至腾讯云 COS 存储桶
3. **获取预签名 URL**：上传成功后，通过 COS skill 生成该文件的预签名 URL（带有临时访问权限的链接）
4. **继续执行 Step 1**：使用获取到的预签名 URL 作为视频 URL，传入 `create_task.py` 创建审核任务

> ⚠️ **注意**：COS 相关的环境变量配置（如 Bucket、Region 等）由 COS skill 自行管理，请参阅对应 skill 的文档。如果用户尚未配置 COS 环境，Agent 应引导用户按照 COS skill 的指引完成配置。

#### Step 1: 发起API调用

```bash
python3 <SKILL_DIR>/scripts/main.py --image "<IMAGE_URL>" --prompt "<PROMPT>"
```

```bash
python3 <SKILL_DIR>/scripts/main.py --video "<VIDEO_URL>" --prompt "<PROMPT>"
```

---

### 📌 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--image <URL>` | 图片 URL（可多次指定，按时序排列） | - |
| `--video <URL>` | 视频 URL（与 --image 互斥） | - |
| `--prompt <TEXT>` | 分析指令/问题（优先级最高，覆盖持久化 prompt） | 持久化 prompt > `请描述这段媒体内容` |
| `--stream` | 开启流式输出 | 关闭 |
| `--temperature <float>` | 采样温度 0.0-1.0，越高越随机 | 默认 |
| `--max-tokens <int>` | 最大输出 token 数 | 默认 |
| `--stdin` | 从 stdin 读取 JSON 输入 | 关闭 |

---

### 📋 完整调用示例

```bash
# 单图片理解
python3 <SKILL_DIR>/scripts/main.py \
  --image "https://example.com/image.jpg" \
  --prompt "描述这张图片中的内容"

# 多图片时序分析
python3 <SKILL_DIR>/scripts/main.py \
  --image "https://example.com/frame1.jpg" \
  --image "https://example.com/frame2.jpg" \
  --image "https://example.com/frame3.jpg" \
  --prompt "分析这些图片中发生了什么变化"

# 视频内容理解
python3 <SKILL_DIR>/scripts/main.py \
  --video "https://example.com/video.mp4" \
  --prompt "总结这段视频的主要内容"

# 流式输出（适合长内容）
python3 <SKILL_DIR>/scripts/main.py \
  --video "https://example.com/video.mp4" \
  --prompt "详细描述视频内容" \
  --stream

# 调低 temperature 获取确定性输出
python3 <SKILL_DIR>/scripts/main.py \
  --image "https://example.com/chart.png" \
  --prompt "提取图表中的数据" \
  --temperature 0.1

# stdin JSON 模式
echo '{"media":[{"type":"video","url":"https://example.com/video.mp4"}],"prompt":"分析视频"}' \
  | python3 <SKILL_DIR>/scripts/main.py --stdin
```

---

### 📤 输出格式

**非流式输出（默认）：**
```json
{
  "result": "视频中展示了...",
  "usage": {
    "prompt_tokens": 1024,
    "completion_tokens": 256,
    "total_tokens": 1280
  }
}
```

**流式输出（--stream）：**
直接逐字输出文本内容（Server-Sent Events），无 JSON 包装。

---

### 📝 Prompt 模板推荐

根据使用场景选择合适的 prompt：

**监控视频分析：**
```
你是一个视频事件摘要专家。分析视频内容，以JSON格式输出：{"description":"一句话描述","title":"标题","object":["对象"],"event":["事件序列"]}
```

**新闻视频解读：**
```
你是专业新闻分析师，基于视频核心信息，生成：①标题（3个风格选项）②事件核心概述③关键细节④影响与延伸⑤信息来源
```

**带货商品讲解：**
```
观看带货视频，提取：商品名称、应用场景、核心卖点，并按营销阶段（时间范围、画面描述、语音内容、景别、营销意图）划分视频结构
```

**体育高光时刻：**
```
以专业体育解说视角，捕捉视频中的得分、高光、犯规、特写片段，输出：片段编号、时间范围（含关键帧）、景别、情景描述、画面文字
```

**直播质量评分：**
```
从6个维度评估直播片段：①直播间环境②主播语言③主播形象④出镜状态⑤互动引导⑥礼貌热情，每项输出是/否及判断依据
```

---

### ❌ Agent 须避免的行为

- 只打印脚本路径而不执行
- 忘记读取输出结果并返回给用户
- VITA 服务调用失败时，自行编造分析内容
- 同时指定 `--image` 和 `--video`（两者互斥）

### 💡 Prompt 优先级说明

脚本中 prompt 的使用优先级从高到低为：

1. **命令行参数 `--prompt`**：用户在调用时显式传入的 prompt，优先级最高。
2. **持久化 Prompt 文件**：`<SKILL_DIR>/prompt/vita_prompt.txt` 中保存的自定义 prompt。
3. **默认 Prompt**：内置默认值 `请描述这段媒体内容`。

> 即：如果用户未传 `--prompt`，脚本会自动尝试读取持久化文件；如果文件也不存在或为空，则使用默认值。

## 费用说明

| 计费项 | 单价 |
|--------|------|
| 输入 token | 1.2 元/百万 token |
| 输出 token | 3.5 元/百万 token |

> 默认并发为 **5**，超出会返回 429 错误。

## 核心脚本

- `scripts/main.py` — VITA 图像/视频理解，支持单图、多图、视频，流式/非流式输出

## 依赖

- Python 3.7+
- `openai`（OpenAI 兼容 SDK）

安装依赖（运行前必须手动安装）：
```bash
pip install openai
```
