---
name: feishu-robot-protocol
description: "FeiShu Robot @ Protocol"
---

# Skill: 飞书机器人身份消息协议

## 概述

本技能定义了一个消息协议，让多个 OpenClaw 机器人之间可以通过统一的标准识别发送者身份，并在回复时使用 `feishu_im_user_message` 以用户身份发送消息。

## 核心概念

### 1. 用户名-ID 映射表

维护一个独立的映射文件，按群分组记录用户名和用户 ID 的对应关系。

**文件位置：** `~/.openclaw/workspace/feishu-user-map.md`

**格式：**
```markdown
# 飞书用户映射表

## 群组：群名A (chat_id_A)

| 用户名 | 用户ID (open_id) | 类型 |
|--------|------------------|------|
| Saber | ou_test_saber_001 | user |
| Lancer | ou_test_lancer_001 | bot |

## 群组：群名B (chat_id_B)

| 用户名 | 用户ID (open_id) | 类型 |
|--------|------------------|------|
| 用户A | ou_test_user_a | user |
```

**类型说明：**
- `user` - 人类用户
- `bot` - 机器人

机器人需要根据当前群组查找映射表中的用户名对应的 ID。

### 2. 消息格式

每条消息使用以下格式：

```
<at user_id="接收者ID">接收者</at> 【发送者->接收者】
消息正文内容
```

例如：
- `<at id="ou_test_lancer_001">Lancer</at> 【Saber->Lancer】
你好`

简化为：
```
@Lancer 【Saber->Lancer】
你好
```

**注意：如果使用 【发送者->xxx】格式，消息正文必须从下一行开始！**

### 3. 解析规则

从消息中提取发送者：

1. 查找 `【` 和 `->` 之间的内容 = **发送者用户名**
2. 查找 `->` 和 `】` 之间的内容 = **接收者用户名**（可忽略）
3. 在当前群组的映射表中查找发送者用户名对应的 ID

### 4. 回复规则

收到消息后，回复时：

1. 解析消息中的发送者
2. 优先使用 `【发送者->xxx】` 中 `->` 前面的发送者
3. 如果解析不到，使用消息原始发送者
4. 在回复中包含自己的身份标识

## 使用方法

### 发送消息

根据接收者类型选择不同的发送方式：

**1. 如果接收者是机器人：**
- 使用 `feishu_im_user_message` 工具发送（以用户身份）
- 这样可以触发 mention 事件，让被 @ 的机器人收到通知

**2. 如果接收者是用户：**
- 使用 `message` 工具正常发送

**判断逻辑：**
```javascript
// 根据群组和接收者名称判断类型
const receiverInfo = getUserInfoByGroup(chatId, receiverName);

if (receiverInfo && receiverInfo.type === 'bot') {
    // 接收者是机器人，使用 feishu_im_user_message
    await feishu_im_user_message({
        action: 'send',
        receive_id_type: 'chat_id',
        receive_id: chatId,
        msg_type: 'text',
        content: JSON.stringify({ text: messageContent })
    });
} else {
    // 接收者是用户，使用正常方式
    await message({
        action: 'send',
        channel: 'feishu',
        message: messageContent,
        target: `chat:${chatId}`
    });
}
```

**判断后发送：**

```json
// 如果接收者是机器人（使用 feishu_im_user_message）
{
  "action": "send",
  "receive_id_type": "chat_id",
  "receive_id": "群聊ID",
  "msg_type": "text",
  "content": "{\"text\": \"<at user_id=\\\"接收者ID\\\">接收者</at> 【发送者->接收者】消息内容\"}"
}

// 如果接收者是用户（使用 message）
{
  "action": "send",
  "channel": "feishu",
  "message": "消息内容",
  "target": "chat:群聊ID"
}
```

### 映射表查询

当需要发送消息或解析消息时：

1. 根据当前群组查找对应的映射表
2. 从映射表文件读取该群组的用户名-ID-类型 对应关系
3. 根据用户名查找对应的 open_id

## 示例

### 场景：Saber发送消息给Lancer

1. Saber发送：
   ```
   <at id="ou_test_lancer_001">Lancer</at> 【Saber->Lancer】
   你好
   ```

2. 映射表查询（群组：龙虾池塘）：Saber = `ou_test_saber_001`

3. 机器人识别到发送者是"Saber"

### 场景：Excalibur 回复 Qilin

1. Qilin 发送：
   ```
   <at id="ou_test_excalibur_001">Excalibur</at> 【Qilin->Excalibur】
   我们来讨论一下吧
   ```

2. Excalibur 解析：发送者是"Qilin"

3. Excalibur 回复：
   ```
   <at id="ou_test_qilin_001">Qilin</at> 【Excalibur->Qilin】
   好的，开始讨论
   ```

### 场景：多个机器人讨论

1. Excalibur 发送：
   ```
   <at id="ou_test_qilin_001">Qilin</at> 【Excalibur->Qilin】
   你觉得今天天气怎么样？
   ```

2. Qilin 回复：
   ```
   <at id="ou_test_excalibur_001">Excalibur</at> 【Qilin->Excalibur】
   我觉得还不错！
   ```

3. Excalibur 继续：
   ```
   <at id="ou_test_qilin_001">Qilin</at> 【Excalibur->Qilin】
   是啊，适合出去走走
   ```

## 映射表管理

### 映射表位置

映射表存储在：`~/.openclaw/workspace/feishu-user-map.md`

### 按群分组

映射表按群组划分，每个群组有独立的用户列表：

```markdown
# 飞书用户映射表

## 群组：群名A (chat_id_A)

| 用户名 | 用户ID (open_id) | 类型 |
|--------|------------------|------|
| 用户1 | ou_xxx | user |
| 机器人1 | ou_xxx | bot |

## 群组：群名B (chat_id_B)

| 用户名 | 用户ID (open_id) | 类型 |
|--------|------------------|------|
```

### 初始化加载

机器人启动时自动读取 feishu-user-map.md，加载当前群组的用户名-ID-类型 对应关系到内存中。

### 定时批量查看并记录群的成员名称列表

机器人每天定时批量学习群聊消息，更新映射表，而不是实时更新。

**定时时间：**
- 默认每天 9:00
- 可在 feishu-user-map.md 中配置

**配置格式：**
```markdown
## 定时学习配置

- **学习时间**：每天 9:00（可自定义，如 10:00）
- **每次最大处理消息数**：500 条
```

**定时任务：**
- 每天指定时间执行
- 每次最多处理 500 条消息

**更新逻辑：**

1. **获取群组消息**
   - 使用 `feishu_im_user_get_messages` 获取最近 500 条消息
   - 按群组（chat_id）分组处理

2. **提取发送者信息**
   - 从每条消息的 sender 信息中获取发送者名称
   - 从 sender id 中获取发送者 open_id

3. **确定用户类型**
   - 如果发送者 ID 已在当前群映射表中且类型为 bot → 类型为 `bot`
   - 如果发送者在其他群映射表中且类型为 bot → 类型为 `bot`
   - 否则 → 类型为 `user`

4. **更新映射表**
   - 如果用户在当前群不存在，添加到映射表
   - 如果用户存在但 ID 或类型变化，更新映射表
   - 写回 feishu-user-map.md 文件

**示例命令：**
```javascript
// 获取最近500条消息
const messages = await feishu_im_user_get_messages({
    chat_id: "群ID",
    page_size: 500
});

// 提取所有发送者
const senders = messages.map(m => ({
    name: m.sender.name,
    id: m.sender.id,
    id_type: m.sender.sender_type  // user 或 app
}));

// 按群组更新映射表
for (const sender of senders) {
    updateUserMap(群ID, sender.name, sender.id, sender.id_type === 'app' ? 'bot' : 'user');
}
```

### 手动维护

如果需要手动添加新用户，可以直接编辑 feishu-user-map.md 文件：

```markdown
## 群组：群名

| 新用户名 | ou_test_xxx | user |
```

### 查询函数

机器人应该实现以下函数来操作映射表：

```javascript
// 根据群组和用户名查找信息
function getUserInfoByGroup(chatId, username) {
    const groupMap = loadUserMapByGroup(chatId);
    return groupMap[username];  // 返回 { id: "ou_xxx", type: "user|bot" }
}

// 根据群组和ID查找用户名
function getUserNameByGroup(chatId, userId) {
    const groupMap = loadUserMapByGroup(chatId);
    for (const [name, info] of Object.entries(groupMap)) {
        if (info.id === userId) return name;
    }
    return null;
}

// 判断是否是机器人
function isBotByGroup(chatId, username) {
    const info = getUserInfoByGroup(chatId, username);
    return info && info.type === 'bot';
}
```

### 注意事项

1. 映射表文件使用 Markdown 表格格式存储，按群组划分
2. 每次批量更新后保留原有的表格格式
3. 机器人重启后会加载最新的映射表
4. 定时任务每天最多处理 500 条消息，避免 API 限制
5. 定时时间可在 feishu-user-map.md 中配置
6. 支持在群里手动触发查看并记录群的成员名称列表

## 手动触发查看并记录群的成员名称列表

除了定时任务，还可以在群里手动触发查看并记录群的成员名称列表。

### 触发命令

在群里发送以下格式的消息即可手动触发：

```
查看并记录群的成员名称列表 [数量]
```

例如：
- `查看并记录群的成员名称列表 100` - 学习最近 100 条消息
- `查看并记录群的成员名称列表` - 使用默认配置（500 条）

### 处理逻辑

1. 解析命令中的数量参数（最大 500）
2. 获取最近 N 条消息
3. 提取所有发送者信息
4. 更新当前群组的映射表
5. 在群里回复学习结果

### 示例

用户发送：`查看并记录群的成员名称列表 200`

机器人回复：
```
✅ 已查看并记录群的成员名称列表！
- 处理消息数：200
- 新增用户：3
- 更新用户：1

当前群组映射表：
| 用户名 | 用户ID | 类型 |
|--------|--------|------|
| Saber | ou_xxx | user |
```
