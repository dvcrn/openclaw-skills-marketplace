---
name: trip
description: "Trip"
---

# Trip.com (携程) 旅行助手

携程网 (Trip.com / Ctrip.com) 自动化工具，支持机票搜索、酒店搜索、订单管理和价格监控。

## 功能

- **机票搜索**: 搜索航班并比较价格
- **酒店搜索**: 搜索酒店并筛选条件
- **订单管理**: 查看历史订单
- **价格监控**: 追踪产品价格变化
- **扫码登录**: 支持 QR 码登录

## 安装

```bash
# 安装 Python 依赖（playwright 等）
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## 使用方法

### 机票搜索

```bash
trip flight <出发地> <目的地> <日期>
```

示例:
```bash
trip flight 北京 上海 2026-03-15
trip flight 上海 深圳 2026-03-20 --json
```

### 酒店搜索

```bash
trip hotel <城市> <入住日期> <离店日期>
```

示例:
```bash
trip hotel 上海 2026-03-15 2026-03-17
trip hotel 北京 2026-04-01 2026-04-03 --json
```

### 查看订单

```bash
trip order
trip order --json
```

### 价格监控

```bash
trip price <链接>
```

示例:
```bash
trip price https://www.trip.com/hotels/shanghai-hotel/12345/
```

### 扫码登录

```bash
trip login
```

## 选项

- `--headless`: 无头模式运行（不显示浏览器窗口）
- `--json`: 以 JSON 格式输出结果

## 数据存储与安全

### 存储架构
**本地数据存储位置：** `~/.openclaw/data/ecommerce/`

| 组件 | 用途 | 安全机制 |
|------|------|----------|
| **auth.db** | 登录会话信息 | AES-256 加密存储 (SQLite BLOB) |
| **ecommerce.db** | 缓存和价格历史 | 不含敏感信息 |
| **trip_profile/** | 浏览器配置文件 | Playwright 用户数据目录 |
| **~/.trip/secure/** | 加密密钥和配置 | 独立安全目录 (权限 600) |

### 隐私保护
1. **加密存储**: 所有会话数据和 cookies 使用 Fernet 加密 (AES-256)
2. **密钥管理**: 加密密钥存储在用户目录，权限 600
3. **用户同意**: 首次运行需要明确同意数据使用条款
4. **数据控制**: 支持一键清除所有个人数据
5. **透明审计**: 可查看所有存储的文件和权限

### 隐私控制命令
```bash
# 查看隐私信息（通过 ecommerce-core 框架）
python -c "from core.auth import AuthManager; print('Auth system ready')"

# 清除所有个人数据
rm -rf ~/.openclaw/data/ecommerce/ ~/.trip/
```

**安全提示：**
- 所有数据仅存储在本地，不会上传到任何服务器
- 建议仅在个人设备上使用，不要在共享设备上保存登录状态
- 加密密钥仅存储在您的设备上，请妥善保管

## 技术架构

- **代码框架**: 内置 `ecommerce_core` 模块（代码自包含，无外部模块依赖）
- **运行时依赖**: Playwright（浏览器自动化）、aiohttp、Pillow
- **数据缓存**: SQLite（本地存储）
- **浏览器**: Chromium via Playwright

## 依赖说明

**代码层面：** 本 skill 包含完整的 `ecommerce_core/` 框架代码，不依赖外部 Python 模块导入。

**运行时层面：** 需要安装以下 Python 包（见 requirements.txt）：
- `playwright>=1.40.0` - 浏览器自动化
- `aiohttp>=3.9.0` - HTTP 客户端
- `pillow>=10.0.0` - 图像处理
- `cryptography>=42.0.0` - 数据加密库 (AES-256)

## 注意事项

1. 首次使用需要运行 `playwright install chromium` 安装浏览器
2. 部分功能需要登录后才能使用
3. 建议使用 `--headless` 模式在后台运行
4. 价格监控数据保留 30 天

## 故障排除

### 无法找到元素

如果页面结构发生变化，可能需要更新 CSS 选择器。检查 Trip.com 网站的最新 HTML 结构。

### 登录问题

- 确保已安装最新版 Chrome
- 尝试删除 `~/.openclaw/data/ecommerce/trip_profile/` 目录后重试
- 检查网络连接

### 缓存问题

清除缓存:
```bash
rm ~/.openclaw/data/ecommerce/ecommerce.db
```
