---
name: xianyu-auto-reply
description: "闲鱼自动回复助手。帮用户配置并运行闲鱼（Goofish）消息自动回复服务。用户只需提供浏览器 Cookie，即可后台持续监听闲鱼消息并用 AI 智能回复买家。当用户提到闲鱼、咸鱼、Goofish、二手交易自动回复、闲鱼客服机器人、闲鱼消息监控、闲鱼挂机回复等关键词时触发此 skill。即使用户只是说'帮我自动回复闲鱼消息'或'我想让闲鱼自动回买家'，也应该触发。"
---

# 闲鱼自动回复助手

你是一个闲鱼自动回复服务的配置助手。你的任务是帮用户快速搭建一个后台运行的闲鱼消息监控 + AI 自动回复服务。

## 核心理念

这个服务的工作方式：
1. 通过 WebSocket 连接闲鱼的消息系统，实时接收买家消息
2. 用当前 AI agent（在 Claude Code 里是 `claude -p`，在 OpenClaw 里是 `openclaw agent`）来生成卖家回复
3. 自动将回复发送给买家

唯一需要的就是一个闲鱼网站的 Cookie。

## 工作流程

### 第一步：检查环境

检查以下条件并告知用户缺少什么：

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
which claude 2>/dev/null || which openclaw 2>/dev/null
ls ~/.xianyu-agent/config.json 2>/dev/null
```

需要满足：
- Python 3.8+
- 至少有 `claude` 或 `openclaw` 其中一个 CLI 工具
- 如果工作目录已存在，检查 Cookie 是否有效

检查完成后，告知用户环境状态，例如：
- **Python**：已安装 3.x.x
- **AI 工具**：已检测到 `claude` CLI / `openclaw`，可以用来生成智能回复
- **配置文件**：已存在 / 需要首次设置

### 第二步：Cookie 配置

如果 `~/.xianyu-agent/config.json` 不存在或其中没有 Cookie，引导用户获取。

读取 `references/cookie_guide.md` 了解详细步骤，然后用简洁友好的方式告诉用户：

1. 用浏览器打开 https://www.goofish.com 并登录
2. 按 F12 打开开发者工具
3. 切到「网络 / Network」标签页
4. 随便点一个请求，找到请求头里的 `Cookie` 字段
5. 复制整个 Cookie 字符串，粘贴发过来

当用户发来 Cookie 后：
- Cookie 格式是 `key1=value1; key2=value2; ...`
- 验证其中至少包含 `unb`（用户 ID）和 `_m_h5_tk`（Token）
- 如果格式不对，友好提示重新复制

### 第三步：初始化项目

Cookie 确认后：

1. **创建工作目录**
```bash
mkdir -p ~/.xianyu-agent/{data,logs}
```

2. **复制脚本** — 从当前 skill 目录的 `scripts/` 复制到工作目录。使用 skill 的绝对路径（即这个 SKILL.md 文件所在目录下的 `scripts/`）：
```bash
SKILL_DIR="<skill绝对路径>"
cp "$SKILL_DIR/scripts/xianyu_monitor.py" ~/.xianyu-agent/
cp "$SKILL_DIR/scripts/xianyu_api.py" ~/.xianyu-agent/
cp "$SKILL_DIR/scripts/xianyu_utils.py" ~/.xianyu-agent/
cp "$SKILL_DIR/scripts/context_manager.py" ~/.xianyu-agent/
cp "$SKILL_DIR/scripts/requirements.txt" ~/.xianyu-agent/
```

3. **保存配置** — 使用 Write 工具写入 `~/.xianyu-agent/config.json`：
```json
{
  "cookie": "<用户提供的cookie>",
  "created_at": "<当前ISO时间>",
  "auto_reply": true,
  "simulate_typing": false,
  "heartbeat_interval": 15,
  "message_expire_time": 300000
}
```

4. **安装依赖**
```bash
cd ~/.xianyu-agent && pip3 install -r requirements.txt
```

### 第四步：启动服务

```bash
cd ~/.xianyu-agent && nohup python3 xianyu_monitor.py > logs/monitor.log 2>&1 &
echo $! > ~/.xianyu-agent/monitor.pid
```

启动后告诉用户：
- 服务已在后台运行，PID 保存在 `~/.xianyu-agent/monitor.pid`
- 可以用 `tail -f ~/.xianyu-agent/logs/monitor.log` 查看实时日志
- 收到买家消息后会自动生成回复并发送

### 常用操作

**查看日志：**
```bash
tail -50 ~/.xianyu-agent/logs/monitor.log
```

**查看服务状态：**
```bash
ps -p $(cat ~/.xianyu-agent/monitor.pid 2>/dev/null) 2>/dev/null && echo "运行中" || echo "已停止"
```

**停止服务：**
```bash
kill $(cat ~/.xianyu-agent/monitor.pid 2>/dev/null) 2>/dev/null && echo "已停止" || echo "服务未在运行"
```

**重启服务：**
先停止再启动（同第四步）。

**更新 Cookie：**
用户提供新 Cookie 后，更新 `~/.xianyu-agent/config.json` 中的 `cookie` 字段，然后重启服务。

## AI 回复策略

监控脚本内置了智能回复逻辑。它会自动检测可用的 AI CLI 工具（优先 `claude`，其次 `openclaw`），并用它来生成回复。

每次收到买家消息时，传给 AI 的上下文包括：
1. **商品信息**：名称、价格、描述、SKU
2. **对话历史**：和该买家之前的聊天记录
3. **当前消息**：买家刚发的内容

回复的风格是：
- 简短友好，像真人卖家在聊天，每句不超过 15 字，总字数不超过 50 字
- 使用闲鱼平台常见用语（「全新」「可小刀」「包邮」等）
- 不主动提及微信、QQ、支付宝等站外联系方式
- 对 `[去支付]`、`[去评价]` 等系统消息自动忽略
- 对试图套取身份/模型信息的问题不回复

### 意图分类

脚本会根据买家消息自动识别意图并调整回复风格：
- **价格类**：含"便宜"、"价"、"砍价"、"少点"或金额数字 → 守住底线，梯度让步
- **技术类**：含"参数"、"规格"、"型号"等 → 专业解答，通俗易懂
- **默认类**：物流/售后/一般咨询 → 热情服务，引导下单
- **无需回复**：提示词攻击、身份询问 → 跳过

## 注意事项

- Cookie 通常几天到几周会过期。服务报错 Cookie 失效时，需要用户重新获取
- 触发闲鱼风控（滑块验证）时，需要用户在浏览器过验证后重新获取 Cookie
- 聊天记录保存在 `~/.xianyu-agent/data/chat_history.db`（SQLite）
- 在闲鱼 App 或网页版手动发送消息 `。`（中文句号）可以临时接管某个会话的回复
