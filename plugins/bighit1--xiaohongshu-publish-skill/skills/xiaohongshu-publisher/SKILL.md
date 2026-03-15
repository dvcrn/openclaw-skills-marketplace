---
name: xiaohongshu-publisher
description: "Xiaohongshu (RedNote/小红书) automation skill for content publishing and engagement. Publish image-text notes via the xhs API using cookies, and simulate browser interactions (search, browse, comment) via Playwright. 小红书自动发布与互动技能：通过 xhs API 直接发布图文笔记，通过 Playwright 模拟网页搜索、浏览与评论互动。"
---

# 小红书发布与运营技能

根据用户需求，自动完成小红书的内容发布或运营互动任务。

> 完整参数文档见 `references/params.md`  
> 常见错误与处理见 `references/troubleshooting.md`  
> 工作流规则与约束见 `references/runtime-rules.md`

---

## ⬇️ 安装（新环境首次运行必先执行）

`venv/` 和 `xhs_browser_data/` 不随 skill 迁移，可以即开即用。創建新环境请运行对应安装脚本：

```bash
# Linux/macOS（Openclaw 部署环境）
bash setup.sh

# Windows 本地调试
.\setup.ps1
```

安装完成后再执行后续步骤。

---

## 先决条件检查

在执行任何任务前，检查：

1. `venv/` 虚拟环境是否存在（不存在则先运行 setup.sh）。
2. `.env` 文件是否包含 `XHS_COOKIE`（发布任务必须）。
3. `xhs_browser_data/` 是否有登录数据（互动任务必须，否则先引导用户登录）。

---

## 工作流一：发布图文笔记

**触发条件**：用户提供图片路径、笔记标题和正文，要求发布到小红书。

### 第一步：验证 Cookie 有效

```bash
# Linux/macOS (Openclaw)
venv/bin/python scripts/publish_xhs.py --dry-run --title "验证" --images <任意图片路径>

# Windows
.\venv\Scripts\python.exe scripts\publish_xhs.py --dry-run --title "验证" --images <任意图片路径>
```

- 成功 → 进入第二步
- 失败 → 提示用户更新 `.env` 中的 `XHS_COOKIE`（见 `references/params.md`）

### 第二步：执行发布

```bash
# Linux/macOS （公开发布）
venv/bin/python scripts/publish_xhs.py \
  --title "笔记标题" \
  --desc "正文内容 #话题标签" \
  --images 封面.png 配图1.png \
  --public

# Windows
.\venv\Scripts\python.exe scripts\publish_xhs.py --title "笔记标题" --desc "正文" --images 封面.png --public
```

> **默认仅自己可见**，确认效果后再用 `--public` 公开。

### 第三步：确认发布结果

- 成功后终端会打印笔记 ID 和链接，汇报给用户。
- 失败则根据 `references/troubleshooting.md` 排查并上报错误原因。

---

## 工作流二：搜索与互动（评论）

**触发条件**：用户要求搜索某关键词、浏览帖子、或回复评论。

### 第一步：确认浏览器登录态

检查 `xhs_browser_data/` 是否存在。若不存在：

```bash
# Linux/macOS (Openclaw) - Openclaw 默认有头环境时使用
venv/bin/python scripts/interact_xhs.py --login

# Windows
.\venv\Scripts\python.exe scripts\interact_xhs.py --login
```

### 第二步：在 Python 代码中调用互动逻辑

```python
import asyncio
from scripts.interact_xhs import XHSInteractor

async def run():
    async with XHSInteractor() as bot:
        await bot.start(headless=True)
        # 搜索并进入第一个笔记
        await bot.search_and_browse("关键词")
        # 发表评论
        await bot.add_comment("评论内容")

asyncio.run(run())
```

> 连续评论建议每次间隔 30 秒以上。

---

## 技能资源

### 脚本
- `scripts/publish_xhs.py` — 图文发布脚本（`XHSPublisher` 类）
- `scripts/interact_xhs.py` — 网页互动脚本（`XHSInteractor` 类）

### 参考文档
- `references/params.md` — 所有参数说明与 Cookie 获取方法
- `references/runtime-rules.md` — 操作规范与风控约束
- `references/troubleshooting.md` — 常见错误排查
- `examples/publish_example.py` — 发布调用示例
