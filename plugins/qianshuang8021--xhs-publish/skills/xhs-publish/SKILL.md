---
name: xhs-publish
description: "小红书发布助手 — 图文/视频笔记发布。当用户要求发小红书、写小红书笔记、发布图文/视频笔记时使用。支持文案生成、封面制作、视频准备、一键发布。"
---

# 📕 小红书发布助手

核心能力：**文案创作**（标题+正文+封面图）和 **笔记发布**（图文/视频）。

---

## 一、文案创作流程

当用户要求写笔记、生成文案时，按 **标题 → 选择类型 → 正文 → 封面/视频 → 发布** 流程执行。

### 1.1 生成标题

**优先使用当前对话模型直接生成**，参考 [references/title-guide.md]({baseDir}/references/title-guide.md) 中的规范生成5个不同风格的标题。

核心要求：每个标题使用不同风格，20字以内，含1-2个emoji，禁用平台禁忌词。

**输出后询问用户**：

> 标题已生成，请选择发布类型：
> 1. **📷 图文笔记** — 封面 + 正文（最常用）
> 2. **🎬 视频笔记** — 视频 + 正文（适合教程/分享）

### 1.2 生成正文

**优先使用当前对话模型直接生成**，参考 [references/content-guide.md]({baseDir}/references/content-guide.md) 中的规范。

**图文笔记**：600-800字，自然语气，文末5-10个标签。

**视频笔记**：200-300字，简洁有力。

**输出后询问用户**：是否满意？确认后进入下一步。

### 1.3 图文笔记：生成封面图

**⚠️ 必须遵循** `xhs/cover-template.md` 中的风格规范（正方形卡通漫画风格）。

#### 询问用户选择封面图片来源

> 封面图的主题图片，你想怎么来？
> 1. **AI 自动生成** — 根据文案主题自动生成匹配的图片
> 2. **上传自己的图片** — 提供图片路径，我来帮你拼接封面

#### AI 生成方式

**继续询问 prompt 方式**：

> AI图片的提示词，你想怎么来？
> 1. **预设推荐** — 我根据你的文案主题自动生成最佳英文prompt
> 2. **自定义提示词** — 你提供想要的画面描述，我来翻译成英文prompt

**预设推荐**：参考 `xhs/cover-template.md` 中的配色方案和风格要求。

**示例**：
- 主题"工具推荐" → prompt: "卡通漫画风格,办公桌上有几个工具图标,选择困难,问号,温暖橙色"
- 主题"入门指南" → prompt: "卡通漫画风格,打开的书本,发光灯泡,学习笔记,清新蓝色"

##### 生图模型选择

**优先尝试当前对话模型**直接生图（如果支持图片生成）：
1. 生成 3:2 比例的主题图片，保存到临时文件
2. 调用 cover.sh 时传入 `__USER_IMAGE__:/tmp/xhs_ai_img.png`

**如果当前模型不支持生图**，询问用户：

> 当前模型不支持图片生成，请选择生图方式：
> 1. **当前对话模型** — 尝试使用当前模型（如果支持）
> 2. **腾讯云混元** — 需要配置 HUNYUAN_SECRET_ID 和 HUNYUAN_SECRET_KEY
> 3. **豆包** — 需要配置 DOUBAO_API_KEY
> 4. **其他方式** — 你来提供图片，我帮你拼接封面

**腾讯云混元生图**：
```bash
IMG_API_TYPE=hunyuan HUNYUAN_SECRET_ID=AKID... HUNYUAN_SECRET_KEY=... bash {baseDir}/scripts/cover.sh "标题" "prompt" [输出路径] [底色hex] [字色hex]
```

**豆包生图**：
```bash
IMG_API_TYPE=doubao DOUBAO_API_KEY=... bash {baseDir}/scripts/cover.sh "标题" "prompt" [输出路径] [底色hex] [字色hex]
```

#### 用户上传图片

```bash
bash {baseDir}/scripts/cover.sh "标题文字" "__USER_IMAGE__:/path/to/image.jpg" [输出路径] [底色hex] [字色hex]
```

### 1.4 视频笔记：准备视频文件

**⚠️ 视频笔记不需要生成封面图！** 小红书会自动从视频中截取封面。

询问用户视频来源：

> 视频笔记准备好了，请选择视频来源：
> 1. **🎬 AI 生成视频** — 用 AI 生成视频
> 2. **📁 上传本地视频** — 提供视频文件路径

#### 方式一：AI 生成视频

**先检查可用的视频生成模型**：

```bash
# 检查已配置的视频生成 API
echo "可用视频生成方式："
[ -n "$DOUBAO_API_KEY" ] && echo "1. 豆包 Seedance — 已配置"
# 添加其他视频生成模型检查...
```

**如果没有可用模型**，询问用户：

> 当前没有配置视频生成模型，请选择：
> 1. **豆包 Seedance** — 我帮你配置（需要 API Key）
> 2. **上传本地视频** — 你提供视频文件

**使用豆包 Seedance 生成视频**：

```bash
# 1. 提交视频生成任务
curl -X POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {"type": "text", "text": "A cute cartoon character... --duration 10 --watermark false"}
    ]
  }'

# 2. 轮询任务状态（每 15 秒查询一次）
curl "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}" \
  -H "Authorization: Bearer $DOUBAO_API_KEY"

# 3. 下载生成的视频
curl -o video.mp4 "{video_url}"
```

**注意事项**：
- 视频时长：5-10 秒（Seedance 不支持 15 秒以上）
- 生成时间：约 1-2 分钟

#### 方式二：上传本地视频

询问用户提供视频文件路径：

> 请提供视频文件路径（支持 mp4 格式）
> - 建议时长：10 秒以内
> - 建议大小：5MB 以内
> - 如果视频太大，我可以帮你压缩

**视频压缩**（如需要）：

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -vf "scale=640:-1" -c:a aac -b:a 64k output.mp4
```

### 1.5 发布流程

#### 图文笔记发布

询问用户是否要直接发布：

> 图文笔记准备好了，要现在发布吗？
> 1. **立即发布** — 我帮你发到小红书
> 2. **稍后发布** — 保存到本地，你手动发布

**发布方式**：调用 MCP `publish_content` 工具

```python
{
    "name": "publish_content",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "images": ["/path/to/cover.jpg"],  # 用路径，不要用 base64！
        "tags": ["标签1", "标签2"]
    }
}
```

#### 视频笔记发布

询问用户是否要直接发布：

> 视频笔记准备好了，要现在发布吗？
> 1. **立即发布** — 我帮你发到小红书
> 2. **稍后发布** — 保存到本地，你手动发布（推荐）

**⚠️ 视频发布注意事项**：
- 视频发布耗时较长（5-10 分钟），可能因网络原因超时
- 推荐凌晨网络稳定时发布，或手动在 App 发布
- MCP 调用前需设置 `ROD_DEFAULT_TIMEOUT=10m` 环境变量

**发布方式**：调用 MCP `publish_with_video` 工具

```python
{
    "name": "publish_with_video",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "video": "/path/to/video.mp4"  # 用路径，不要用 base64！
    }
}
```

### 1.6 如果选择不发布

**图文笔记**：
- 封面图片保存到 `/root/.openclaw/media/inbound/xhs_cover_标题.png`
- 标题和正文输出给用户，方便复制

**视频笔记**：
- 视频文件原位置不变
- 标题和正文输出给用户，方便复制

---

## 二、发布操作

### 2.1 前置检查

每次发布前必须先执行：

```bash
bash {baseDir}/check_env.sh
```

返回码：`0` = 正常已登录；`1` = 未安装；`2` = 未登录 → 扫码登录流程。

### 2.2 MCP 调用方式

**⚠️ 极其重要**：小红书 MCP 使用 Streamable HTTP 模式。每次调用都必须：初始化 → 获取 Session ID → 带 Session ID 调用工具。三步在同一个 exec 中执行。

**超时设置**：
| 操作类型 | 建议超时 |
|----------|----------|
| 检查登录状态、获取二维码 | 10-15 秒 |
| 搜索、获取详情、评论 | 30 秒 |
| 发布笔记 | 60-180 秒 |

```bash
MCP_URL="${XHS_MCP_URL:-http://localhost:18060/mcp}"

# 1. 初始化并获取 Session ID（15秒超时）
SESSION_ID=$(curl -s --max-time 15 -D /tmp/xhs_headers -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0"}},"id":1}' > /dev/null && grep -i 'Mcp-Session-Id' /tmp/xhs_headers | tr -d '\r' | awk '{print $2}')

# 2. 确认初始化（10秒超时）
curl -s --max-time 10 -X POST "$MCP_URL" -H "Content-Type: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' > /dev/null

# 3. 调用工具（根据操作类型设置超时）
curl -s --max-time 30 -X POST "$MCP_URL" -H "Content-Type: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"<工具名>","arguments":{<参数>}},"id":2}'
```

### 2.3 可用工具

| 工具 | 触发词 | 必填参数 |
|------|--------|----------|
| `check_login_status` | 检查登录、登录状态 | 无 |
| `get_login_qrcode` | 获取二维码、扫码登录 | 无 |
| `delete_cookies` | 退出登录、重新登录 | 无 |
| `publish_content` | 发小红书、发布笔记 | title, content, images[] |
| `publish_with_video` | 发视频、发布视频笔记 | title, content, video |

---

## 🔴 发布重要规则（强制执行！）

### ✅ 正确做法

**图片/视频必须使用服务器本地绝对路径**：

```python
# ✅ 正确 - 图文笔记
{
    "name": "publish_content",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "images": ["/root/.openclaw/media/inbound/cover.jpg"],  # 直接用路径
        "tags": ["标签1", "标签2"]
    }
}

# ✅ 正确 - 视频笔记
{
    "name": "publish_with_video",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "video": "/root/.openclaw/media/inbound/video.mp4"  # 直接用路径
    }
}
```

### ❌ 错误做法

**不要用 base64 编码**，会导致上传超时：

```python
# ❌ 错误 - 用 base64 编码
import base64
with open("cover.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# ❌ 这样会导致上传超时！
"images": [img_b64]  # 即使图片只有 9KB 也会超时
```

### 核心原则

**永远用文件路径，永远不要用 base64！**

---

## 三、登录流程

当前置检查返回 `2`（未登录）时，询问用户选择登录方式：

> 需要登录小红书，请选择登录方式：
> 1. **快捷扫码** — 直接获取二维码图片
> 2. **手动Cookie** — 直接粘贴浏览器Cookie字符串

### 方式一：快捷扫码

通过 MCP `get_login_qrcode` 工具直接获取二维码 Base64 图片。

```bash
# 调用 get_login_qrcode（参考 2.2 节 MCP 调用方式）
# 返回 Base64 图片，保存后发送给用户
echo "$BASE64_STR" | base64 -d > /tmp/xhs_qr.png
```

扫码后用 `check_login_status` 工具验证是否登录成功。

### 方式二：手动Cookie

用户提供浏览器 Cookie 字符串，转换为 JSON 保存到 `~/xiaohongshu-mcp/cookies.json`。

```python
python3 -c "
import json, sys
cookie_str = sys.argv[1].strip()
cookies = []
for pair in cookie_str.split(';'):
    if '=' not in pair: continue
    name, value = pair.split('=', 1)
    cookies.append({
        'name': name.strip(), 'value': value.strip(),
        'domain': '.xiaohongshu.com', 'path': '/',
        'httpOnly': name.strip() in ('web_session', 'id_token'),
        'secure': name.strip() in ('web_session', 'id_token')
    })
with open('$HOME/xiaohongshu-mcp/cookies.json', 'w') as f:
    json.dump(cookies, f)
print(f'✅ 已保存 {len(cookies)} 个 Cookie')
" "用户提供的cookie字符串"
```

重启 MCP 服务使 Cookie 生效：

```bash
pkill -f xiaohongshu-mcp-linux 2>/dev/null
cd ~/xiaohongshu-mcp && DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 > mcp.log 2>&1 &
```

---

## 四、安装 MCP 服务（仅首次）

当前置检查返回 `1` 时执行。

### 安装依赖

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y xvfb imagemagick zbar-tools xdotool fonts-noto-cjk

# CentOS/RHEL
sudo yum install -y xorg-x11-server-Xvfb ImageMagick zbar xdotool
```

### 启动虚拟显示

```bash
Xvfb :99 -screen 0 1920x1080x24 &
```

### 下载并启动 MCP

```bash
mkdir -p ~/xiaohongshu-mcp && cd ~/xiaohongshu-mcp
wget https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-mcp-linux-amd64.tar.gz
tar xzf xiaohongshu-mcp-linux-amd64.tar.gz
chmod +x xiaohongshu-*

# 启动服务（设置 ROD 超时为 10 分钟，避免视频发布超时）
export ROD_DEFAULT_TIMEOUT=10m
DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 -port :18060 > mcp.log 2>&1 &
```

### ⚠️ ROD_DEFAULT_TIMEOUT 环境变量

**重要**：MCP 底层使用 rod（浏览器自动化库），默认超时约 5 分钟。发布视频时容易超时。

**解决方案**：启动 MCP 前设置环境变量：

```bash
export ROD_DEFAULT_TIMEOUT=10m
```

---

## 五、注意事项

1. 标题不超过 **20 字**，正文不超过 **1000 字**
2. 小红书**不支持多设备同时登录**
3. 所有带 GUI 的进程**必须用 nohup 后台运行**

## 六、故障排查

```bash
pgrep -f xiaohongshu-mcp-linux  # MCP 是否运行
pgrep -x Xvfb                   # Xvfb 是否运行
tail -20 ~/xiaohongshu-mcp/mcp.log  # 查看 MCP 日志
lsof -i :18060                  # 检查端口
```

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `context deadline exceeded` | rod 库超时 | 设置 `ROD_DEFAULT_TIMEOUT=10m` |
| 图片上传超时 | 使用 base64 编码 | 改用图片路径 |
| 登录失效 | cookies 过期 | 重新扫码登录 |
