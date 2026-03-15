---
name: ezviz-open-ptz-control
description: "萤石开放平台云台设备控制技能。支持设备列表查询、设备状态查询、云台控制 (PTZ)、预置点管理等功能。Use when: 需要控制萤石云台设备、调整摄像头角度、设置预置点。"
---

# Ezviz Open PTZ Control (萤石开放平台云台设备控制)

萤石开放平台云台设备控制，支持设备查询、云台控制、预置点管理等功能。

## 快速开始

安装依赖：
```bash
pip install requests
```

设置环境变量：
```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
```

**注意**: 
- 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token（有效期 7 天）
- **无配置文件**: 技能不创建或读取任何配置文件
- **Token 不持久化**: Token 仅在内存中使用，运行结束后销毁，不写入磁盘

运行：
```bash
python3 {baseDir}/scripts/main.py
```

命令行参数：
```bash
# 查询设备列表
python3 {baseDir}/scripts/main.py appKey appSecret list

# 查询设备状态
python3 {baseDir}/scripts/main.py appKey appSecret status dev1

# 查询设备能力集
python3 {baseDir}/scripts/main.py appKey appSecret capacity dev1

# 云台控制（上）
python3 {baseDir}/scripts/main.py appKey appSecret ptz_start dev1 1 0 1

# 停止云台
python3 {baseDir}/scripts/main.py appKey appSecret ptz_stop dev1 1

# 调用预置点
python3 {baseDir}/scripts/main.py appKey appSecret preset_move dev1 1 1
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken, 有效期 7 天)
       ↓
2. 执行操作 (根据命令调用对应 API)
       ↓
3. 输出结果 (JSON + 控制台)
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

**为什么这样设计**:
- 简化实现，避免跨进程缓存复杂性
- Token 获取速度快（<1 秒），对性能影响小
- 每次获取新 Token 确保权限最新

## 输出示例

```
======================================================================
Ezviz Open PTZ Controller (萤石开放平台云台设备控制)
======================================================================
[Time] 2026-03-13 20:00:00
[INFO] Command: list

======================================================================
[Step 1] Getting access token...
======================================================================
[SUCCESS] Token obtained, expires: 2026-03-20 20:00:00

======================================================================
[Step 2] Executing command...
======================================================================
[INFO] Calling API: https://open.ys7.com/api/lapp/device/list
[SUCCESS] Device list retrieved

======================================================================
RESULT
======================================================================
  Total devices:  3
  Devices:
    - dev1 (Channel: 1, Status: online)
    - dev2 (Channel: 1, Status: online)
    - dev3 (Channel: 1, Status: offline)
======================================================================
```

## 支持的命令

| 命令 | 功能 | API 文档 |
|------|------|----------|
| `list` | 查询设备列表 | https://open.ys7.com/help/680 |
| `status [dev]` | 查询设备状态 | https://open.ys7.com/help/681 |
| `capacity [dev]` | 查询设备能力集 | https://open.ys7.com/help/683 |
| `ptz_start [dev] [ch] [dir] [spd]` | 开始云台控制 | https://open.ys7.com/help/690 |
| `ptz_stop [dev] [ch]` | 停止云台控制 | https://open.ys7.com/help/691 |
| `preset_add [dev] [ch]` | 添加预置点 | https://open.ys7.com/help/692 |
| `preset_move [dev] [ch] [idx]` | 调用预置点 | https://open.ys7.com/help/694 |
| `mirror [dev] [ch] [cmd]` | 镜像翻转 | https://open.ys7.com/help/695 |

## 云台控制参数

**方向参数** (direction):
| 值 | 方向 | 值 | 方向 |
|----|------|----|------|
| `0` | 上 | `1` | 下 |
| `2` | 左 | `3` | 右 |
| `4` | 左上 | `5` | 左下 |
| `6` | 右上 | `7` | 右下 |
| `8` | 物理放大 | `9` | 物理缩小 |
| `10` | 调整近焦距 | `11` | 调整远焦距 |
| `16` | 自动控制 | | |

**速度参数** (speed):
- `0` - 慢速
- `1` - 适中（推荐）
- `2` - 快速

**镜像命令** (command):
- `0` - 上下翻转
- `1` - 左右翻转
- `2` - 中心翻转

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://open.ys7.com/help/81 |
| 设备列表 | `POST /api/lapp/device/list` | https://open.ys7.com/help/680 |
| 设备状态 | `POST /api/lapp/device/info` | https://open.ys7.com/help/681 |
| 设备能力集 | `POST /api/lapp/device/capacity` | https://open.ys7.com/help/683 |
| 云台启动 | `POST /api/lapp/device/ptz/start` | https://open.ys7.com/help/690 |
| 云台停止 | `POST /api/lapp/device/ptz/stop` | https://open.ys7.com/help/691 |
| 预置点管理 | `POST /api/lapp/device/preset/*` | https://open.ys7.com/help/692 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `open.ys7.com` | 萤石开放平台 API |

## 格式代码

**设备状态**:
- `online` - 设备在线
- `offline` - 设备离线
- `error` - 状态查询失败

**错误码**:
- `200` - 操作成功
- `10002` - accessToken 过期
- `20007` - 设备不在线
- `20008` - 设备响应超时
- `60020` - 不支持该命令 (设备不支持此功能)

## Tips

- **设备序列号**: 字母需为大写
- **Token 有效期**: 7 天（每次运行自动获取）
- **云台控制**: 需要先调用 `ptz_start` 启动，再调用 `ptz_stop` 停止
- **预置点**: 添加预置点后会自动返回预置点序号
- **设备兼容性**: 消费级设备可能不支持部分高级功能
- **v3 接口**: 部分高级功能需要使用 v3 接口

## 注意事项

⚠️ **设备支持**: 不是所有设备都支持云台控制，请先确认设备能力集

⚠️ **权限要求**: 需要设备控制权限，子账户需要 `Permission: Config`

⚠️ **操作谨慎**: 云台控制会影响摄像头角度，请谨慎操作

⚠️ **Token 安全**: Token 仅在内存中使用，不写入日志，不发送到非萤石端点

⚠️ **v3 接口特殊要求**: 所有 v3 接口必须同时在 URL 参数、请求头和表单数据中包含 accessToken 和 deviceSerial

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `open.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `open.ys7.com` (萤石) | 设备控制请求 | ✅ 必需 |
| 云台控制参数 | `open.ys7.com` (萤石) | 控制设备 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`open.ys7.com`): Token 请求、设备控制 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备控制）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 在内存中使用，不写入磁盘
- ✅ 不记录完整 API 响应
- ✅ 不跨运行缓存 Token（每次运行重新获取）
- ✅ **无配置文件**: 不创建、读取或修改任何配置文件
- ✅ **无凭据持久化**: appKey/appSecret 仅从环境变量读取，不保存到磁盘

## 使用场景

| 场景 | 命令 | 说明 |
|------|------|------|
| 📋 查看设备 | `list` | 获取所有设备列表 |
| 🔍 检查状态 | `status [dev]` | 查看设备是否在线 |
| 🎮 云台控制 | `ptz_start` / `ptz_stop` | 调整摄像头角度 |
| 📍 保存位置 | `preset_add` | 保存当前位置为预置点 |
| 🎯 调用位置 | `preset_move [idx]` | 移动到预置点 |
| 🔄 镜像翻转 | `mirror [cmd]` | 翻转摄像头画面 |
