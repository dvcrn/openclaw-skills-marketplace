---
name: video-generator-mcp
description: "电商视频生成技能（MCP 版）。用户提供商品标题、描述、图片，自动生成营销短视频。 当用户提到\"生成视频\"\"做视频\"\"视频生成\"\"商品视频\"\"产品视频\"\"带货视频\"时必须使用此技能。 通过 MCP tool 调用 API，不使用 exec curl。"
---

# 电商视频生成 Skill（MCP 版）

## 绝对禁止

- 绝对禁止使用 exec curl 调用 API，必须使用 MCP tool。
- 绝对禁止在未调用 API 的情况下声称"已生成"。
- 绝对禁止跳过用户确认直接提交任务。

## 前置条件

本 Skill 依赖 `video-generator` MCP server。

**安装方式（二选一）：**

方式 A — 自动安装（推荐）：
```bash
npx @lu200852/openclaw-mcp-video-generator-setup
```

方式 B — 手动配置：

在 OpenClaw config.json（`tools.mcp.servers`）中添加：
```json
{
  "video-generator": {
    "command": "npx",
    "args": ["-y", "@lu200852/openclaw-mcp-video-generator"],
    "env": {
      "VIDEO_API_BASE_URL": "https://your-api.com/v1",
      "VIDEO_API_KEY": "your_api_key"
    }
  }
}
```

配置完成后重启 OpenClaw。

## 可用 MCP Tool 列表

本 skill 使用 `video-generator` MCP server 提供的以下 tool：

| Tool 名称 | 作用 | 关键参数 |
|-----------|------|---------|
| `upload_image` | 上传图片 | file_path |
| `check_balance` | 查余额 | 无 |
| `get_pricing` | 查单价 | duration |
| `create_video_task` | 创建任务 | title, description, image_urls, video_count |
| `get_task_status` | 查任务进度 | task_id |
| `list_tasks` | 任务列表 | page, page_size, status |
| `download_video` | 下载成品 | task_id, save_dir |

## 触发条件

- 生成视频、做视频、创建视频、video、generate
- 商品视频、产品视频、带货视频、营销视频
- 下载、列表、进度、状态

## 执行流程

### 步骤 1：解析用户输入

从用户消息中提取以下参数：

| 参数 | 是否必填 | 默认值 | 说明 |
|------|---------|--------|------|
| title | 必填 | - | 商品标题 |
| description | 选填 | auto | 商品描述 |
| images | 必填 | - | 图片路径列表 |
| video_count | 选填 | 与图片数相同 | 生成视频数量 |
| duration | 选填 | 15 | 视频时长（秒） |

**提取规则：**
- **title**：匹配 `标题是「...」`、`标题："..."`，或第一段短文本名词
- **description**：标题之后、"生成"/"上传"等关键词之前的连续文本
- **images**：匹配 `~/...`、`/Users/...` 等路径；"剪贴板" → pngpaste
- **video_count**：匹配 `生成N个视频`、`N个视频`
- **duration**：匹配 `N秒`

提取后**必须展示确认摘要，等用户回复"确认"才继续**：

```text
我从你的描述中提取到以下信息，请确认：

· 商品标题：{title}
· 商品描述：{description 前30字}...
· 图片：{image_count} 张
· 生成数量：{video_count} 个视频
· 视频时长：{duration} 秒

确认无误请回复「确认」，如需修改请直接说明。
```

- 用户回复 确认/好的/ok → 进入步骤 2
- 用户回复修改内容 → 更新字段，重新展示
- 用户回复 取消 → 终止

### 步骤 2：上传图片

对每张图片调用 MCP tool：

```
tool: upload_image
args: { "file_path": "~/Desktop/shoe1.jpg" }
```

收集每次返回的 `url`，组成 `image_urls` 数组。

如果用户说"用剪贴板的图"，先 `exec pngpaste /tmp/openclaw_upload.png`，再上传 `/tmp/openclaw_upload.png`。

### 步骤 3：查余额 & 算费用

并行调用两个 tool：

```
tool: check_balance
args: {}

tool: get_pricing
args: { "duration": 15 }
```

计算：
- total_cost = unit_price × video_count
- affordable_count = floor(balance / unit_price)

### 步骤 4：展示确认 & 余额判断

展示费用摘要：

```text
· 商品标题：{title}
· 图片数量：{image_count}张
· 视频时长：{duration}秒
· 生成数量：{video_count}个

单价：{unit_price} 积分
总消耗：{total_cost} 积分
当前余额：{balance} 积分
```

**余额充足**（balance >= total_cost）→ 直接进入步骤 5

**余额不足**（balance < total_cost）→ 展示选项：

```text
⚠️ 当前余额不足，还需 {total_cost - balance} 积分。

你可以：
1️⃣ 充值后生成 {video_count} 个视频
2️⃣ 生成 {affordable_count} 个视频（当前余额最多支持{affordable_count}个）
```

- 用户选 1 → 提示充值后重新检查余额
- 用户选 2 → 调整 video_count，继续步骤 5

### 步骤 5：提交生成任务

```
tool: create_video_task
args: {
  "title": "男士防水运动鞋",
  "description": "这是专为全天候出行打造的...",
  "image_urls": ["https://cdn.example.com/img1.jpg", "https://cdn.example.com/img2.jpg"],
  "video_count": 3,
  "duration": 15
}
```

成功后展示 task_id。

### 步骤 6：查询进度

用户问"好了吗"/"进度"时：

```
tool: get_task_status
args: { "task_id": "task_12345" }
```

### 步骤 7：下载

用户说"下载"时：

```
tool: download_video
args: { "task_id": "task_12345", "save_dir": "~/Downloads" }
```

### 步骤 8：任务列表

用户说"列表"时：

```
tool: list_tasks
args: { "page": 1, "page_size": 20 }
```

## 错误处理

- `401/403`：API Key 无效或过期
- `402`：余额不足（应在步骤 4 已拦截）
- `413`：图片太大，提示压缩后重试
- `422`：缺少必填字段（检查 title 和 images）
- `429`：限流，建议 30 秒后重试
- `5xx`：服务端异常，记录 request_id 后重试

## 完整对话示例

**用户**：标题是「男士防水运动鞋」这是专为全天候出行打造的男士防水运动鞋。生成3个视频（图片 ~/Desktop/shoe1.jpg ~/Desktop/shoe2.jpg ~/Desktop/shoe3.jpg）

**Agent**：
```
我从你的描述中提取到以下信息，请确认：
· 商品标题：男士防水运动鞋
· 商品描述：这是专为全天候出行打造的男士防水运动鞋...
· 图片：3 张
· 生成数量：3 个视频
· 视频时长：15 秒
确认无误请回复「确认」。
```

**用户**：确认

**Agent**：（上传图片 → 查余额 → 展示费用 → 提交任务）
```
✅ 视频生成任务已提交！
- task_id: task_12345
- 生成数量：3 个视频
- 预计耗时：约 3 分钟
- 消耗积分：864
生成完成后说"下载"即可获取。
```
