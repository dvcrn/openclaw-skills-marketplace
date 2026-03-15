---
name: Meteor Master AI Bridge
description: "通过 mma-bridge 命令行工具与 Meteor Master AI 交互"
---

# MMA Bridge Skill

## 技能名称

mma-bridge

## 描述

此技能允许通过 mma-bridge CLI 工具与 Meteor Master AI （简称 MMA） 进行交互。它支持发送 API 请求以获取 Meteor Master AI 的信息。

## 前置条件

- 已安装 mma-bridge：`npm install mma-bridge -g`
- 已购买并安装 Meteor Master AI 应用：
  - Microsoft Store: https://apps.microsoft.com/detail/9pksmkz7c10n
  - Apple App Store: https://apps.apple.com/cn/app/meteor-master-ai-%E5%BF%AB%E9%80%9F%E6%89%BE%E5%87%BA%E6%B5%81%E6%98%9F/id6458742068?mt=12
- 在 Meteor Master AI 应用的设置-通用设置中启用 MMABridge（默认端口：9000）

## 基本命令

### check 命令

检查系统是否安装了 Meteor Master AI 应用。

**命令：**

```bash
mma check
```

**功能：**

- 检查 Windows 或 macOS 系统上是否安装了 Meteor Master AI
- 如果已安装，显示应用的 AppID
- 如果未安装，提供安装指引

**示例输出：**

```
[INFO] Executing check command...
[DEBUG] Checking on Windows platform...
[DEBUG] Executing command: powershell -Command "Get-StartApps | Where-Object {$_.Name -like '*Meteor Master AI*'} | Format-List"
[DEBUG] PowerShell returned result:
...
[SUCCESS] Meteor Master AI is installed, AppID: 9Pksmkz7c10n

✓ Meteor Master AI is installed
  AppID: 9Pksmkz7c10n
```

### start 命令

启动 Meteor Master AI 应用。

**命令：**

```bash
mma start
```

**功能：**

- 首先检查系统是否安装了 Meteor Master AI
- 如果已安装，启动应用
- 如果未安装，显示错误信息并退出

**示例输出：**

```
[INFO] Executing start command...
[DEBUG] Checking if Meteor Master AI is installed...
[DEBUG] Checking on Windows platform...
[DEBUG] Executing command: powershell -Command "Get-StartApps | Where-Object {$_.Name -like '*Meteor Master AI*'} | Format-List"
[DEBUG] PowerShell returned result:
...
[SUCCESS] Meteor Master AI is installed, AppID: 9Pksmkz7c10n
[DEBUG] Launching Meteor Master AI...
[DEBUG] AppID: 9Pksmkz7c10n
[DEBUG] Launching on Windows platform...
[SUCCESS] Meteor Master AI launched on Windows
[SUCCESS] Meteor Master AI launched successfully
```

### list 命令

列出所有正在运行的 Meteor Master AI 实例的端口号。

**命令：**

```bash
mma list
```

**功能：**

- 查找系统临时目录中的实例文件（路径：{temp}/MeteorMasterAI/mma-bridge-registry/），文件名中的数字包含了端口号
- 检查每个实例的健康状态（通过请求 http://127.0.0.1:{port}/health）
- 删除无响应或响应无效的实例文件
- 返回所有有效实例的端口列表，后续在调用 mma post 相关方法时，即可通过手动指定端口的形式来调用实例

**示例输出：**

```
[INFO] Executing list command...
[INFO] System temp directory: C:\Users\Username\AppData\Local\Temp
[INFO] Registry directory: C:\Users\Username\AppData\Local\Temp\MeteorMasterAI\mma-bridge-registry
[INFO] Found 3 files in registry directory
[INFO] Found 3 instance files
[INFO] Checking health for port 9000...
[INFO] Instance on port 9000 is healthy
[INFO] Checking health for port 9001...
[WARN] Instance on port 9001 is not responding: connect ECONNREFUSED 127.0.0.1:9001
[INFO] Removed invalid instance file: instance-9001.json
[INFO] Checking health for port 9002...
[INFO] Instance on port 9002 is healthy

[INFO] Valid instances:
[
  9000,
  9002
]
```

## 可用方法

### getCurrentInfo

获取 Meteor Master AI 的当前信息。

**命令：**

```bash
mma post --method getCurrentInfo
```

**可选参数：**

- `--port <数字>`: 指定 API 服务器端口（默认：9000）

**示例：**

```bash
# 使用默认端口
mma post --method getCurrentInfo

# 指定端口
mma post --method getCurrentInfo --port 9000
```

**响应格式：**

```json
{
  "success": true,
  "message": "Request completed",
  "data": {
    "uuid": "17ff364f",
    "status": "active",
    "timestamp": "2026-03-13T07:19:53.829Z"
  }
}
```

**响应字段说明：**

- `success` (布尔值): 表示请求是否成功
- `message` (字符串): 状态消息
- `data` (对象): 包含实际信息
  - `uuid` (字符串): 唯一标识符
  - `status` (字符串): 当前状态（例如："active"）
  - `timestamp` (字符串): ISO 8601 格式的时间戳

## 使用示例

### 检查应用安装状态

```bash
# 检查系统是否安装了 Meteor Master AI
mma check
```

### 启动应用

```bash
# 启动 Meteor Master AI 应用
mma start
```

### 列出运行中的实例

```bash
# 列出所有正在运行的实例
mma list
```

### 基本用法

```bash
# 使用默认端口获取当前信息
mma post --method getCurrentInfo
```

### 自定义端口

```bash
# 使用自定义端口获取当前信息
mma post --method getCurrentInfo --port 9000
```

## 错误处理

如果 API 服务器未运行或请求失败，命令将返回包含失败详细信息的错误消息。

## 注意事项

- 发送请求前确保 Meteor Master AI 正在运行
- 默认 API 端口为 9000，但可以使用 `--port` 参数更改
- 所有响应均以 JSON 格式返回，便于解析
