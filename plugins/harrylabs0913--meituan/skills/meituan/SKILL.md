---
name: meituan
description: "Meituan"
---

# Meituan (美团) Skill

美团外卖和本地服务平台 CLI 工具，支持餐厅搜索、红包查询和订单管理。

## 功能

- **餐厅搜索**: 搜索附近餐厅，查看评分、销量、配送信息
- **红包查询**: 查看可用优惠券和红包
- **订单管理**: 查看历史订单
- **扫码登录**: 支持 QR 码登录

## 安装

```bash
# 安装依赖
pip install playwright

# 安装浏览器
playwright install chromium
```

## 使用方法

### 搜索餐厅

```bash
meituan food <关键词> [--location <城市>] [--limit <数量>]
```

示例:
```bash
meituan food 火锅
meituan food 烧烤 --location 北京 --limit 20
meituan food 日料 --location 上海 --json
```

### 扫码登录

```bash
meituan login
```

### 查看红包

```bash
meituan redpacket
meituan redpacket --json
```

### 查看订单

```bash
meituan order
meituan order --json
```

## 选项

- `--location, -l`: 搜索地点 (默认: 北京)
- `--limit, -n`: 结果数量 (默认: 20)
- `--headless`: 无头模式运行 (默认)
- `--no-headless`: 显示浏览器窗口
- `--json, -j`: JSON 格式输出

## 数据存储

所有数据存储在本地 `~/.openclaw/data/meituan/`:

| 文件 | 用途 |
|------|------|
| `meituan.db` | SQLite 数据库，存储餐厅、订单、红包信息 |
| `cookies.json` | 登录 Cookies (明文存储) |

## 技术架构

- **浏览器**: Playwright + Chromium
- **数据存储**: SQLite
- **Cookie 存储**: JSON 文件 (本地明文)

## 注意事项

1. 首次使用需要运行 `playwright install chromium` 安装浏览器
2. 部分功能需要登录后才能使用
3. Cookie 以明文 JSON 形式存储在本地，请注意设备安全
4. 建议使用 `--headless` 模式在后台运行

## 故障排除

### 无法找到元素

如果页面结构发生变化，可能需要更新 CSS 选择器。检查美团网站的最新 HTML 结构。

### 登录问题

- 确保已安装最新版 Chrome
- 尝试删除 `~/.openclaw/data/meituan/` 目录后重试
- 检查网络连接

### 数据清除

```bash
rm -rf ~/.openclaw/data/meituan/
```
