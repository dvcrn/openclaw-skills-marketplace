---
name: ezviz-multimodal-analysis
description: "萤石多模态理解技能。通过设备抓图 + 智能体分析接口，实现对摄像头画面的 AI 理解分析。Use when: 需要对监控画面进行智能分析、场景识别、行为理解、物体检测等多模态 AI 分析任务。"
---

# Ezviz Multimodal Analysis (萤石多模态分析)

通过萤石设备抓图 + 智能体分析接口，实现对摄像头画面的多模态 AI 理解。

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 设置环境变量

```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
export EZVIZ_AGENT_ID="your_agent_id"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"              # 通道号，默认 1
export EZVIZ_ANALYSIS_TEXT="请分析这张图片"  # 分析提示词
```

**注意**: 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token（每次运行自动获取）。

### 运行

```bash
python3 {baseDir}/scripts/multimodal_analysis.py
```

命令行参数：
```bash
# 单个设备
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret dev1 1 agentId

# 多个设备（逗号分隔）
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret "dev1,dev2,dev3" 1 agentId

# 自定义分析提示词
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret dev1 1 agentId "请识别画面中的人员"
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken)
       ↓
2. 设备抓图 (accessToken + deviceSerial → picUrl)
       ↓
3. AI 分析 (agentId + picUrl → 分析结果)
       ↓
4. 输出结果 (JSON + 控制台)
```

## Token 自动获取说明

**你不需要手动获取或配置 `EZVIZ_ACCESS_TOKEN`！**

技能会自动处理 Token 的获取：

```
每次运行:
  appKey + appSecret → 调用萤石 API → 获取 accessToken (有效期 7 天)
  ↓
使用 Token 完成本次请求
  ↓
Token 在内存中使用，不保存到磁盘
```

**Token 管理特性**:
- ✅ **自动获取**: 每次运行自动调用萤石 API 获取
- ✅ **有效期 7 天**: 获取的 Token 7 天内有效
- ✅ **无需配置**: 不需要手动设置 `EZVIZ_ACCESS_TOKEN` 环境变量
- ✅ **安全**: Token 不写入日志，不保存到磁盘
- ⚠️ **注意**: 每次运行会重新获取 Token（不跨运行缓存）

## 输出示例

```
======================================================================
Ezviz Multimodal Analysis Skill (萤石多模态分析)
======================================================================
[Time] 2026-03-13 17:00:00
[INFO] Target devices: 2
       - dev1 (Channel: 1)
       - dev2 (Channel: 1)
[INFO] Agent ID: 98af3e...
[INFO] Analysis: 请分析这张图片的内容

======================================================================
[Step 1] Getting access token...
[SUCCESS] Token obtained, expires: 2026-03-20 17:00:00

======================================================================
[Step 2] Capturing and analyzing images...
======================================================================

[Device] dev1 (Channel: 1)
[SUCCESS] Image captured: https://opencapture.ys7.com/...
[SUCCESS] Analysis completed!

[Analysis Result]
{
  "场景": "办公室",
  "人员数量": 3,
  "主要物体": ["办公桌", "电脑", "椅子"]
}

======================================================================
ANALYSIS SUMMARY
======================================================================
  Total devices:  2
  Success:        2
  Failed:         0
======================================================================
```

## 多设备格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 单设备 | `dev1` | 默认通道 1 |
| 多设备 | `dev1,dev2,dev3` | 全部使用默认通道 |
| 指定通道 | `dev1:1,dev2:2` | 每个设备独立通道 |
| 混合 | `dev1,dev2:2,dev3` | 部分指定通道 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://open.ys7.com/help/81 |
| 设备抓图 | `POST /api/lapp/device/capture` | https://open.ys7.com/help/687 |
| 智能体分析 | `POST /api/service/open/intelligent/agent/engine/agent/anaylsis` | https://open.ys7.com/help/5006 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `open.ys7.com` | 萤石开放平台 API（Token、抓图） |
| `aidialoggw.ys7.com` | 萤石 AI 智能体分析接口 |

## 格式代码

**返回字段**:
- `analysis` - AI 分析结果（依赖智能体配置）
- `pic_url` - 抓拍图片 URL（有效期 2 小时）

**错误码**:
- `200` - 操作成功
- `400` - 参数错误
- `500` - 服务异常
- `10002` - accessToken 过期

## Tips

- **多设备**: 逗号分隔 `dev1,dev2,dev3`
- **指定通道**: 冒号分隔 `dev1:1,dev2:2`
- **Token 有效期**: 7 天（每次运行自动获取）
- **图片有效期**: 2 小时
- **频率限制**: 设备间自动间隔 1 秒
- **分析超时**: 默认 60 秒
- **智能体**: 从 https://open.ys7.com/console/aiAgent/aiAgent.html 获取

## 分析提示词示例

| 场景 | 提示词 |
|------|--------|
| 通用分析 | "请分析这张图片的内容" |
| 人员识别 | "请识别画面中的人员数量和位置" |
| 行为分析 | "请分析画面中人员的行为活动" |
| 安全检测 | "请检测画面中是否存在安全隐患" |
| 物体识别 | "请识别画面中的主要物体" |

## 注意事项

⚠️ **频率限制**: 萤石抓图接口建议间隔 4 秒以上，频繁调用可能触发限流（错误码 10028）

⚠️ **隐私合规**: 使用摄像头监控可能涉及隐私问题，确保符合当地法律法规

⚠️ **Token 安全**: Token 仅在内存中使用，不写入日志，不发送到非萤石端点

⚠️ **分析超时**: AI 分析可能耗时较长，默认超时 60 秒

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| 摄像头抓拍图片 | `open.ys7.com` (萤石) | AI 智能体分析 | ✅ 必需 |
| appKey/appSecret | `open.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `open.ys7.com` (萤石) | 请求抓图 | ✅ 必需 |
| 智能体 ID | `aidialoggw.ys7.com` (萤石) | AI 分析请求 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`open.ys7.com`): Token 请求、设备抓图 - 萤石官方 API
- ✅ **萤石 AI 智能体** (`aidialoggw.ys7.com`): 图片分析 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备抓图、AI 分析）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 在内存中使用，不写入磁盘
- ✅ 不记录完整 API 响应
- ✅ 图片 URL 只显示前 50 字符
- ✅ 不跨运行缓存 Token（每次运行重新获取）

## 应用场景

| 场景 | 说明 |
|------|------|
| 🏢 办公场景 | 识别人员数量、工作状态、办公环境 |
| 🏭 工厂监控 | 检测安全规范、设备状态、人员行为 |
| 🏪 零售分析 | 客流统计、货架状态、顾客行为 |
| 🏠 智能家居 | 场景识别、异常检测、家庭成员活动 |
