# 小红书自动化发布技能（Skill）

基于 [Auto-Redbook-Skills](https://github.com/comeonzhj/Auto-Redbook-Skills) 和 [xiaohongshu-ops-skill](https://github.com/Xiangyu-CAS/xiaohongshu-ops-skill) 两个开源项目核心思路构建，遵循标准 Skill 封装格式。

---

## 目录结构

```
xiaohongshu_mcp/          ← Skill 根目录
├── SKILL.md              # 🧠 技能主文件（工作流定义，AI 读此文件理解如何操作）
├── scripts/
│   ├── publish_xhs.py    # 📦 图文发布脚本（XHSPublisher 类）
│   └── interact_xhs.py   # 🖱️ 网页互动脚本（XHSInteractor 类）
├── references/
│   ├── params.md         # 参数说明 & Cookie 获取方法
│   ├── runtime-rules.md  # 操作规范与风控约束
│   └── troubleshooting.md# 常见错误排查
├── examples/
│   └── publish_example.py# 发布调用示例
├── venv/                 # Python 虚拟环境（已含所有依赖）
└── .env                  # 🔑 配置文件（需填写 Cookie，格式见 references/params.md）
```

> **⚠️ 注意：** 所有命令须使用虚拟环境中的 Python：`.\venv\Scripts\python.exe`

---

## 一、环境配置

### 配置 Cookie（发布模块用）

1. 用 Chrome/Edge 登录小红书网页版：[www.xiaohongshu.com](https://www.xiaohongshu.com)
2. 按 `F12` 打开开发者工具 → 切到 **Network** 标签页
3. 刷新页面后点击任意请求 → 在右侧 **Headers** 中找到 `cookie` 字段
4. 复制完整的 Cookie 字符串（很长，完整复制）
5. 在本项目根目录新建 `.env` 文件，内容如下：

```env
XHS_COOKIE=a1=xxx; web_session=yyy; 其他cookie字段...
```

> **关键字段**：Cookie 中必须包含 `a1` 和 `web_session`，否则发布签名会失败。

---

## 二、发布图文笔记（publisher_v2.py）

**功能**：通过小红书官方接口直接发布图文笔记，速度极快，无需打开浏览器。

### 命令参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | ✅ | 笔记标题（不超过20字，超出自动截断） |
| `--desc` | 否 | 笔记正文内容（含话题标签等） |
| `--images` | ✅ | 图片路径，可多个，用空格分隔 |
| `--public` | 否 | 加此参数则公开发布；**不加则默认仅自己可见** |
| `--dry-run` | 否 | 仅验证 Cookie 连通性，不真实发布 |

### 使用示例

```powershell
# 1. 测试 Cookie 是否有效（不发布）
.\venv\Scripts\python.exe publisher_v2.py --dry-run --title "测试" --images test.jpg

# 2. 私密发布（仅自己可见，推荐先这样测试）
.\venv\Scripts\python.exe publisher_v2.py --title "今日好物分享" --desc "超好用推荐！#好物推荐 #生活方式" --images cover.png card1.png

# 3. 公开发布
.\venv\Scripts\python.exe publisher_v2.py --title "今日好物分享" --desc "超好用！" --images cover.png card1.png --public
```

### 在 Python 代码中调用

```python
from publisher_v2 import XHSPublisher

publisher = XHSPublisher()  # 自动从 .env 中读取 Cookie
publisher.get_self_info()   # 验证登录状态
publisher.publish_image_note(
    title="今日好物分享",
    desc="内容正文 #话题标签",
    images=["cover.png", "card1.png"],
    is_private=False  # 公开发布
)
```

---

## 三、网页互动运营（interactor.py）

**功能**：模拟真实用户在网页版小红书操作，适用于搜索浏览、评论互动等高风控场景。登录状态一次记录，后续自动复用。

### 第一步：首次登录（只需做一次）

```powershell
.\venv\Scripts\python.exe interactor.py --login
```

这将打开一个有界面的浏览器。请在浏览器中：
1. 扫码或密码登录小红书
2. 确认登录成功后，回到终端按**回车**继续

登录状态将自动保存在 `xhs_browser_data/` 目录，后续运行无需重复登录。

### 第二步：运行互动脚本

```powershell
.\venv\Scripts\python.exe interactor.py
```

默认演示模式：搜索 "自动化编程" 并打开第一个笔记详情。

### 在 Python 代码中调用

```python
import asyncio
from interactor import XHSInteractor

async def main():
    async with XHSInteractor() as bot:
        await bot.start(headless=True)  # headless=True 为无界面后台运行
        await bot.search_and_browse("好物推荐")
        await bot.add_comment("哇太好看了！请问哪里买的呀～")

asyncio.run(main())
```

---

## 四、常见问题

**Q: Cookie 多久会失效？**
A: 一般 7-30 天不等。失效后重新从浏览器提取并更新 `.env` 文件即可。

**Q: 发布报签名错误怎么办？**
A: 检查 `.env` 中的 Cookie 是否包含 `a1` 和 `web_session` 两个字段，或者 Cookie 是否已过期。

**Q: 评论框没找到 / 互动失败怎么办？**
A: 小红书前端随时可能更新 DOM 结构。可以先运行 `interactor.py --login` 用有头模式打开页面，手动查看元素，更新 `interactor.py` 中的 CSS 选择器。

**Q: 能否批量发布？**
A: 可以，在 Python 脚本中循环调用 `publisher.publish_image_note()` 即可，建议每次发布间隔 30 秒以上避免触发风控。
