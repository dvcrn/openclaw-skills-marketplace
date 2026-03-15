---
name: interactive-card-reader
description: "获取飞书/QQ/企业微信交互式卡片内容，自动调用平台API解析卡片结构。Trigger on \"卡片内容\"、\"交互式卡片\"、\"获取卡片\"、\"card content\"。"
---

# 交互式卡片内容读取技能

自动获取飞书、QQ、企业微信的交互式卡片内容，解析卡片JSON结构，提供完整的卡片数据。

## 🎯 核心特性

### ⭐ 多平台支持
- ✅ **飞书**：支持交互式卡片、消息卡片
- ✅ **QQ**：待实现
- ✅ **企业微信**：待实现

### ⭐ 自动获取
- ✅ 检测消息ID
- ✅ 自动调用平台API
- ✅ 解析JSON结构
- ✅ 返回完整内容

### ⭐ AI友好
- ✅ 静默模式（无卡片不输出）
- ✅ JSON格式输出
- ✅ 易于AI处理

## 📊 平台支持

### 飞书（已完成）✅

**API端点：**
```
GET /open-apis/im/v1/messages/:message_id
```

**需要的权限：**
- `im:message:readonly` - 读取消息
- `im:message.p2p_msg:readonly` - 读取私聊消息

**返回格式：**
```json
{
  "msg_type": "interactive",
  "body": {
    "content": {
      "title": "卡片标题",
      "elements": [
        [{"tag": "text", "text": "内容"}]
      ]
    }
  }
}
```

### QQ（待实现）
- API研究进行中
- 需要QQ Bot权限

### 企业微信（待实现）
- API研究进行中
- 需要企业微信权限

## 🚀 使用方式

### 1. 安装技能

```bash
# 从ClawHub安装
clawhub install interactive-card-reader

# 或从本地安装
cd ~/.openclaw/workspace/skills/interactive-card-reader
bash install.sh
```

### 2. 配置

**飞书配置（config/feishu-config.json）：**
```json
{
  "app_id": "cli_a92cdc08bff8dcd3",
  "app_secret": "YOUR_APP_SECRET",
  "token_cache": true
}
```

### 3. AI集成

**方式1：自动检测（推荐）**

```bash
# AI收到消息后自动调用
scripts/integrate-card.sh "$USER_MESSAGE"
```

**方式2：手动调用**

```bash
# 指定消息ID获取卡片
scripts/get-feishu-card.sh "om_x100b55a43f16d4a0c2bff2ed4e68060"
```

### 4. 使用示例

**场景1：获取飞书卡片**

```
用户：[引用一张飞书卡片]
用户：这个卡片里有什么？

AI：[执行 scripts/integrate-card.sh]
    [检测到消息ID: om_x100b55a4...]
    [调用飞书API获取卡片]
    
    这张卡片包含：
    - 标题：xxx
    - 内容：xxx
    - 按钮：xxx
```

**场景2：解析表单卡片**

```
用户：看看这个表单卡片的内容

AI：[获取卡片]
    
    这是一个表单卡片：
    - 字段1：姓名（文本输入）
    - 字段2：部门（下拉选择）
    - 提交按钮：提交
```

## 🛠️ 技术实现

### 核心流程

```
用户消息 → detect-message-id.sh
              ↓
         检测消息ID
              ↓
         get-feishu-card.sh
              ↓
         调用飞书API
              ↓
         parse-card-json.sh
              ↓
         解析卡片结构
              ↓
         返回给AI
```

### 脚本说明

#### get-feishu-token.sh - 获取Token

```bash
# 自动获取tenant_access_token
# 缓存token（7082秒有效期）

输出：
{
  "token": "t-g10435cLWOEWVHKN36Y...",
  "expire": 7082
}
```

#### get-feishu-card.sh - 获取卡片

```bash
# 输入：消息ID
# 输出：卡片JSON

用法：
get-feishu-card.sh "om_x100b55a43f16d4a0c2bff2ed4e68060"

输出：
{
  "msg_type": "interactive",
  "content": {...}
}
```

#### parse-card-json.sh - 解析卡片

```bash
# 输入：卡片JSON
# 输出：易读的卡片结构

输出：
卡片类型：交互式卡片
标题：xxx
内容：
- 元素1：文本（xxx）
- 元素2：图片（image_key）
- 元素3：按钮（xxx）
```

## 📁 文件结构

```
interactive-card-reader/
├── SKILL.md                      # 技能文档
├── README.md                     # 使用说明
├── package.json                  # ClawHub配置
├── install.sh                    # 安装脚本
├── config/
│   ├── platform-config.json     # 平台配置
│   └── feishu-config.json       # 飞书配置
├── scripts/
│   ├── get-feishu-token.sh      # 获取Token
│   ├── get-feishu-card.sh       # 获取卡片
│   ├── parse-card-json.sh       # 解析卡片
│   └── integrate-card.sh        # AI集成
└── data/
    └── token-cache.json         # Token缓存
```

## 🔧 配置说明

### feishu-config.json

```json
{
  "app_id": "cli_a92cdc08bff8dcd3",
  "app_secret": "YOUR_APP_SECRET",
  "token_cache": {
    "enabled": true,
    "max_age": 7000
  },
  "api": {
    "base_url": "https://open.feishu.cn/open-apis",
    "timeout": 10000
  }
}
```

### platform-config.json

```json
{
  "platforms": {
    "feishu": {
      "enabled": true,
      "priority": 1
    },
    "qq": {
      "enabled": false,
      "priority": 2
    },
    "wechat": {
      "enabled": false,
      "priority": 3
    }
  }
}
```

## 📊 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 获取速度 | <500ms | API调用 |
| Token缓存 | ✅ | 7082秒有效期 |
| 解析准确率 | >95% | JSON解析 |
| 多平台 | 3个 | 飞书优先 |

## 💡 核心优势

### vs 截图识别
- ✅ 精确：获取原始JSON数据
- ✅ 完整：不遗漏任何字段
- ✅ 结构化：易于AI处理
- ✅ 自动化：无需手动截图

### vs 手动复制
- ✅ 快速：API调用获取
- ✅ 准确：不遗漏内容
- ✅ 格式化：JSON结构
- ✅ 可编程：易于扩展

## 🚨 常见问题

### Q1: Token过期怎么办？

**解决：**
- 自动缓存Token（7082秒有效期）
- 过期后自动重新获取
- 无需手动操作

### Q2: 无法获取卡片？

**可能原因：**
1. 权限不足（需要`im:message:readonly`）
2. 消息ID错误
3. 网络问题

**调试：**
```bash
# 测试Token获取
scripts/get-feishu-token.sh

# 测试卡片获取
scripts/get-feishu-card.sh "消息ID"
```

### Q3: 支持哪些卡片类型？

**飞书支持：**
- ✅ 交互式卡片（interactive）
- ✅ 消息卡片
- ✅ 表单卡片
- ✅ 图文卡片

## 🚀 未来规划

### 短期（本周）
- [x] 飞书卡片获取
- [x] Token自动管理
- [ ] QQ平台支持
- [ ] 企业微信支持

### 中期（本月）
- [ ] 卡片类型识别
- [ ] 表单数据提取
- [ ] 图片下载
- [ ] 批量获取

### 长期（未来）
- [ ] 卡片模板生成
- [ ] 可视化编辑
- [ ] 多语言支持
- [ ] 卡片分析统计

## 📝 版本历史

### v1.0.0 (2026-03-05)
- ✅ 飞书卡片获取
- ✅ Token自动管理
- ✅ JSON解析
- ✅ AI集成

---

*交互式卡片内容读取技能 v1.0.0*
*让卡片内容透明可见，AI完全理解*
*创建时间：2026-03-05 12:50*
*状态：✅ 飞书已完成，多平台进行中*
