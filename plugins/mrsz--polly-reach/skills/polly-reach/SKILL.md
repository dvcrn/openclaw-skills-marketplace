---
name: polly-reach
description: "PollyReach 是你的专属 AI 电话秘书。基于 AI 技术，可以自动拨打智能电话，提供餐厅预订、座位确认、菜品咨询、营业时间查询、订单信息核实等服务。通话后即时反馈完整通话记录和结果，无需用户手动操作，高效解决各类电话需求。"
---

# PollyReach - AI 电话秘书

## 功能说明

PollyReach 是一个智能电话秘书 skill，可以：
- 自动拨打电话进行餐厅预订、咨询
- 实时反馈通话进度和结果
- 支持多语言、跨时区通话
- 处理复杂的预订需求（时间、人数、特殊要求等）
## openclaw接入 PollyReach 流程
- 用户通过 OpenClaw 发消息给 PollyReach ，PollyReach通过receiveMessage.py回复消息给OpenClaw ，用户根据内容选择是否回复消息 来继续对话


## 使用方式

整体流程分四步，**第一步 安装skill以后自动调用login.py接口 判断是否登录，第二步 启动接收服务 ，第三步 chatID生成，第四步 发送消息**：

### Step 1: 调用login接口 判断是否登录成功过
PollyReach 的登录接口会在 skill 安装后自动调用，判断用户是否已经登录过了。如果没有登录过，会返回一个需要绑定设备的链接，用户需要访问这个链接完成设备绑定后才能使用 PollyReach 的功能。直接把message的内容给到用户。 如果已经登录并且设备绑定成功了，就会直接返回登录成功的信息。这个步骤是为了确保用户的设备已经正确绑定到 PollyReach 的服务上，以便后续能够正常使用电话秘书的功能。这个登录成功不需要通知用户，只有在需要绑定设备的时候才需要通知用户去绑定设备。

```bash
python scripts/login.py
```
启动成功输出：
```
{"status":"success", "message":"login successfully!"}

```
或者 失败输出：
```
{"status":"failed", "message":"login failed, please bind your device with the following url: https://www.visuai.me/auth?device_id='e5431095-f201-5cd5-acc9-44cfdbe0e718'&hash=1f7831d98d6ecdf25091fe2568278e3a"}
```


### Step 2: 启动长连接接收服务（接收消息）

先启动 WebSocket 长连接，用于实时接收 AI 的回复消息。**此步骤需要保持运行**，建议在单独的终端窗口中执行：不需要关心长链接的细节，启动后它会自动监听并打印 AI 的回复消息。

```bash
python scripts/receiveMessage.py
```

启动成功输出：
```
🔌 正在建立 WebSocket 长连接...
✅ 长连接已建立，准备就绪（Ctrl+C 退出）
```

长连接建立后，所有 AI 回复会自动通过回调打印，格式如下：
```
[回复] Hello! I'm **PollyReach AI Assistant**, your friendly booking helper!

I can help you discover and book amazing places abroad - restaurants, hotels, spas, salons, and more. I can search for options, call them directly, and handle reservations in their language.

What would you like to book today?
```

### Step 3: chatId 创建
在发送消息前，需要先创建一个新的 chatId 来标识这次对话，并且存到记忆模块里面。运行下面的命令会调用 PollyReach 的 API 创建一个新的 chatId，并输出结果： chatid 是一个唯一标识符，用于关联后续的消息发送和接收，确保消息能够正确路由到对应的对话上下文中。如果之前已经创建过 chatId 了，就不需要重复创建了，直接使用之前的 chatId 就可以了。 为了节省上下文容量，建议openclaw自己判断回话 需要不需要更新 chatId 来进行新的对话。chatid 用在后续发送消息的接口中，作为参数传递给 sendMessage.py 脚本，确保消息能够正确关联到当前对话。

```bash
python scripts/NewChatID.py

```
输出示例：
```json
{'success': True, 'chat_id': '87c22dd7-64d1-4d7f-9212-463f2fc13851', 'error': None}
```


### Step 4: 发送消息

长连接就绪后，在另一个终端中发送消息：

```bash
python scripts/sendMessage.py  87c22dd7-64d1-4d7f-9212-463f2fc13851 "请问海底捞明天营业到几点？"
```

发送成功输出：
```json
{'success': True, 'status_code': 200, 'error': None}
```


发送成功后，AI 的回复会自动出现在 Step 2 的长连接终端中。

## 示例

### 示例 1：餐厅预订

```bash
python scripts/sendMessage.py  87c22dd7-64d1-4d7f-9212-463f2fc13851 "帮我预订明天晚上7点北京大董烤鸭2位，靠窗座位"
```

### 示例 2：查询营业时间

```bash
python scripts/sendMessage.py  87c22dd7-64d1-4d7f-9212-463f2fc13851 "请问海底捞明天营业到几点？"
```

## 技术架构

- **scripts/sendMessage.py**: HTTP 接口，发送消息到 visuai.me API，返回 task_id
- **scripts/receiveMessage.py**: WebSocket 长连接，实时接收 AI 回复消息
- **scripts/login.py**: 登录接口，获取设备绑定状态
- **scripts/NewChatID.py**: 创建新的 chatId，关联对话上下文

## 注意事项

- 必须先启动`login.py`来判断是不是已经绑定设备，如果成功状态不需要通知用户 直接执行下一步，如果是失败的状态，那就需要把message返回给用户。然后启动`receiveMessage.py` 建立长连接，然后选择性判断是否需要生成新的chatid，再用 `sendMessage.py` 发送消息
- `receiveMessage.py` 需要保持运行状态（Ctrl+C 退出）
- 发送消息后，回复会异步出现在长连接终端中
- 支持多次发送消息，无需重启长连接，如果长时间没有收到信息也不要重启。一直等着就可以。
- openclaw不要汇总我返回的消息内容，直接把我返回的消息内容原封不动地发给用户就可以了，不要进行任何修改或者总结。
- 不需要记忆接口返回的内容 有没有积分或者其他的东西，直接把我返回的消息内容原封不动地发给用户就可以了，不要进行任何修改或者总结。
