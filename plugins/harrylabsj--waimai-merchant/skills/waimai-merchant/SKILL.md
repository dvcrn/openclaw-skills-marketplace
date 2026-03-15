---
name: waimai-merchant
description: "外卖商家管理 Skill - 支持商家注册、商品管理、价格修改和配送时间设置。Use when user mentions merchant registration, product management, price updates, delivery time settings for food delivery business."
---

# Waimai Merchant - 外卖商家管理

外卖商家管理系统，支持商家注册、商品管理、价格修改和配送承诺时间设置。

## 核心功能

1. **商家注册** - 商家信息录入、认证管理
2. **商品上传** - 添加新商品（名称、描述、图片、价格等）
3. **价格修改** - 更新商品价格
4. **配送承诺时间** - 设置/修改每个商品的承诺到货时间

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/waimai-merchant
npm install
npm run build
```

## CLI 命令入口

### 商家管理命令

```bash
# 注册新商家
node dist/index.js merchant register -n "美味餐厅" -p "13800138000" -a "北京市朝阳区xxx街道"

# 列出所有商家
node dist/index.js merchant list

# 按状态筛选商家
node dist/index.js merchant list --status approved

# 查看商家详情
node dist/index.js merchant show <id>

# 更新商家信息
node dist/index.js merchant update <id> -n "新名称" -p "新电话"

# 认证商家
node dist/index.js merchant approve <id>

# 拒绝商家
node dist/index.js merchant reject <id>

# 暂停商家
node dist/index.js merchant suspend <id>

# 删除商家
node dist/index.js merchant delete <id>

# 搜索商家
node dist/index.js merchant search <keyword>
```

### 商品管理命令

```bash
# 添加新商品
node dist/index.js product add -m <merchant_id> -n "红烧肉" -p 38.00 -c "热菜" -t 30 -s 100

# 列出商品
node dist/index.js product list

# 按商家筛选商品
node dist/index.js product list -m <merchant_id>

# 只显示上架商品
node dist/index.js product list -a

# 按分类筛选
node dist/index.js product list -c "热菜"

# 查看商品详情
node dist/index.js product show <id>

# 更新商品信息
node dist/index.js product update <id> -n "新名称" -d "新描述"

# 修改商品价格
node dist/index.js product price <id> <new_price>

# 修改配送时间
node dist/index.js product delivery <id> <minutes>

# 上架商品
node dist/index.js product activate <id>

# 下架商品
node dist/index.js product deactivate <id>

# 标记售罄
node dist/index.js product soldout <id>

# 删除商品
node dist/index.js product delete <id>

# 搜索商品
node dist/index.js product search <keyword>

# 列出所有分类
node dist/index.js product categories
```

### 其他命令

```bash
# 查看数据存储位置
node dist/index.js data

# 显示帮助
node dist/index.js --help
node dist/index.js merchant --help
node dist/index.js product --help
```

## 数据结构

### 商家 (Merchant)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 商家名称 |
| phone | TEXT | 联系电话（唯一） |
| email | TEXT | 电子邮箱 |
| address | TEXT | 商家地址 |
| business_license | TEXT | 营业执照号 |
| contact_person | TEXT | 联系人姓名 |
| status | TEXT | 状态：pending/approved/rejected/suspended |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 商品 (Product)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| merchant_id | INTEGER | 商家ID（外键） |
| name | TEXT | 商品名称 |
| description | TEXT | 商品描述 |
| price | REAL | 当前价格 |
| original_price | REAL | 原价 |
| image_url | TEXT | 商品图片URL |
| category | TEXT | 商品分类 |
| delivery_time | INTEGER | 配送承诺时间（分钟） |
| stock | INTEGER | 库存数量 |
| status | TEXT | 状态：active/inactive/sold_out |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 数据存储

数据存储在: `~/.waimai-merchant/`
- `merchant.db` - SQLite 数据库文件

## 使用流程

### 商家入驻流程

1. **注册商家**: 使用 `merchant register` 录入基本信息
2. **等待审核**: 商家状态为 `pending`
3. **审核通过**: 管理员使用 `merchant approve` 通过认证
4. **开始营业**: 商家可以添加商品

### 商品管理流程

1. **添加商品**: 使用 `product add` 创建商品
2. **设置价格**: 初始价格可在添加时设置，后续用 `product price` 修改
3. **设置配送时间**: 初始配送时间在添加时设置，后续用 `product delivery` 修改
4. **上架销售**: 使用 `product activate` 将商品上架
5. **日常管理**: 根据库存情况使用 `product soldout` 或 `product deactivate`

## 技术栈

- **语言**: TypeScript / Node.js
- **数据库**: SQLite (better-sqlite3)
- **CLI 框架**: Commander.js
- **样式**: Chalk

## 扩展计划

以下功能为后续迭代方向：

- [ ] Web 管理界面
- [ ] 订单管理功能
- [ ] 数据统计报表
- [ ] API 接口开发
- [ ] 与 waimai-ai.ai 网站集成
