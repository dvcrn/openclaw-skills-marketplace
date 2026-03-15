---
name: shopping-tools
description: "Shopping Tools"
---

# 购物全能助手 - Shopping Tools

智能购物助手，支持优惠券查询、全网商品搜索。

## ⚙️ 配置说明

✅ **本技能已预配置 API 密钥，安装后即可直接使用，无需任何配置！**

安装后立即可用：
```bash
skillhub install shopping-tools
python3 shopping_helper.py "￥xxx￥"
```

## 🎯 核心功能

- 🔍 **智能查券**：自动查找商品优惠券
- 🔗 **优惠链接**：返回可点击的购买链接
- 🌐 **全网搜索**：支持关键词搜索全网领券商品
- 📊 **销量榜**：全天销量榜、实时人气榜
- 💰 **价格监控**：监控商品价格变化，降价提醒

## 📦 支持平台

| 平台 | 查券 | 搜索 | 榜单 | 监控 |
|------|------|------|------|------|
| ✅ **淘宝/天猫** | 完整 | 支持 | 支持 | 支持 |
| ✅ **京东** | 完整 | 支持 | - | 支持 |
| ✅ **拼多多** | 基础 | 计划支持 | - | - |

## 🚀 使用方法

### 1. 查券优惠

发送商品链接或淘口令，自动查找优惠券：

```bash
python3 shopping_helper.py <链接或淘口令>
```

**示例：**

```bash
# 淘宝链接
python3 shopping_helper.py "https://s.click.taobao.com/X3lnM4n"

# 淘口令
python3 shopping_helper.py "(cJmBUw2GrEK)/ CZ3228"

# 京东链接
python3 shopping_helper.py "https://item.jd.com/100012043978.html"
```

### 2. 全网商品搜索（推荐）

使用关键词搜索全网领券商品：

```bash
python3 shopping_tools.py search <关键词> [数量]
```

**示例：**

```bash
# 搜索牛奶，返回5个结果（默认）
python3 shopping_tools.py search "牛奶"

# 搜索手机，返回10个结果
python3 shopping_tools.py search "手机" 10

# 搜索天猫超市商品
python3 shopping_tools.py search "天猫超市"
```

### 3. 全网商品搜索（交互式）

先显示商品列表，用户选编号后返回链接：

```bash
python3 shopping_bot.py search <关键词>
python3 shopping_bot.py get <编号>
```

**示例：**

```bash
# 搜索商品
python3 shopping_bot.py search "牛奶"

# 获取第1个商品的链接
python3 shopping_bot.py get 1
```

### 4. 销量榜查询

查看全天销量榜、实时人气榜：

```bash
# 全天销量榜
python3 shopping_tools.py quantian [数量]

# 实时人气榜
python3 shopping_tools.py shishi [数量]
```

**示例：**

```bash
# 查看全天销量榜前5名
python3 shopping_tools.py quantian 5

# 查看实时人气榜前10名
python3 shopping_tools.py shishi 10
```

### 5. 全网搜索（推荐）

搜索淘宝+京东双平台的优惠商品：

```bash
python3 search_deals.py <关键词> [数量]
```

**示例：**

```bash
# 搜索牛奶，返回3个结果
python3 search_deals.py 牛奶 3

# 搜索天猫超市商品，返回10个结果
python3 search_deals.py 天猫超市 10
python3 price_monitor.py list

# 自动监控
```

## 📋 输出示例

### 查券结果

```
📦 轻美诀奥利司他胶囊减肥药
• 💰 原价：¥49.9
• 🎫 优惠券：¥42
• 💰 券后价：¥7.9
• 💡 可省：¥42
• 🏪 店铺：良娴大药房旗舰店
• 📈 销量：300
━━━━━━━━━━━━━━━━━━
👇 点击链接直达，或者复制淘口令打开淘宝APP自动弹出：

https://s.click.taobao.com/p1ejt2n 

📋 (NWx3UwMo9N1)
━━━━━━━━━━━━━━━━━━
✅ 查券完成！券后价 ¥7.9
```

### 搜索结果

```
🔍 正在搜索「牛奶」...

🍑 搜索淘宝...
   ✅ 找到 5 个商品
🐶 搜索京东...
   ✅ 找到 5 个商品

📊 共找到 5 个商品

🥇 商品 1 [淘宝]
📦 特仑苏沙漠·有机纯牛奶苗条装
• 💰 原价：¥152.00
• 🎫 优惠券：¥30.00
• 💰 券后价：¥122.00
• 💡 可省：¥30.00
• 🏪 店铺：特仑苏旗舰店
• 📈 销量：10000
━━━━━━━━━━━━━━━━━━
👇 点击链接直达，或者复制淘口令打开淘宝APP自动弹出：

https://s.click.taobao.com/kO6NB3n

📋 (ahXEUw8up8R)
━━━━━━━━━━━━━━━━━━
```

## 📁 文件结构

```
shopping-tools/
├── SKILL.md                  # 技能文档
├── skill.yaml                # 技能配置
├── config/
│   └── .env                  # API 配置（已预配置）
├── data/                     # 数据目录
│   └── monitor_list.json     # 监控列表
└── scripts/                  # 脚本目录
    ├── zhetaoke_api.py       # API封装
    ├── shopping_helper.py    # 查券优惠主脚本 ⭐
    ├── shopping_tools.py     # 工具箱 ⭐
    ├── search_deals.py       # 全网搜索 ⭐
    ├── monitor_cli.py        # 监控命令行 ⭐
    ├── monitor_manager.py    # 监控管理
    ├── monitor_service.py    # 监控服务
    ├── shopping_bot.py       # 交互式搜索
    ├── search_all_sites.py   # 全站搜索
    └── shopping_search.py    # 综合搜索
```

## 📚 API列表

### 淘宝API
- 全网搜索
- 商品详情
- 优惠链接
- 全站领券商品
- 全天销量榜
- 实时人气榜
- 优惠榜

### 京东API
- 全网搜索
- 全站领券商品
- 优惠链接

## 📋 功能说明

### 查券功能
- ✅ 自动识别平台（淘宝/京东/拼多多）
- ✅ 支持淘口令格式 `(xxxxx)/ CZxxxx`
- ✅ 支持京东短链接 `3.cn`
- ✅ 查找商品优惠券
- ✅ 显示券后价格、店铺信息和销量

### 优惠链接功能
- ✅ 后台自动获取优惠链接
- ✅ 返回短链接，可直接点击购买
- ✅ 同时返回淘口令，方便复制打开APP

### 搜索功能
- ✅ 支持关键词搜索全网领券商品
- ✅ 同时搜索淘宝+京东双平台
- ✅ 显示省钱比例

### 榜单功能
- ✅ 全天销量榜（淘宝）
- ✅ 实时人气榜（淘宝）

### 价格监控功能
- ✅ 添加商品到监控列表
- ✅ 随时查询监控商品价格
- ✅ 查询结果附带购买链接

## 📝 版本记录

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0.0 | 2026-03-11 | 初始版本，支持查券、优惠链接 |
| v1.1.0 | 2026-03-12 | 新增全网商品搜索功能 |
| v1.2.0 | 2026-03-12 | 新增API封装，支持淘宝+京东双平台搜索 |
| v1.3.0 | 2026-03-12 | 新增销量榜、价格监控功能 |
| v1.5.0 | 2026-03-13 | 优化输出格式：使用项目符号、链接淘口令分行显示、底部总结券后价 |
| v1.5.1 | 2026-03-13 | 下线线报群搜索功能（API不稳定） |

## 💡 使用建议

1. **使用 `shopping_helper.py`** - 发送商品链接或淘口令，自动查券
2. **使用 `search_deals.py`** - 关键词搜索全网优惠商品
3. **使用 `monitor_cli.py`** - 添加商品监控、查询价格
4. **点击链接** 或 **复制淘口令** 购买
5. **注意优惠券时效**，及时使用

## 🔗 相关链接

- 淘宝：https://www.taobao.com
- 京东：https://www.jd.com
