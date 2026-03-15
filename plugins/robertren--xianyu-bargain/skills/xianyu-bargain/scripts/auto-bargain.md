# 闲鱼全自动砍价 - 完整实现指南

## 概述

本文档详细说明如何实现完全自动化的闲鱼砍价流程，包括：
- 自动发送砍价消息
- 定时监控卖家回复
- 智能分析并自动跟进
- 关键节点通知用户

---

## 启动全自动砍价

### Step 1: 收集参数

```yaml
required:
  - item_url: 商品链接
  - target_price: 目标价格
  - max_price: 底价（最高可接受）

optional:
  - check_interval: 监控间隔（默认 3 分钟）
  - max_rounds: 最大轮次（默认 5 轮）
  - strategy: 策略（aggressive/moderate/gentle）
```

### Step 2: 获取商品信息

```javascript
// 1. 打开商品页面
browser({ action: "open", url: itemUrl })

// 2. 获取快照，提取：
//    - 商品名称
//    - 卖家ID
//    - 当前价格
//    - 商品成色
//    - 卖家信息（评价、在线时间等）
```

### Step 3: 创建状态文件

```bash
mkdir -p ~/.openclaw/workspace/xianyu-bargain-state
```

```json
// ~/.openclaw/workspace/xianyu-bargain-state/{itemId}.json
{
  "itemId": "1030963177488",
  "itemUrl": "https://www.goofish.com/item?id=1030963177488",
  "chatUrl": "https://www.goofish.com/im?itemId=1030963177488&peerUserId=2009038787",
  "itemName": "iPhone 17 256G 紫色",
  "originalPrice": 4588,
  "sellerId": "2009038787",
  "sellerName": "北京十年数码人",
  
  "targetPrice": 4500,
  "maxPrice": 4550,
  "currentOffer": 4500,
  
  "round": 1,
  "maxRounds": 5,
  "checkInterval": 180000,
  
  "status": "active",
  "lastCheck": "2026-03-13T13:22:00+08:00",
  "lastMessageTime": "2026-03-13T13:22:00+08:00",
  "lastSellerMessageId": null,
  
  "history": [
    {
      "role": "buyer",
      "message": "你好～这台 iPhone 17 很喜欢...",
      "time": "2026-03-13T13:22:00+08:00"
    }
  ],
  
  "cronJobId": "xxxxxxxx-xxxx-xxxx-xxxx"
}
```

### Step 4: 发送首轮消息

```javascript
// 1. 导航到聊天页面
browser({ action: "navigate", url: chatUrl })

// 2. 输入砍价消息
browser({ 
  action: "act", 
  kind: "type", 
  ref: "inputRef",
  text: generateFirstMessage(itemName, targetPrice)
})

// 3. 点击发送
browser({ action: "act", kind: "click", ref: "sendButtonRef" })
```

### Step 5: 创建监控 Cron Job

```javascript
cron({
  action: "add",
  job: {
    name: `闲鱼砍价-${itemId}`,
    schedule: { kind: "every", everyMs: 180000 },  // 3分钟
    sessionTarget: "isolated",
    payload: {
      kind: "agentTurn",
      message: `
执行闲鱼砍价监控任务：
1. 读取状态文件 ~/.openclaw/workspace/xianyu-bargain-state/${itemId}.json
2. 打开聊天页面检查新消息
3. 如果有新的卖家回复，使用 bargain_analyzer.py 分析
4. 根据分析结果执行相应动作
5. 更新状态文件
6. 如需通知用户，通过 announce 推送
`,
      timeoutSeconds: 120
    },
    delivery: { mode: "announce" }
  }
})
```

---

## 监控任务执行流程

### 每次监控执行的步骤

```
1. 读取状态文件
   ↓
2. 检查状态是否为 active
   ├─ 否 → 退出
   └─ 是 ↓
3. 打开聊天页面
   ↓
4. 获取消息列表快照
   ↓
5. 比对最新消息与上次记录
   ├─ 无新消息 → 检查是否需要跟进 → 更新状态 → 退出
   └─ 有新消息 ↓
6. 分析卖家回复（调用 bargain_analyzer.py）
   ↓
7. 根据分析结果执行动作
   ├─ SUCCESS → 通知用户成交 → 更新状态为 success
   ├─ ACCEPT → 发送接受消息 → 通知用户 → 更新状态
   ├─ COUNTER → 检查是否达到底价上限
   │     ├─ 是 → 通知用户决策
   │     └─ 否 → 发送加价消息 → 更新状态
   ├─ RESPOND → 生成回复 → 发送 → 更新状态
   ├─ GIVE_UP → 发送放弃消息 → 通知用户 → 更新状态
   └─ FOLLOW_UP → 发送跟进消息 → 更新状态
   ↓
8. 保存更新后的状态文件
```

### 检查新消息的方法

```javascript
// 获取聊天页面快照
const snapshot = await browser({ action: "snapshot", targetId })

// 解析消息列表
// 查找最新的卖家消息（非当前用户发送的）
// 比对消息ID或时间戳与状态文件中的 lastSellerMessageId

// 如果有新消息，提取消息内容
```

### 超时跟进逻辑

```python
# 计算距离上次消息的时间
time_since_last = now - last_message_time

# 超过设定时间（如 30 分钟）无回复
if time_since_last > timedelta(minutes=30):
    if follow_up_count < 2:  # 最多跟进 2 次
        send_follow_up_message()
        update_follow_up_count()
    else:
        notify_user("卖家长时间未回复")
```

---

## 停止监控

### 用户主动停止

```javascript
// 1. 获取 cron job ID
const state = read_state_file(itemId)
const cronJobId = state.cronJobId

// 2. 删除 cron job
cron({ action: "remove", jobId: cronJobId })

// 3. 更新状态
state.status = "cancelled"
save_state_file(state)

// 4. 通知用户
announce("已停止对 {itemName} 的砍价监控")
```

### 自动停止条件

- 砍价成功（status = success）
- 主动放弃（status = abandoned）
- 达到最大轮次且卖家仍拒绝
- 商品已下架或已被他人购买

---

## 通知模板

### 成交通知
```
🎉 砍价成功！

商品：{itemName}
成交价：¥{finalPrice}（原价 ¥{originalPrice}，省了 ¥{saved}）

请尽快前往闲鱼下单：
{itemUrl}
```

### 卖家还价（需决策）
```
💰 卖家还价通知

商品：{itemName}
卖家出价：¥{sellerPrice}
你的底价：¥{maxPrice}

卖家价格超出你的底价 ¥{diff}，请决定：
- 回复 "接受" 同意卖家价格
- 回复 "继续砍" 尝试继续压价
- 回复 "放弃" 结束砍价
```

### 卖家拒绝
```
❌ 砍价未成功

商品：{itemName}
卖家表示不议价

是否要：
- 回复 "加到{maxPrice}" 出底价
- 回复 "放弃" 结束砍价
```

### 超时无回复
```
⏰ 卖家暂未回复

商品：{itemName}
已等待：{waitTime}

已自动发送跟进消息，继续监控中...
如需停止，回复 "停止砍价"
```

---

## 文件结构

```
~/.agents/skills/xianyu-bargain/
├── SKILL.md                          # 主技能文件
├── scripts/
│   ├── bargain_analyzer.py           # 回复分析器
│   └── auto-bargain.md               # 本文档
└── references/
    ├── market-prices.md              # 市场参考价
    └── advanced-strategies.md        # 高级策略

~/.openclaw/workspace/xianyu-bargain-state/
└── {itemId}.json                     # 各商品的砍价状态
```

---

## 安全考虑

1. **频率限制**：监控间隔不低于 3 分钟
2. **同时任务数**：建议同时监控不超过 3 个商品
3. **异常处理**：登录失效、页面变化等需要人工介入
4. **数据保护**：状态文件仅存储在本地
