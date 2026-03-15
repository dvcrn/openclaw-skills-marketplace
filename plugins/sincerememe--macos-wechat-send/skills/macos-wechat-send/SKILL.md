---
name: macos-wechat-send
description: "macos-wechat-send"
---

# wechat-send - 微信自动发送技能

## 描述

通过 AppleScript 控制微信 Mac 版自动发送消息。使用剪贴板复制粘贴方式，避免输入法影响。

**触发场景：**
- 用户要求发送微信消息
- 需要自动化微信操作
- macOS 系统 + 微信 Mac 版环境

## 环境检查

1. **系统检查** - 必须是 macOS
2. **微信检查** - 微信必须已打开并登录
3. **权限检查** - 需要辅助功能权限

```bash
# 检查微信是否运行
osascript -e 'tell application "System Events" to get name of every process' | grep -i wechat
```

## 使用方法

### 直接调用脚本

```bash
wechat-send.sh "联系人名字" "消息内容"
```

### 参数说明

| 参数 | 说明 |
|------|------|
| 联系人名字 | 微信中的联系人名字，必须完全匹配 |
| 消息内容 | 要发送的消息文本（支持特殊字符） |

## 操作流程

1. **四重激活微信窗口**
   - `open -a WeChat`
   - `tell application "WeChat" to activate`
   - `set frontmost of process "WeChat" to true`
   - `perform action "AXRaise" of window 1`

2. **搜索文件传输助手（垫脚石）**
   - 按 ESC 清除残留状态
   - Cmd+F 搜索
   - 粘贴"文件传输助手"
   - 回车打开

3. **搜索目标联系人**
   - 按 ESC 清除状态
   - Cmd+A 清空搜索框
   - Cmd+F 搜索
   - 粘贴联系人名字
   - 回车打开（输入框自动聚焦）

4. **发送消息**
   - 粘贴消息内容
   - 回车发送

## 脚本文件

- `wechat-send.py` - 主脚本
- `wechat-send.sh` - 快捷脚本

## 依赖

- Python 3
- pyautogui
- macOS AppleScript

## 常见问题

### 1. 辅助功能权限
如果提示权限不足：
```
系统设置 → 隐私与安全性 → 辅助功能
```
勾选"终端"或你使用的终端应用。

### 2. 联系人找不到
- 检查名字是否完全匹配
- 确认联系人确实存在
- 尝试使用备注名

### 3. 消息发送失败
- 确认微信已登录
- 确认网络正常
- 检查是否有多个同名联系人

## 扩展建议

未来可以扩展：
- 发送图片/文件
- 群聊支持
- 聊天记录读取
- 更多联系人匹配方式

## ⚠️ 免责声明

本工具仅供学习和个人使用。使用者应遵守：
1. 微信服务条款
2. 当地法律法规
3. 道德规范

**请勿用于骚扰、诈骗或其他非法活动。**
