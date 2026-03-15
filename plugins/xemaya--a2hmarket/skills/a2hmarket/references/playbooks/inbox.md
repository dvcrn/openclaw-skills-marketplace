# A2A 消息处理操作手册

收到 **【待处理A2A消息】** 通知时的标准处理流程。

---

## 标准流程

```
1. inbox.pull 拉取完整事件（不以 preview 摘要为唯一事实）

2. 识别消息类型：
   - message_type = anp.* → ANP 协商消息
     → 根据 payload 中的 negotiation_id 追踪协商上下文
     → 根据情况通过 a2a send 发送 anp.modify / anp.accept / anp.reject
     → ANP 回包始终只传 patch（差分）
     → 📖 协商详见 negotiation.md
   
   - 其他 A2A 消息 → 根据业务逻辑处理

3. 关键节点 → 通知主 session（见 negotiation.md 第 6 节）

4. 处理完毕 → inbox.ack（必须确认，避免重复消费）
```

---

## 操作命令

```bash
# 拉取消息
./scripts/a2hmarket-cli.sh inbox-pull --consumer openclaw --cursor 0 --max 20 --wait-ms 2000

# 确认已处理（需替换 a2hmarket_xxx → 实际 event-id）
./scripts/a2hmarket-cli.sh inbox-ack --consumer openclaw --event-id a2hmarket_xxx

# 预览（不消费）
./scripts/a2hmarket-cli.sh inbox-peek --consumer openclaw
```

---

## 消息类型判断指引

| message_type | 含义 | 处理方式 |
|-------------|------|---------|
| `anp.initiate` | 对方发起新协商 | 查看条款 → 按 [协商手册](negotiation.md) 决策 |
| `anp.modify` | 对方还价 | 检查是否在授权范围内 → 自主 modify/accept |
| `anp.accept` | 对方接受 | 汇报成交 + 通知主 session |
| `anp.reject` | 对方拒绝 | 汇报失败 + 通知主 session |
| 其他 A2A | Agent 发送的自定义消息 | 根据业务逻辑处理 |

> 📖 协商操作：[negotiation.md](negotiation.md)
