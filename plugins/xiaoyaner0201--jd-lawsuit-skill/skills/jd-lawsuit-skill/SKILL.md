---
name: jd-lawsuit-skill
description: "Jd Lawsuit Skill"
---

# JD Lawsuit — 京东诉讼案件管理

> 京东内网诉讼/仲裁案件管理系统的 CLI 能力封装。运行环境为 JoyDesk 内网，通过 `joydesk_sdk.browser_fetch_json` 自动携带 Electron Cookie 认证。

## 触发词

案件、诉讼、lawsuit、案件列表、商家详情、查看明文

## 前提

- 运行在 JoyDesk 的 skillRunningAgent 中
- `joydesk_sdk` 已安装（提供 `browser_fetch_json` 和 `get_browser_page`）
- `playwrightComponent` 已挂载（商家截图能力需要）
- 用户已在 Electron 中登录京东内网

## 能力

### 1. 案件列表查询（API）

**脚本**: `scripts/case_list.py`

```bash
# 查看处理中的诉讼案件（默认）
python scripts/case_list.py

# 按状态筛选
python scripts/case_list.py --status 2          # 已生效
python scripts/case_list.py --status 3          # 执行中
python scripts/case_list.py --status 4          # 已执结

# 按类型
python scripts/case_list.py --type 11           # 仲裁案件

# 搜索
python scripts/case_list.py --plaintiff 张三
python scripts/case_list.py --defendant 京东
python scripts/case_list.py --handler 陈子豪
python scripts/case_list.py --inner-code AJ-20241126-1554399489

# 拉取全部（自动翻页）
python scripts/case_list.py --all --format table

# 分页控制
python scripts/case_list.py --page 2 --size 50
```

**输出格式**: `--format json`（默认）或 `--format table`

**核心 API**: `POST /api/v1/workbench/searchCaseList`
- ⚠️ 注意：前端实际调用的是 `searchCaseList`（自动按登录用户过滤），而非 `search`（全量数据）
- 认证方式: HttpOnly Cookie（curl 不行，必须 browser_fetch_json）
- 详细字段说明: `references/api-schema.md`

### 2. 商家详情截图（Playwright）

**脚本**: `scripts/merchant_screenshot.py`

```bash
# 基本用法 — 传入案件 ID（从 case_list 的 id 字段获取）
python scripts/merchant_screenshot.py -7896699726227267508

# 指定输出路径
python scripts/merchant_screenshot.py -7896699726227267508 --output /tmp/merchant.png

# 调整超时
python scripts/merchant_screenshot.py -7896699726227267508 --timeout 15
```

**执行流程**:
1. 导航到 `case-detail?no={case_id}` 详情页
2. 点击「查看商家详情」按钮
3. 等待弹框出现
4. 遍历点击所有「查看明文」按钮（解密手机号/地址等）
5. 对弹框区域截图保存

**注意**: 
- `case_no` 参数是 `id` 字段（长数字），不是 `innerCaseCode`
- 商家详情按钮和明文按钮的选择器可能随页面改版变化，脚本已内置多个候选选择器做容错
- 需要 playwrightComponent 已挂载

## 典型工作流

```
用户: 帮我看看处理中的案件
Agent: 调用 case_list.py → 展示列表

用户: 把第一个案件的商家信息截图给我
Agent: 从列表取 id → 调用 merchant_screenshot.py → 返回截图
```

## API 参考

详见 `references/api-schema.md`，包含：
- 完整请求/响应字段说明
- 风险等级、状态、类型枚举值
- 所有已知 API 端点清单
- 页面 URL 路由规则

## SDK API 参考

### browser_fetch_json（API 请求）
```python
from joydesk_sdk import browser_fetch_json

# 签名: browser_fetch_json(url, method="GET", headers=None, body=None, cookie_domain=None, timeout_ms=None)
# body 传 dict（SDK 内部 json.dumps），不要自己序列化
# 底层走 /api/browser-proxy/fetch，自动注入 Electron session cookie
data = browser_fetch_json(
    "https://jdlawsuit-web.jd.com/api/v1/workbench/searchCaseList",
    method="POST",
    headers={"Content-Type": "application/json"},
    body={"current": 1, "size": 10, "caseType": 1, "stageStatus": 1},
)
```

### PlaywrightBrowser（浏览器自动化）
```python
from joydesk_sdk import PlaywrightBrowser

br = PlaywrightBrowser()  # 通过 HTTP 调用后端的 playwright-component

# 打开页面（sync_cookies=True 同步 Electron cookie）
tab = br.open("https://example.com", sync_cookies=True)
tab_id = tab["browserTabId"]

# 获取 ARIA 快照（含 ref 编号）
snap = br.snapshot(tab_id)

# 通过 ref 点击/填写
br.click(tab_id, ref=42)
br.fill(tab_id, ref=15, text="搜索内容")

# 截图
br.screenshot(tab_id, save_path="/tmp/shot.png")      # 保存到文件
br.screenshot(tab_id, full_page=True)                   # 返回 base64

# 等待 DOM 稳定
br.smart_wait(tab_id, timeout=10000)

# 关闭 tab
br.close_tab(tab_id)
```

## 适配须知

- 商家详情的 DOM 结构（按钮文本、弹框选择器）可能随页面改版变化
- 脚本已内置多个候选文本做容错（查看商家详情/店铺信息/商家信息等）
- 必要时在 JoyDesk 中用 `pw_snapshot()` 查看当前页面结构，调整目标文本
