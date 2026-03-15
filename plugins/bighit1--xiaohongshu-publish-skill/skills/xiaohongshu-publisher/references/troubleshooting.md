# 常见错误排查

## 发布相关

### ❌ `No matching distribution found for xhs`
- 使用 `.\venv\Scripts\pip.exe install xhs` 单独安装。

### ❌ `ValueError: 未提供Cookie且环境变量XHS_COOKIE为空`
- 根目录缺少 `.env` 文件。请新建 `.env` 并填入内容（格式见 `references/params.md`）。

### ❌ 签名错误 / `sign failed`
1. 检查 Cookie 中是否包含 `a1` 和 `web_session` 字段。
2. Cookie 可能已过期，从浏览器重新获取。

### ❌ `FileNotFoundError: 未提供有效的图片路径`
- 确认图片路径正确，可使用绝对路径。

### ❌ 发布成功但笔记不可见
- 正常现象，新发布的笔记需要 1-5 分钟审核后才会出现在主页。

---

## 互动相关

### ❌ 浏览器打不开 / Playwright 报错
- 确认已安装 Chromium：`.\venv\Scripts\playwright.exe install chromium`

### ❌ `check_login()` 返回 False / 登录态丢失
- `xhs_browser_data/` 目录被删或 Session 过期。重新运行 `--login` 扫码登录。

### ❌ 评论框找不到 (`p.content-input` 不存在)
- 小红书可能更新了页面结构。用有头模式 (`headless=False`) 打开页面，在浏览器开发者工具中重新定位评论框的 CSS 选择器，更新 `interact_xhs.py` 中的 `add_comment()` 方法。

### ❌ 搜索结果不加载 / 网络超时
- 检查网络连通性，或适当增大 `wait_for_selector` 的 `timeout` 参数。
