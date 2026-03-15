# 参数参考

## Cookie 获取方法

1. 在浏览器中登录小红书：[www.xiaohongshu.com](https://www.xiaohongshu.com)
2. 按 `F12` → **Network** 标签 → 刷新页面
3. 点击任意请求 → 右侧 **Headers** → 找到 `cookie` 字段
4. 复制完整字符串，填入项目根目录的 `.env` 文件：

```env
XHS_COOKIE=a1=xxx; web_session=yyy; 其他字段...
```

> **必须包含**：`a1` 和 `web_session` 两个字段，否则发布签名会失败。  
> **有效期**：一般 7-30 天，失效后重新获取。

---

## publish_xhs.py 参数

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `--title` `-t` | ✅ | str | 笔记标题（超过 20 字自动截断） |
| `--desc` `-d` | 否 | str | 正文内容，支持 Emoji 和 #话题 |
| `--images` `-i` | ✅ | list | 图片路径，空格分隔，最多 18 张 |
| `--public` | 否 | flag | 公开发布（不加默认私密） |
| `--dry-run` | 否 | flag | 仅验证连接，不实际发布 |

## interact_xhs.py 参数

| 参数 | 说明 |
|------|------|
| `--login` | 打开有头浏览器，引导用户扫码完成首次登录 |

## XHSInteractor Python API

| 方法 | 说明 |
|------|------|
| `start(headless=False)` | 启动浏览器；`headless=True` 为后台模式 |
| `check_login()` | 检查当前是否已登录，返回 `bool` |
| `manual_login_wait()` | 打开页面并等待用户手动登录 |
| `search_and_browse(keyword)` | 搜索关键词并进入第一个笔记 |
| `add_comment(text)` | 在当前打开的笔记中发送评论 |
| `close()` | 关闭浏览器 |

## XHSPublisher Python API

| 方法 | 说明 |
|------|------|
| `__init__(cookie=None)` | `cookie=None` 则自动从 `.env` 读取 |
| `get_self_info()` | 获取用户信息，可用于验证 Cookie 有效性 |
| `publish_image_note(title, desc, images, is_private=True)` | 发布图文笔记 |
