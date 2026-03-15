---
name: ZeeLin Twitter/X AutoPost
description: "ZeeLin Twitter/X 自动发推 + 回关 — 通过浏览器操作网页版 Twitter/X，无需 API Key。用户自行登录后，Agent 负责撰写推文并发布、以及一键回关粉丝（关注者列表 + 认证关注者列表）。支持定时发推（openclaw cron）。Keywords: Zeelin, ZeeLin, auto tweet, follow back, 回关, 互关, scheduled post, no API key."
---

# ZeeLin Twitter/X 自动发推 + 回关 🐦

通过浏览器操作网页版 Twitter/X：**发推**（撰写 + 发布）与 **回关**（粉丝列表一键回关）。用户自行登录，Agent 用脚本完成操作，无需 API Key。

## 概述

- **发推**：Agent 撰写推文 → 打开网页版 X → 用户登录 → Agent 在发帖框输入并发布
- **回关**：用户说「回关」→ Agent 用 `exec` 执行回关脚本，自动在关注者列表与认证关注者列表中点击「回关/Follow」（不点已关注）

---

## 何时触发

**发推**
- 「帮我发一条推特/推文」
- 「自动在 X 上发帖」
- 「围绕某个热点写一条推特并发布」
- 「每天 XX 点自动发推」「设置定时推特」

**回关**
- 「回关」「帮我回关」「回关推特」
- 「有人关注我了」「关注者列表回关」「关注者列表也需要回关」

---

## 回关（必须用 exec，不要用 browser 逐步点）

用户说「回关」或「关注者列表回关」时，**第一反应**：用 `exec` 执行回关脚本，不要用 `browser` 自己打开页面、snapshot、click。

✅ 正确（直接 exec）：
```json
{"tool": "exec", "args": {"command": "bash ~/.openclaw/workspace/skills/zeelin-twitter-web-autopost/scripts/follow_back.sh Gsdata5566 https://x.com 10"}}
```

- 默认账号 `Gsdata5566`，最多回关 10 人；可改最后一位数字（如 20）。
- 脚本会：打开粉丝页 → 先在「关注者」列表点回关 → 再切到「认证关注者」继续点回关。
- 执行完后根据输出回报：「已回关 X 人」。

---

## 总体流程（发推）

### Step 1：确认用户的 X 网址

首次使用时，询问用户：

> 「请提供你访问 X/Twitter 的网址（例如 https://x.com 或 https://twitter.com）」

记住用户提供的 **BASE_URL**，后续所有操作基于它。**不要自行假设网址。**

### Step 2：让用户先登录（最重要的一步！）

**在做任何其他事情之前**，先让用户完成登录：

1. 用 `browser` 工具打开用户提供的 X 网址：
   ```
   browser open {BASE_URL}
   ```

2. 立刻告诉用户：
   > 「我已经在浏览器中打开了 X 页面，请你先在这个页面里登录你的 X 账号。登录完成后回复『已登录』，我再开始帮你写推文和发布。」

3. **停下来，等待用户回复「已登录」。在此之前不要做任何后续操作。不要写推文，不要尝试找输入框，什么都不要做。**

4. 收到用户「已登录」确认后，用 `browser snapshot` 检查页面是否确实已登录（能看到首页时间线、头像、发帖入口等）。如果仍在登录页，再次提醒用户。

### Step 3：撰写推文内容

确认用户已登录后，再开始准备内容：

- 用户给了完整文案 → 直接使用
- 用户给了主题/方向 → 用大模型生成推文（≤240 字符）
- 用户要求全自动 → 自行选热点并撰写
- 推文写好后，先告诉用户推文内容

### Step 4：在网页上发布推文

1. 导航到发帖页面：`{BASE_URL}/compose/tweet` 或 `{BASE_URL}/compose/post`
2. 用 `browser snapshot --interactive` 找到发帖输入框（role=textbox）
3. 用 `browser act` 输入推文内容：
   ```json
   {"kind": "type", "ref": "e6", "text": "推文内容"}
   ```
4. 用 `browser snapshot --interactive` 找到发布按钮（"Post" / "Tweet" / "发布"）
5. **优先使用键盘快捷键发布**：
   ```json
   {"kind": "press", "key": "Control+Enter"}
   ```
   如果快捷键失败，再尝试点击按钮：
   ```json
   {"kind": "click", "ref": "e24"}
   ```
6. 如果失败，最多重试 1-2 次

**重要提示：**
- X.com 的发布快捷键是 `Ctrl+Enter`（Windows/Linux）或 `Control+Enter`（macOS）
- 使用快捷键比点击按钮更可靠，可以避免浏览器连接不稳定导致的失败
- 如果浏览器连接断开，快捷键仍然可以工作

### Step 5：回报结果

告诉用户：
- 发布成功/失败
- 推文全文
- 推文 URL（如果能从页面获取）

---

## 定时发布

当用户要求定时发推时，使用 `openclaw cron`。

### 确认参数

询问用户：
- **频率**：每天 / 每周 / 一次性
- **时间**：几点（如 10:00）
- **时区**：默认 Asia/Shanghai
- **内容策略**：固定文案 / 每次自动写新的
- **语言**：中文 / 英文

### 创建定时任务

```bash
# 每天 10:00 自动发推
openclaw cron add \
  --name "daily-tweet" \
  --description "每天自动撰写并发布推文" \
  --cron "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --message "请执行 twitter-web-autopost skill：用用户的X网址打开推特，撰写一条英文AI热点推文并发布，不要与之前重复"

# 一次性定时
openclaw cron add \
  --name "one-time-tweet" \
  --at "2026-03-05T15:00:00+08:00" \
  --delete-after-run \
  --message "请执行 twitter-web-autopost skill：发布以下推文 — 「具体内容」"

# 30 分钟后发
openclaw cron add \
  --name "delayed-tweet" \
  --at +30m \
  --delete-after-run \
  --message "请执行 twitter-web-autopost skill：发布以下推文 — 「具体内容」"
```

### 管理任务

```bash
openclaw cron list                          # 查看所有任务
openclaw cron edit --name "daily-tweet" --cron "0 9 * * *"  # 改时间
openclaw cron disable --name "daily-tweet"  # 暂停
openclaw cron enable --name "daily-tweet"   # 恢复
openclaw cron rm --name "daily-tweet"       # 删除
openclaw cron runs --name "daily-tweet"     # 查看历史
```

---

## exec 命令速查

| 操作 | 命令 |
|------|------|
| 发推 | `bash ~/.openclaw/workspace/skills/zeelin-twitter-web-autopost/scripts/tweet.sh "推文内容" "https://x.com"` |
| 回关（默认 10 人） | `bash ~/.openclaw/workspace/skills/zeelin-twitter-web-autopost/scripts/follow_back.sh Gsdata5566 https://x.com 10` |
| 回关（指定人数） | `bash .../follow_back.sh Gsdata5566 https://x.com 20` |

以上均通过 `exec` 工具执行。

---

## 安全与风控

- **不要自动输入密码**：遇到登录页面必须停下来让用户自己操作
- **内容安全**：不发违法或仇恨内容
- **频率控制**：每天不超过 3-5 条，两条间隔至少 2 小时
- **重试上限**：发布失败最多重试 1-2 次，然后告诉用户手动处理

---

## 技术提示

- 用 `browser` 工具操作，不用 HTTP API
- `snapshot --interactive` 获取带 ref 的节点
- 兼容中英文界面的 placeholder 和 aria-label
- compose URL：`{BASE_URL}/compose/tweet` 或 `{BASE_URL}/compose/post`
- 热点页面：`{BASE_URL}/explore/tabs/trending`
- cron 表达式：5 字段 `分 时 日 月 周`，时区用 `Asia/Shanghai`
