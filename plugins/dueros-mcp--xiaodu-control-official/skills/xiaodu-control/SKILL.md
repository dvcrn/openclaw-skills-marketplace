---
name: xiaodu-control
description: "当用户要连接、验证、排障或控制小度智能屏 MCP 与小度 IoT MCP 时使用，包括配置 mcporter、列设备、文本播报、语音指令、拍照、资源推送、IoT 家电控制、场景触发与平台 token 刷新。"
---

# xiaodu-control

使用这套 skill 处理所有小度 MCP 相关任务。优先使用 `mcporter` 和本 skill 自带脚本，不要临时拼接命令，也不要把请求路由到错误的 server。

## 使用前确认

- 这套 skill 依赖 `mcporter`、`python3` 和 `bash`。
- 这套 skill 需要小度平台相关凭据：`ACCESS_TOKEN`，以及用于长期刷新的 `AppKey / SecretKey / refresh_token`。
- 默认会读取并可能回写：
  - `~/.mcporter/mcporter.json`
  - `~/.mcporter/xiaodu-mcp-oauth.json`
- `scripts/refresh_xiaodu_mcp_token.sh` 会向百度 OAuth endpoint 发起网络请求，并更新 `mcporter` 配置里的 token。
- 如果你不希望修改默认全局配置，请改用自定义 OAuth 文件路径，并在其中把 `mcporter_config` 指向你自己的配置文件。

## 快速规则

- 把 `xiaodu` 和 `xiaodu-iot` 当作两个独立 server；它们通常共用同一个小度 MCP 平台 `ACCESS_TOKEN`。
- 不要猜测 MCP URL。优先使用平台给出的真实地址；智能屏常见地址是 `https://xiaodu.baidu.com/dueros_mcp_server/mcp/`。
- 只要本 skill 已经提供了脚本封装，就优先用脚本，不要直接跳到底层 MCP 工具。
- 智能屏操作先解析设备，再执行真实调用。
- 灯、空调、窗帘、电视、插座、风扇等家电控制，优先走 `xiaodu-iot`，不要走 `control_xiaodu`。
- `control_xiaodu` 只用于智能屏语音助手类请求，例如播放音乐、暂停、天气、新闻。
- 排障时，用 `mcporter list ... --schema` 和 direct `mcporter call` 对照 skill 行为。
- 不要把密钥写进 workspace 文件或聊天记录；优先写入 `mcporter` 配置或 auth 存储。

## 标准流程

1. 先确认前提：
   - 已安装 `mcporter`
   - 已拿到平台 `ACCESS_TOKEN`
   - 如果需要长期刷新，还要拿到 `AppKey / SecretKey / refresh_token`
2. 先探测，再持久化配置：
   - 智能屏：`bash scripts/probe_xiaodu.sh --url "https://real-xiaodu-mcp-url" --name xiaodu`
   - IoT：`mcporter list --stdio npx --stdio-arg -y --stdio-arg dueros-iot-mcp --env ACCESS_TOKEN=... --name xiaodu-iot --schema`
3. 持久化后先读 schema：
   - `mcporter list xiaodu --schema`
   - `mcporter list xiaodu-iot --schema`
4. 操作前先拿设备信息：
   - 智能屏：`bash scripts/list_devices.sh`
   - IoT：`bash scripts/list_iot_devices.sh`
5. 执行控制；如果结果异常，再回退 direct `mcporter call`

## 操作选择

### 智能屏

- 列设备：`bash scripts/list_devices.sh`
- 文本播报：`bash scripts/speak.sh`
- 语音指令：`bash scripts/control_xiaodu.sh`
- 拍照：`bash scripts/take_photo.sh`
- 推送图片/视频/音频：`bash scripts/push_resource.sh`

### IoT

- 查设备状态：`bash scripts/list_iot_devices.sh`
- 控制家电：`bash scripts/control_iot.sh`
- 查场景：`bash scripts/list_scenes.sh`
- 触发场景：`bash scripts/trigger_scene.sh`

### Token 刷新

- 刷新平台 token 并回写配置：`bash scripts/refresh_xiaodu_mcp_token.sh`

## 关键路由规则

- 智能屏侧除 `list_user_devices` 外，通常都要求 `cuid` 和 `client_id`；如果用户只给设备名，先解析设备。
- `IOT_CONTROL_DEVICES` 的 `applianceName` 是必填字段，不能只传房间不传设备名。
- 若用户只说“关灯 / 开空调 / 调亮度 / 调温度”，默认按 IoT 控制理解。
- 若用户只说“播报一句话 / 拍张照 / 播放音乐”，默认按智能屏理解。
- 负向测试和参数校验优先走脚本，确保返回本地校验错误。
- 只有这几类情况可以直接用原始 `mcporter call`：
  - 读取 schema
  - 用户明确要求 direct CLI
  - 本 skill 没有对应脚本
  - 做兜底验证，证明问题在 skill 层还是在 MCP 本身

## 自带脚本

发布到 ClawHub 后，脚本文件默认按普通文本落盘，不保证保留可执行位。命令示例里优先使用 `bash scripts/*.sh` 和 `python3 scripts/*.py`，不要假设可以直接 `./scripts/foo.sh`。

- `scripts/probe_xiaodu.sh`
  - 对真实 MCP URL 做快速连通性检查。
- `scripts/list_devices.sh`
  - 直接调用 `list_user_devices` 并输出 JSON。
- `scripts/refresh_devices.sh`
  - 拉取智能屏和 IoT 设备快照，输出 JSON 和 Markdown 摘要。
- `scripts/device_resolver.py`
  - 按设备名解析 `cuid` 和 `client_id`，供其他脚本复用。
- `scripts/speak.sh`
  - 封装 `xiaodu_speak`，用于单次文本播报。
- `scripts/control_xiaodu.sh`
  - 封装 `control_xiaodu`，用于发送语音指令。
- `scripts/push_resource.sh`
  - 封装 `push_resource_to_xiaodu`，支持图片、图片+背景音、视频、音频。
- `scripts/take_photo.sh`
  - 封装 `xiaodu_take_photo`，用于指定设备拍照。
- `scripts/control_iot.sh`
  - 封装 `IOT_CONTROL_DEVICES`，用于按房间或设备名控制。
- `scripts/list_iot_devices.sh`
  - 封装 `GET_ALL_DEVICES_WITH_STATUS`，用于读取 IoT 设备和状态。
- `scripts/list_scenes.sh`
  - 封装 `GET_ALL_SCENES`，用于读取可用场景。
- `scripts/trigger_scene.sh`
  - 封装 `TRIGGER_SCENES`，用于触发指定场景。
- `scripts/refresh_xiaodu_mcp_token.sh`
  - 用 `refresh_token` 刷新小度 MCP 平台 `ACCESS_TOKEN`，并按配置里的 `targets` 自动回写 `mcporter` 配置。默认模板会同时更新 `xiaodu` 和 `xiaodu-iot`。

## 按需阅读引用文档

- 安装、鉴权、模板、token 刷新：读 [references/install-for-users.md](references/install-for-users.md)。
- 直接给用户模板：读 [references/mcporter.template.json](references/mcporter.template.json) 和 [references/xiaodu-mcp-oauth.template.json](references/xiaodu-mcp-oauth.template.json)。
- 精确 CLI 示例：读 [references/command-patterns.md](references/command-patterns.md)。
- 中文聊天模板：读 [references/prompt-templates.md](references/prompt-templates.md)。
- 功能验证：读 [references/test-cases.md](references/test-cases.md)。
- 排障：读 [references/troubleshooting.md](references/troubleshooting.md)。
