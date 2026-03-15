---
name: zhihu-cli
description: "提供知乎的 CLI 工具 (pyzhihu-cli），在终端完成搜索、热榜、看问题与回答、发想法/提问/文章、点赞关注等一整套操作；用自然语言说出需求即可由 Agent 代为执行，无需记命令。"
---

# zhihu-cli 技能

## 前置条件与数据范围声明

使用本技能前请确认以下内容；**使用即表示知悉**下述行为与数据范围。

### 必需条件

- **已安装 zhihu 命令行**：系统 PATH 中可执行 `zhihu`（即已通过 `uv tool install pyzhihu-cli` / `pipx install pyzhihu-cli` / `pip install pyzhihu-cli` 之一安装）。
- **本地配置目录**：本技能会读写 **`~/.zhihu-cli/`**（Windows：`%USERPROFILE%\.zhihu-cli`），包括：
  - **`cookies.json`**：登录后保存的知乎 Cookie，仅存本地，权限 0600；Agent 会通过调用 `zhihu` 使用该文件，**不得将 Cookie 内容上传、转发或写入对话/日志**。
  - **`login_qrcode.png`**：执行 `zhihu login --qrcode` 时生成的二维码图片；Agent 在扫码登录流程中**可能读取该文件**，用于通过 OpenClaw 发送给用户（见下）。

### 可选集成与知情同意

- **OpenClaw（向外部渠道发送内容）**：在扫码登录场景下，为便于用户扫码，Agent 可能将 **`~/.zhihu-cli/login_qrcode.png`** 通过 **`openclaw message send --media ...`** 发送至用户已配置的即时通讯渠道（如 Telegram、Discord、Slack 等）。该行为**超出“仅帮用户执行 zhihu 命令”**，涉及：
  - **读取**本地二维码图片；
  - **向用户配置的外部渠道发送**该图片及说明文字。
- **使用本技能即表示知悉并同意**：若环境已配置 OpenClaw 且用户请求扫码登录，Agent 可能执行上述读取与发送；OpenClaw 的渠道与凭证由用户自行配置与管理，本技能**不声明、不持有**任何 OpenClaw 或第三方通讯凭证。
- 若用户未配置 OpenClaw 或不愿通过外部渠道接收二维码，可仅依赖终端内显示的二维码完成扫码，或使用 `zhihu login --cookie "..."` 方式登录。

### 凭证与数据流小结

| 类型 | 说明 |
|------|------|
| **zhihu 凭证** | 仅存于 `~/.zhihu-cli/cookies.json`，不要求环境变量；Agent 仅通过调用 `zhihu` 间接使用，不得泄露。 |
| **OpenClaw** | 本技能不声明其凭证；若使用 `openclaw message send`，需用户已配置 OpenClaw 及对应渠道，并知悉 Agent 会向该渠道发送二维码等内容。 |
| **数据流出** | 除上述“向用户配置的 OpenClaw 渠道发送二维码/文案”外，不向其他外部目标发送 Cookie 或登录凭证。 |

---

## 项目简介

本技能围绕 **知乎命令行工具 zhihu-cli**（PyPI 包名 `pyzhihu-cli`），让你在终端里完成知乎上的常见操作。

**能做什么**：在终端中**搜索**话题与用户、看**热榜**、浏览**问题与回答**、查看用户主页与动态、**发布**想法 / 提问 / 文章（支持富文本与图片）、**点赞**与**关注**、查看收藏与通知等，覆盖 23 个子命令，相当于把知乎核心能力搬进命令行。

- **PyPI 包名**: `pyzhihu-cli`
- **CLI 命令名**: `zhihu`
- **Python 要求**: >= 3.10

---

## Installation（安装）

### 用户安装（从 PyPI）

```bash
# 推荐方式：使用 uv（全局命令行工具）
uv tool install pyzhihu-cli

# 或使用 pipx
pipx install pyzhihu-cli

# 或使用 pip
pip install pyzhihu-cli
```

### 更新（升级）

用户询问「更新」「升级」「检查新版本」时，按当前安装方式执行对应命令升级到最新版：

```bash
# 若当初用 uv 安装
uv tool upgrade pyzhihu-cli

# 若当初用 pipx 安装
pipx upgrade pyzhihu-cli

# 若当初用 pip 安装（全局或当前环境）
pip install -U pyzhihu-cli
```

查看当前版本：`zhihu --version`。

二维码登录通过知乎 API（`POST /api/v3/account/api/login/qrcode`）获取 token 与 link，在终端用 `qrcode` 库渲染二维码，轮询 `scan_info` 直至扫码确认。

---

## Agent Rules

以下规则均以**前置条件与数据范围声明**为前提：仅在使用已安装的 `zhihu` CLI 及上述配置路径下操作；通过 OpenClaw 发送二维码时，视为用户已配置并知情。

1. **信息获取类命令说明**：使用 `--json` 输出原始 JSON 数据，获得更加详细的数据。
2. **更新提示**：当用户提出「更新 zhihu」「升级到最新版」「检查是否有新版本」等诉求时，提示其按安装方式执行升级命令（uv 用 `uv tool upgrade pyzhihu-cli`，pipx 用 `pipx upgrade pyzhihu-cli`，pip 用 `pip install -U pyzhihu-cli`）；若无法确定安装方式，可一并给出三种方式供用户选择。
3. **协助用户登录时必须检查二维码是否已发送给用户**：只要执行了 `zhihu login --qrcode`，二维码就会同时保存为图片，路径为 **`~/.zhihu-cli/login_qrcode.png`**（Windows 下为 `%USERPROFILE%\.zhihu-cli\login_qrcode.png`）。Agent 在提示用户扫码前，**必须先检查本轮登录流程中该二维码是否已经发送给用户**；若未发送，且用户环境已配置 OpenClaw 且符合前置声明中的知情同意，则**先将该图片复制到 OpenClaw 工作目录下的 media 文件夹**（若 media 不存在则先创建；路径如 `~/.openclaw/workspace/media/login_qrcode.png`），再以**该路径**执行 `openclaw message send --media <工作目录路径> ...` 发送；若未配置 OpenClaw 或用户未同意向外部渠道发送，则仅依赖终端内展示并提示用户扫码。登录成功后 CLI 会自动保存 Cookie，无需用户再操作。
4. **登录过程完整性**：
   - **不能切断登录进程**：一旦执行 `zhihu login --qrcode` 并进入扫码登录流程，Agent 不得主动中断、关闭、杀掉、替换或遗弃该登录进程。
   - **保持原进程等待完成**：在二维码已发送且等待用户扫码确认期间，必须保持该命令继续运行，直到登录成功、明确失败、超时退出，或用户明确要求停止。
   - **禁止并发重复登录**：同一轮登录流程中，不要再次启动新的 `zhihu login --qrcode` 来替代当前正在等待的登录进程，除非当前进程已经结束或用户明确要求重开。
   - **例外—用户要求重新登录**：若用户明确表示要「重新登录」「换号登录」「重新扫码」等，则**立即中断**当前正在执行的任何进程（包括正在等待扫码的登录进程），并重新发起登录流程。
5. **安全相关**：
   - **凭证仅存本地**：Cookie 仅保存在用户本机 `~/.zhihu-cli/cookies.json`（权限 0600），不得将 Cookie 或登录凭证上传、转发给任何第三方或写入对话/日志。
   - **优先扫码登录**：协助登录时优先引导用户使用 `zhihu login --qrcode`，并且在等待扫码前必须先检查二维码是否已发送；若未发送则立即用 OpenClaw 发送图片，避免在不可信渠道粘贴 Cookie。
   - **环境与退出**：提醒用户仅在可信环境中使用；在他人可接触的机器上使用后，建议执行 `zhihu logout` 清除本地登录态。

---

## Agent 使用 OpenClaw 向用户发送内容

**范围与知情**：本小节涉及**读取本地文件**（如 `~/.zhihu-cli/login_qrcode.png`）并**通过 OpenClaw 向用户配置的外部渠道发送**。仅当用户环境已配置 OpenClaw 且用户请求扫码登录时执行；用户应知悉并同意该数据流（见上文「前置条件与数据范围声明」）。

当 Agent 需要把二维码、说明文字等主动推送给用户时，应使用 `openclaw message send`。

**登录时发送二维码的强制要求**：必须先**将 `~/.zhihu-cli/login_qrcode.png` 复制到 OpenClaw 工作目录下的 `media` 文件夹**（**若 `media` 不存在则先创建**），再以**该路径**（如 `~/.openclaw/workspace/media/login_qrcode.png`）作为 `--media` 发送给用户，不得直接使用 `~/.zhihu-cli/login_qrcode.png` 作为 `--media`。OpenClaw 工作目录默认为 **`~/.openclaw/workspace`**，故 media 路径默认为 **`~/.openclaw/workspace/media`**（可通过 `~/.openclaw/openclaw.json` 或环境变量等覆盖，以当前环境为准）。

### 登录时发送二维码（必须经工作目录）

1. 确认二维码已生成：`~/.zhihu-cli/login_qrcode.png`（Windows：`%USERPROFILE%\.zhihu-cli\login_qrcode.png`）。
2. **复制到 OpenClaw 工作目录下的 `media` 文件夹**（例如 `~/.openclaw/workspace/media`）：**若 `media` 文件夹不存在则先创建**，再复制，得到新路径如 `~/.openclaw/workspace/media/login_qrcode.png`（若环境使用其他工作目录，则使用该目录下的 `media` 路径）。
   ```bash
   mkdir -p ~/.openclaw/workspace/media    # 若 media 不存在则创建
   cp ~/.zhihu-cli/login_qrcode.png ~/.openclaw/workspace/media/login_qrcode.png
   ```
   Windows 示例：先创建 media（不存在时）：`mkdir "%USERPROFILE%\.openclaw\workspace\media" 2>nul`，再复制：`copy "%USERPROFILE%\.zhihu-cli\login_qrcode.png" "%USERPROFILE%\.openclaw\workspace\media\login_qrcode.png"`（若工作目录不同则替换为目标路径）。
3. **使用 media 路径**调用 OpenClaw 发送：
   ```bash
   openclaw message send --channel <渠道> --target <目标> --media ~/.openclaw/workspace/media/login_qrcode.png --message "请用知乎 App 扫描图中二维码，并在手机上点击「确认登录」。"
   ```
4. 在对话中提示用户「二维码已发送到您的 [渠道]，请扫码并确认登录」。

### 基本用法

```bash
openclaw message send --channel <渠道> --target <目标> [--message "文本"] [--media <文件路径>]
```

- **必选**：`--target`（目标用户/频道），以及 **`--message` 或 `--media` 至少其一**。**登录二维码**必须使用**工作目录下 `media` 文件夹中的路径**作为 `--media`（见上）。
- **渠道**：若配置了多个渠道，必须用 `--channel` 指定，取值如：`whatsapp` | `telegram` | `discord` | `googlechat` | `slack` | `mattermost` | `signal` | `imessage` | `msteams`；若仅配置一个渠道则可省略。
- **目标格式**（依渠道而定）：
  - Telegram：`@username` 或 chat id
  - Discord：`channel:<id>` 或 `user:<id>`
  - Slack：`channel:<id>` 或 `user:<id>`
  - WhatsApp：E.164 或 group JID

### 典型场景

| 场景 | 命令示例 |
|------|----------|
| **发送登录二维码图片** | 若 `media` 不存在则先创建，再将 `~/.zhihu-cli/login_qrcode.png` 复制到 OpenClaw 工作目录的 `media` 文件夹（如 `~/.openclaw/workspace/media/login_qrcode.png`），再：`openclaw message send --channel telegram --target @用户 --media ~/.openclaw/workspace/media/login_qrcode.png --message "请用知乎 App 扫描图中二维码…"` |
| **仅发图片（无文案）** | `openclaw message send --channel <渠道> --target <目标> --media <工作目录或其它路径>/image.png` |
| **仅发文字** | `openclaw message send --channel <渠道> --target <目标> --message "登录成功，可以继续使用 zhihu 命令。"` |

### 可选参数

- `--account <id>`：多账号时指定账号。
- `--reply-to <message-id>`：回复某条消息（部分渠道支持）。
- `--thread-id`：Discord/Slack 线程、Telegram 论坛主题等。
- `--dry-run`：仅模拟不真实发送。
- `--verbose`：输出详细日志。
- `--json`：以 JSON 输出结果。

### 登录流程中发送二维码的推荐步骤

1. 执行 `zhihu login --qrcode` 后，确认二维码已生成到 `~/.zhihu-cli/login_qrcode.png`。
2. 若本轮尚未向用户发送过该图：
   - **复制**：先确保 `media` 存在（若不存在则创建），再复制：`mkdir -p ~/.openclaw/workspace/media && cp ~/.zhihu-cli/login_qrcode.png ~/.openclaw/workspace/media/login_qrcode.png`（或当前环境的 OpenClaw 工作目录下的 `media`）。
   - **发送**：`openclaw message send --channel <用户所在渠道> --target <用户目标> --media ~/.openclaw/workspace/media/login_qrcode.png --message "请用知乎 App 扫描图中二维码，并在手机上点击「确认登录」。"`
3. 再在对话中提示用户「二维码已发送到您的 [渠道]，请扫码并确认登录」。
4. 保持当前 `zhihu login --qrcode` 进程不中断，等待用户扫码完成。

---

## Agent 命令标准化流程

当用户提出与知乎相关的诉求时，Agent 按以下流程执行，保证行为一致、可复现。

### 1. 理解诉求并映射到命令

| 用户诉求（示例） | 需登录 | 对应命令 |
|------------------|--------|----------|
| 登录知乎 / 扫码登录 | — | `zhihu login --qrcode` |
| 重新登录 / 换号登录 / 重新扫码 | — | 立即中断当前进程，再执行 `zhihu login --qrcode` |
| 搜一下「Python」/ 查热榜 / 看某问题 | 否（部分接口可匿名） | `zhihu search "Python"` / `zhihu hot` / `zhihu question <id>` |
| 看我的资料 / 我的收藏 / 通知 / 发想法 / 点赞 / 关注 | 是 | `zhihu whoami` / `zhihu collections` / `zhihu notifications` / `zhihu pin ...` / `zhihu vote <id>` / `zhihu follow-question <id>` |
| 要原始数据 / 方便你进一步处理 | 视命令而定 | 在对应命令后加 `--json` |
| 更新 zhihu / 升级到最新版 / 检查新版本 | — | 按安装方式执行：`uv tool upgrade pyzhihu-cli` 或 `pipx upgrade pyzhihu-cli` 或 `pip install -U pyzhihu-cli`；可先 `zhihu --version` 查看当前版本 |

### 2. 判断是否需要登录

- **仅读公开内容**（搜索、热榜、问题/回答详情、用户主页等）：可先直接执行命令；若返回未登录或 403，再进入登录流程。
- **写操作或个人数据**（发想法/提问/文章、点赞、关注、whoami、收藏、通知）：**先检查登录**，未登录则先完成登录再执行。

### 3. 检查登录状态（需登录时）

```bash
zhihu status
```

- 输出为「Authenticated」：继续执行用户请求的命令。
- 输出为「Not authenticated」：进入**登录流程**（见下）。

### 4. 登录流程（用户未登录时）

1. **执行登录**：`zhihu login --qrcode`  
   二维码会保存到 **`~/.zhihu-cli/login_qrcode.png`**（Windows：`%USERPROFILE%\.zhihu-cli\login_qrcode.png`）。
2. **检查是否已发送**：确认本轮登录流程中该二维码是否已经通过 OpenClaw 发送给用户。
3. **若尚未发送**：先将 `~/.zhihu-cli/login_qrcode.png` **复制到 OpenClaw 工作目录下的 `media` 文件夹**（**若 `media` 不存在则先创建**，如 `mkdir -p ~/.openclaw/workspace/media`），再以该路径用 OpenClaw 发送（可同时发说明文字）：
   ```bash
   mkdir -p ~/.openclaw/workspace/media    # 若 media 不存在则创建
   cp ~/.zhihu-cli/login_qrcode.png ~/.openclaw/workspace/media/login_qrcode.png
   openclaw message send --channel <渠道> --target <目标> --media ~/.openclaw/workspace/media/login_qrcode.png --message "请用知乎 App 扫描图中二维码，并在手机上点击「确认登录」。"
   ```
   不能跳过复制与发送，也不能仅依赖终端展示；若已发送过则不要重复发送。
4. **提示用户**：在对话中说明「二维码已发送到您的 [渠道]，请扫码并在手机上点击「确认登录」」。
5. **保持进程**：在确认二维码已发送后，等待用户扫码；CLI 会轮询至多约 2 分钟。**不得切断当前登录进程**，也不要再启动新的 `zhihu login --qrcode`，直到成功、失败、超时或用户明确要求终止。**例外**：若用户明确要求「重新登录」「换号登录」「重新扫码」，则立即中断当前进程并重新执行本登录流程。
6. **后续**：登录完成后，再执行用户原本请求的命令（如 whoami、发想法等）。

若用户坚持用 Cookie 登录，可引导：`zhihu login --cookie "z_c0=xxx; _xsrf=yyy; ..."`（遵守安全规则，不代填、不记录 Cookie）。

### 5. 执行用户请求的命令

- 根据「诉求 → 命令」映射执行对应 `zhihu <子命令> [参数]`。
- 若用户需要**详细数据**或 Agent 需要**结构化处理**，在数据类命令后加 **`--json`**（如 `zhihu search "Python" --json`、`zhihu whoami --json`）。

### 6. 结果与错误处理

- **成功**：将终端输出或 JSON 整理成用户可读的回复（摘要、列表、链接等）。
- **未登录 / 401 / 403**：提示用户需要先登录，并进入上述登录流程。
- **超时 / 网络错误**：提示稍后重试或检查网络。
- **其他错误**：根据 CLI 报错信息简要说明原因，并建议重试或检查参数（如 ID、url_token 是否正确）。

### 7. 流程小结（简版）

```
用户诉求 → 若为「重新登录/换号/重新扫码」：立即中断当前进程 → zhihu login --qrcode → …
    → 否则：映射到 zhihu 子命令
    → 若需登录：zhihu status → 未登录则 zhihu login --qrcode
        → 若未发过二维码：复制 ~/.zhihu-cli/login_qrcode.png 到 OpenClaw 工作目录/media → openclaw message send --channel <渠道> --target <目标> --media <工作目录>/media/login_qrcode.png [--message "…"]
        → 提示用户扫码 → 保持登录进程直至完成（用户要求重新登录时则中断并重新登录）
    → 执行 zhihu <子命令> [--json]
    → 整理结果或处理错误并回复用户
```

---

## Usage（使用方法）

### 1. 登录（首次使用必须先登录）

```bash
# 方式一：二维码扫码登录（推荐，仅需 requests + qrcode）
zhihu login --qrcode
```

执行后除在终端显示二维码外，会**自动将二维码保存为图片**至 **`~/.zhihu-cli/login_qrcode.png`**。Agent 在扫码登录场景下必须先检查该图在本轮是否已通过 **OpenClaw** 发送给用户；若未发送则**先将该图复制到 OpenClaw 工作目录下的 `media` 文件夹**（若 `media` 不存在则先创建，如 `mkdir -p ~/.openclaw/workspace/media`；路径如 `~/.openclaw/workspace/media/login_qrcode.png`），再执行 `openclaw message send --channel <渠道> --target <目标> --media <工作目录>/media/login_qrcode.png`（可加 `--message "请用知乎 App 扫描图中二维码…"`），不能只依赖终端展示。登录开始后须保持原登录进程持续运行，不能中途切断。

```bash
# 方式二：手动提供 Cookie 字符串（至少包含 z_c0）
zhihu login --cookie "z_c0=xxx; _xsrf=yyy; d_c0=zzz"
```

Cookie 获取方法：在浏览器登录知乎 → F12 → Network → 任意请求 → Headers → Cookie，复制完整值。


### 2. 验证登录状态

```bash
# 离线检查（只查本地 cookie 文件）
zhihu status

# 在线验证并显示个人资料
zhihu whoami

# JSON 格式输出
zhihu whoami --json
```

### 3. 搜索

```bash
zhihu search "Python 学习"
zhihu search "机器学习" --type topic
zhihu search "张三" --type people
zhihu search "Python" --limit 20
zhihu search "Python" --json
```

### 4. 热榜

```bash
zhihu hot
zhihu hot --limit 10
zhihu hot --json
```

### 5. 问题与回答

```bash
# 查看问题详情
zhihu question 12345678

# 查看问题下的回答
zhihu answers 12345678 --limit 5

# 查看单个回答详情
zhihu answer 87654321
zhihu answer 87654321 --json
```

### 6. 用户

```bash
# 查看用户资料（URL Token = 知乎主页路径 /people/xxx 中的 xxx）
zhihu user some-url-token

# 查看用户的回答、文章
zhihu user-answers some-url-token
zhihu user-articles some-url-token

# 粉丝和关注
zhihu followers some-url-token
zhihu following some-url-token
```

### 7. 推荐与话题

```bash
zhihu feed
zhihu topic 12345678
```

### 8. 互动

```bash
# 赞同回答
zhihu vote 87654321

# 取消赞同
zhihu vote --neutral 87654321

# 关注 / 取消关注问题
zhihu follow-question 12345678
zhihu follow-question --unfollow 12345678
```

### 9. 创作

```bash
# 发布提问
zhihu ask "如何学习 Python？"

# 发布提问（带描述和话题）
zhihu ask "什么是机器学习？" -d "请详细解释" -t 19550517 -t 19551275

# 发布想法（标题 + 可选正文；正文支持 HTML 富文本，见下方说明）
zhihu pin "今天天气真好！"
zhihu pin "标题" -c "想法正文内容"

# 带图片发布（-i 可重复使用以添加多张图片）
zhihu ask "求推荐" -d "详情" -i photo.jpg
zhihu pin "标题" -c "正文" -i image1.jpg -i image2.jpg
zhihu article "标题" "内容" -i cover.jpg
```

### 10. 发布文章

```bash
# 发布文章
zhihu article "文章标题" "文章内容"

# 发布文章（带话题）
zhihu article "标题" "内容" -t 19550517
```

### 富文本（HTML）

**创作类命令的正文/内容均支持 HTML 富文本**，可用于加粗、换行、链接等：

- **提问** `ask`：`-d/--detail` 中可使用 HTML（如 `<p>...</p>`、`<strong>...</strong>`）。
- **想法** `pin`：`-c/--content` 中可使用 HTML；无图时正文会以 `<p>...</p>` 包裹后提交，带图时正文直接作为 `hybrid.html` 提交。
- **文章** `article`：第二个参数为正文，支持完整 HTML 正文。

示例：`zhihu pin "标题" -c "<p>第一段</p><p><strong>加粗</strong>与<a href=\"https://zhihu.com\">链接</a></p>"`

### 11. 其他

```bash
zhihu collections           # 收藏夹
zhihu notifications         # 通知
zhihu logout                # 退出登录
zhihu --version             # 当前版本（更新前可先查看）
zhihu -v search "Python"    # 开启调试日志
zhihu --help                # 帮助
```

**更新到最新版**：按安装方式执行 `uv tool upgrade pyzhihu-cli`、`pipx upgrade pyzhihu-cli` 或 `pip install -U pyzhihu-cli`。

### 所有命令汇总

| 分类 | 命令 | 说明 |
|------|------|------|
| 认证 | `login --qrcode` / `login --cookie "..."` | 登录 |
| 认证 | `logout` | 退出登录 |
| 认证 | `status` | 检查登录状态（离线） |
| 认证 | `whoami [--json]` | 查看个人资料 |
| 内容 | `search QUERY [--type general/people/topic] [--limit N] [--json]` | 搜索 |
| 内容 | `hot [--limit N] [--json]` | 热榜 |
| 内容 | `question ID [--json]` | 问题详情 |
| 内容 | `answers ID [--limit N] [--json]` | 问题下的回答列表 |
| 内容 | `answer ID [--json]` | 回答详情 |
| 内容 | `feed [--json]` | 推荐 Feed |
| 内容 | `topic ID [--json]` | 话题详情 |
| 用户 | `user URL_TOKEN [--json]` | 用户资料 |
| 用户 | `user-answers URL_TOKEN [--limit N] [--json]` | 用户回答 |
| 用户 | `user-articles URL_TOKEN [--limit N] [--json]` | 用户文章 |
| 用户 | `followers URL_TOKEN [--limit N] [--json]` | 粉丝列表 |
| 用户 | `following URL_TOKEN [--limit N] [--json]` | 关注列表 |
| 互动 | `vote ANSWER_ID [--neutral]` | 赞同/取消赞同 |
| 互动 | `follow-question QID [--unfollow]` | 关注/取消关注问题 |
| 创作 | `ask TITLE [-d DETAIL] [-t TOPIC_ID ...] [-i IMAGE ...]` | 发布提问（正文可 HTML 富文本） |
| 创作 | `pin TITLE [-c CONTENT] [-i IMAGE ...]` | 发布想法 |
| 创作 | `article TITLE CONTENT [-t TOPIC_ID ...] [-i IMAGE ...]` | 发布文章（正文可 HTML 富文本） |
| 其他 | `collections [--limit N] [--json]` | 收藏夹 |
| 其他 | `notifications [--limit N] [--json]` | 通知 |

> **所有数据命令均支持 `--json` 输出原始 JSON。**

---

### ZhihuClient Methods

| 方法 | 端点 | 说明 |
|------|------|------|
| `get_self_info()` | `/me` | 当前用户信息 |
| `search(keyword, ...)` | `/search_v3` | 搜索 |
| `get_hot_list(limit)` | V3 `/feed/topstory/hot-lists/total` | 热榜 |
| `get_question(id)` | `/questions/{id}` | 问题详情 |
| `get_question_answers(id, ...)` | `/questions/{id}/answers` | 问题下的回答 |
| `get_answer(id)` | `/answers/{id}` | 回答详情 |
| `get_user_profile(token)` | `/members/{token}` | 用户资料 |
| `get_user_answers(token, ...)` | `/members/{token}/answers` | 用户回答 |
| `get_user_articles(token, ...)` | `/members/{token}/articles` | 用户文章 |
| `get_followers(token, ...)` | `/members/{token}/followers` | 粉丝 |
| `get_following(token, ...)` | `/members/{token}/followees` | 关注 |
| `get_feed(...)` | V3 `/feed/topstory/recommend` | 推荐 |
| `get_topic(id)` | `/topics/{id}` | 话题 |
| `vote_up(id)` / `vote_neutral(id)` | POST `/answers/{id}/voters` | 投票 |
| `follow_question(id)` / `unfollow_question(id)` | POST/DELETE `/questions/{id}/followers` | 关注问题 |
| `create_question(title, detail, topic_ids)` | POST `/questions` | 发布提问 |
| `upload_image(file_path)` | POST `/images` + PUT OSS | 上传图片 |
| `create_pin(title, content, image_infos)` | `/content/publish`（draft + publish） | 发布想法 |
| `create_article(title, content, topic_ids)` | zhuanlan API: draft → patch → publish | 发布文章 |
| `get_collections(...)` | `/members/{token}/favlists` | 收藏夹 |
| `get_notifications(...)` | `/notifications` | 通知 |

---