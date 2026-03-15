---
name: ezviz-device-config
description: "萤石设备配置技能。支持 9 个设备配置 API，包括布防/撤防、镜头遮蔽、全天录像、移动侦测灵敏度等。Use when: 需要远程配置萤石设备参数、修改设备布防状态、调整设备功能开关。"
---

# Ezviz Device Config (萤石设备配置)

远程配置萤石设备参数，支持 9 个配置 API。

## 快速开始

安装依赖：
```bash
pip install requests
```

设置环境变量：
```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
export EZVIZ_DEVICE_SERIAL="dev1"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"  # 通道号，默认 1
```

**注意**: 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token（每次运行自动获取）。

运行：
```bash
python3 {baseDir}/scripts/device_config.py
```

命令行参数：
```bash
# 设置布防 (isDefence=1)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_set 1

# 设置撤防 (isDefence=0)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_set 0

# 获取布防计划
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_plan_get

# 设置布防计划
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_plan_set '{"startTime":"23:00","stopTime":"07:00","period":"0,1,2,3,4,5,6","enable":1}'

# 设置镜头遮蔽 (enable=1)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 shelter_set 1

# 获取镜头遮蔽状态
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 shelter_get

# 设置移动侦测灵敏度 (0-6)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 motion_detect_sensitivity_set 5
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken, 有效期 7 天)
       ↓
2. 执行配置 (根据 configType 调用对应 API)
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

## 输出示例

```
======================================================================
Ezviz Device Config (萤石设备配置)
======================================================================
[Time] 2026-03-13 19:00:00
[INFO] Device: dev1
[INFO] Config Type: defence_set
[INFO] Value: 1

======================================================================
[Step 1] Getting access token...
======================================================================
[SUCCESS] Token obtained, expires: 2026-03-20 19:00:00

======================================================================
[Step 2] Executing config...
======================================================================
[INFO] Calling API: https://open.ys7.com/api/lapp/device/defence/set
[INFO] Device: dev1, Type: defence_set
[INFO] Value: 1
[SUCCESS] Config executed successfully!

======================================================================
CONFIG RESULT
======================================================================
  Device:     dev1
  Type:       defence_set
  Value:      1 (armed)
  Status:     success
======================================================================
```

## 支持的配置类型 (9 个 API)

| 配置类型 | 功能 | 文档 ID | API 路径 | 参数 |
|----------|------|--------|----------|------|
| `defence_set` | 设置布撤防 | 701 | `/api/lapp/device/defence/set` | isDefence: 0/1/8/16 |
| `defence_plan_get` | 获取布撤防时间计划 | 702 | `/api/lapp/device/defence/plan/get` | channelNo(可选) |
| `defence_plan_set` | 设置布撤防计划 | 703 | `/api/lapp/device/defence/plan/set` | startTime,stopTime,period,enable |
| `shelter_get` | 获取镜头遮蔽开关状态 | 706 | `/api/lapp/device/scene/switch/status` | - |
| `shelter_set` | 设置镜头遮蔽开关 | 707 | `/api/lapp/device/scene/switch/set` | enable: 0/1 |
| `fullday_record_get` | 获取全天录像开关状态 | 712 | `/api/lapp/device/fullday/record/switch/status` | - |
| `fullday_record_set` | 设置全天录像开关状态 | 713 | `/api/lapp/device/fullday/record/switch/set` | enable: 0/1 |
| `motion_detect_sensitivity_get` | 获取移动侦测灵敏度配置 | 714 | `/api/lapp/device/algorithm/config/get` | - |
| `motion_detect_sensitivity_set` | 设置移动侦测灵敏度配置 | 715 | `/api/lapp/device/algorithm/config/set` | value: 0-6 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://open.ys7.com/help/81 |
| 设置布防 | `POST /api/lapp/device/defence/set` | https://open.ys7.com/help/701 |
| 获取布防计划 | `POST /api/lapp/device/defence/plan/get` | https://open.ys7.com/help/702 |
| 镜头遮蔽 | `POST /api/lapp/device/scene/switch/set` | https://open.ys7.com/help/707 |
| 全天录像 | `POST /api/lapp/device/fullday/record/switch/set` | https://open.ys7.com/help/713 |
| 移动侦测灵敏度 | `POST /api/lapp/device/algorithm/config/set` | https://open.ys7.com/help/715 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `open.ys7.com` | 萤石开放平台 API |

## 格式代码

**布防状态值** (defence_set):
- `0` - 撤防/睡眠
- `1` - 布防 (普通 IPC)
- `8` - 在家模式 (智能设备)
- `16` - 外出模式 (智能设备)

**开关值** (enable):
- `0` - 关闭
- `1` - 开启

**布防计划参数** (defence_plan_set):
- `startTime`: 开始时间 (HH:mm 格式，如 23:20)
- `stopTime`: 结束时间 (HH:mm 格式，n00:00 表示第二天 0 点)
- `period`: 周期 (0-6 表示周一 - 周日，逗号分隔，如 "0,1,6")
- `enable`: 是否启用 (1-启用，0-不启用)

**移动侦测灵敏度** (motion_detect_sensitivity_set):
- `0-6`: 灵敏度级别 (0 最低，6 最高)

**错误码**:
- `200` - 操作成功
- `10002` - accessToken 过期
- `20007` - 设备不在线
- `20008` - 设备响应超时
- `60020` - 不支持该命令 (设备不支持此功能)

## Tips

- **设备序列号**: 字母需为大写
- **Token 有效期**: 7 天（每次运行自动获取）
- **频率限制**: 建议操作间隔 ≥2 秒
- **权限要求**: 需要设备配置权限（Permission: Config）
- **设备支持**: 不同设备支持的功能不同，请先确认设备能力集

## 注意事项

⚠️ **设备支持**: 不是所有设备都支持全部 9 个功能，请先确认设备能力

⚠️ **权限要求**: 需要设备配置权限，子账户需要 `Permission: Config`

⚠️ **操作谨慎**: 修改设备配置可能影响设备正常运行，请谨慎操作

⚠️ **Token 安全**: Token 仅在内存中使用，不写入日志，不发送到非萤石端点

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `open.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `open.ys7.com` (萤石) | 设备配置请求 | ✅ 必需 |
| 配置参数 | `open.ys7.com` (萤石) | 配置设备参数 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`open.ys7.com`): Token 请求、设备配置 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备配置）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 在内存中使用，不写入磁盘
- ✅ 不记录完整 API 响应
- ✅ 不跨运行缓存 Token（每次运行重新获取）

## 使用场景

| 场景 | 配置类型 | 说明 |
|------|----------|------|
| 🏠 离家布防 | `defence_set` = 1 | 外出时开启设备布防 |
| 🏡 回家撤防 | `defence_set` = 0 | 回家时关闭布防 |
| 📅 查询布防计划 | `defence_plan_get` | 查看布撤防时间计划 |
| 📅 设置布防计划 | `defence_plan_set` | 设置定时布撤防 |
| 🎥 隐私保护 | `shelter_set` = 1 | 开启镜头遮蔽保护隐私 |
| 📹 全天录像 | `fullday_record_set` = 1 | 开启全天录像功能 |
| 🔍 移动侦测 | `motion_detect_sensitivity_set` = 5 | 设置移动侦测灵敏度 |
