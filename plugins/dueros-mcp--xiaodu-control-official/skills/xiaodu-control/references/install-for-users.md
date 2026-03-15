# 用户的安装指南

这份文档就是这套 skill 的唯一安装文档。目标是让每个安装者在自己的 OpenClaw 环境里独立完成配置、验证和自动刷新。

## 适用场景

- 你在自己的电脑上安装了 OpenClaw
- 你想把 `xiaodu-control` 用在自己的 OpenClaw 会话里
- 你不会复用别人机器上的 `mcporter` 配置

## 你需要准备的东西

### 智能屏 MCP

- 小度智能屏 MCP 的真实 HTTP MCP URL
- 可用的 `ACCESS_TOKEN`

### 小度 IoT MCP

- `AppKey`
- `SecretKey`
- `refresh_token`
- 一个当前可用的 `ACCESS_TOKEN`

## 最短理解版

整个安装流程可以压成 5 步：

1. 先到小度 MCP 控制台创建应用，并完成调试授权
2. 按模板填写 `~/.mcporter/mcporter.json`
3. 按模板填写 `~/.mcporter/xiaodu-mcp-oauth.json`
4. 用 `mcporter list` / `mcporter call` 验证本地 MCP 已跑通
5. 需要长期使用时，再安装自动刷新

通常情况下，`xiaodu` 和 `xiaodu-iot` 可以复用同一个小度 MCP 平台 `ACCESS_TOKEN`。这份文档和模板默认按“同一个 token 同时写入两个 server”处理；只有当你明确拿到了两套不同 token，才需要手动改成分别维护。

## 第零步：先在平台创建应用并完成调试授权

第一次接入时，不要先改本地文件，先去平台把信息拿齐。

### 入口

- 小度 MCP 控制台：[`https://dueros.baidu.com/dbp/mcp/console`](https://dueros.baidu.com/dbp/mcp/console)

### 你需要在平台做的事

1. 登录控制台
2. 创建你自己的小度 MCP 应用
3. 打开应用详情页
4. 点击“调试授权”
5. 记录下面这些信息

### 你要从平台拿到什么

- 平台 `ACCESS_TOKEN`
- `AppKey`
- `SecretKey`
- `refresh_token`
- 智能屏 MCP 地址

### 关于智能屏 MCP 地址

如果你接的是当前这套小度智能终端 MCP，实际接入时通常使用：

```text
https://xiaodu.baidu.com/dueros_mcp_server/mcp/
```

这是基于当前平台接入和现有实测整理出的常用地址。  
如果你在控制台或官方说明里看到了平台明确给出的地址，优先以平台显示为准。

### 调试授权拿到的值怎么用

- `ACCESS_TOKEN`
  - 直接写进 `mcporter.json`
  - 默认同时给 `xiaodu` 和 `xiaodu-iot` 用
- `AppKey / SecretKey / refresh_token`
  - 写进 `xiaodu-mcp-oauth.json`
  - 供后续刷新 token 使用

## 第一步：安装 mcporter

如果还没装：

```bash
npm install -g mcporter
```

验证：

```bash
mcporter --help
```

建议先确认 `mcporter` 当前会读哪些配置源：

```bash
mcporter config list
```

正常情况下你会看到：

- 项目配置：`./config/mcporter.json`
- 系统配置：`~/.mcporter/mcporter.json`

给这套 skill 配置 server 时，推荐统一写到系统配置 `~/.mcporter/mcporter.json`。

如果你平时把 `mcporter` 或 OpenClaw 配在非默认目录，下面所有示例里的 `~/.mcporter/...` 和 `~/.openclaw/...` 都要按你的实际路径替换。

## 第二步：创建 `~/.mcporter/mcporter.json`

建议直接以这个模板为起点：

[`mcporter.template.json`](mcporter.template.json)

最小示例：

```json
{
  "mcpServers": {
    "xiaodu": {
      "baseUrl": "https://替换成你的智能屏MCP地址",
      "headers": {
        "ACCESS_TOKEN": "替换成你的小度MCP平台ACCESS_TOKEN"
      }
    },
    "xiaodu-iot": {
      "command": "npx",
      "args": [
        "-y",
        "dueros-iot-mcp"
      ],
      "env": {
        "ACCESS_TOKEN": "替换成你的小度MCP平台ACCESS_TOKEN"
      }
    }
  }
}
```

保存到：

```text
~/.mcporter/mcporter.json
```

如果你不想手动编辑 JSON，也可以直接用命令写入：

```bash
mcporter config add xiaodu \
  --url "https://替换成你的智能屏MCP地址" \
  --header "ACCESS_TOKEN=替换成你的小度MCP平台ACCESS_TOKEN" \
  --persist ~/.mcporter/mcporter.json

mcporter config add xiaodu-iot \
  --command npx \
  --arg -y \
  --arg dueros-iot-mcp \
  --env "ACCESS_TOKEN=替换成你的小度MCP平台ACCESS_TOKEN" \
  --persist ~/.mcporter/mcporter.json
```

## 第三步：创建小度 MCP 平台 OAuth 刷新凭据文件

这一步不是在配置“只给 `xiaodu-iot` 用的一套 OAuth”。

这里配置的是：

- 用来刷新小度 MCP 平台 `ACCESS_TOKEN` 的 OAuth 凭据
- 刷新成功后，要把新 token 回写到哪些 MCP server 配置里

默认模板会把同一个平台 token 同时回写到：

- `xiaodu`
- `xiaodu-iot`

建议直接以这个模板为起点：

[`xiaodu-mcp-oauth.template.json`](xiaodu-mcp-oauth.template.json)

最小示例：

```json
{
  "token_endpoint": "https://openapi.baidu.com/oauth/2.0/token",
  "client_id": "替换成你的AppKey",
  "client_secret": "替换成你的SecretKey",
  "refresh_token": "替换成你当前最新的refresh_token",
  "scope": "basic dueros",
  "mcporter_config": "~/.mcporter/mcporter.json",
  "targets": [
    {
      "server": "xiaodu",
      "container": "headers",
      "key": "ACCESS_TOKEN"
    },
    {
      "server": "xiaodu-iot",
      "container": "env",
      "key": "ACCESS_TOKEN"
    }
  ]
}
```

默认保存到：

```text
~/.mcporter/xiaodu-mcp-oauth.json
```

这里有个关键点：

- `~/.mcporter/mcporter.json` 是 `mcporter` 的系统配置默认路径，`mcporter` 自己会读它
- `~/.mcporter/xiaodu-mcp-oauth.json` 不是平台强制文件名，而是这套 skill 默认给刷新脚本使用的凭据文件路径
- 如果你想把凭据文件放在别处，可以，只要后续执行刷新脚本时把 `--config` 指到你的真实路径，或者设置 `XIAODU_MCP_OAUTH_CONFIG=/实际路径`
- OAuth 文件里的 `mcporter_config` 字段，决定了刷新后要回写哪一个 `mcporter.json`；如果你把 `mcporter` 配在别处，这里必须改成真实路径

刷新脚本对 OAuth 凭据文件的写回规则也要说明白：

- 默认情况下，脚本会把新的 `refresh_token`、`current_access_token`、`last_refresh` 等字段回写到 `~/.mcporter/xiaodu-mcp-oauth.json`
- 如果默认新文件不存在，但旧文件 `~/.mcporter/xiaodu-iot-oauth.json` 存在，脚本会回退到旧文件，并把更新结果写回旧文件
- 如果新旧两个默认文件都存在，脚本会更新当前实际使用的那一份，并把另一份同步成相同内容，避免新旧文件分叉
- 如果你通过 `--config /实际路径` 或 `XIAODU_MCP_OAUTH_CONFIG=/实际路径` 使用了自定义 OAuth 文件路径，脚本会回写你指定的那份文件；只有在默认新旧文件也存在时，才会顺手同步默认兼容文件

建议权限：

```bash
chmod 600 ~/.mcporter/mcporter.json ~/.mcporter/xiaodu-mcp-oauth.json
```

这里有一个很重要的边界：

- `xiaodu-control` skill 可以分发
- 但 `AppKey / SecretKey / refresh_token / ACCESS_TOKEN` 不能跟 skill 一起公开分发

每个安装者都必须在自己的机器上填写自己的值。

默认模板会在刷新 token 时同时回写：

- `mcpServers.xiaodu.headers.ACCESS_TOKEN`
- `mcpServers.xiaodu-iot.env.ACCESS_TOKEN`

如果你的部署确实要求两套不同 token，可以修改 `targets`，只保留你想自动回写的那一边。

## 第四步：验证配置

### 验证智能屏 MCP

```bash
mcporter list xiaodu --schema
mcporter call xiaodu.list_user_devices --output json
```

### 验证 IoT MCP

```bash
mcporter list xiaodu-iot --schema
mcporter call xiaodu-iot.GET_ALL_DEVICES_WITH_STATUS --output json
```

## 第五步：接入自动刷新

先明确原则：

- 如果你是“自己机器上自己用”，就在自己的机器上装自动刷新
- 如果你们多人共用同一个 OpenClaw / Gateway 主机，只需要那台主机装一次自动刷新
- 如果每个人都各自安装 OpenClaw，就每个人各自装自己的自动刷新

这个 skill 不再内置某个平台专属的自动安装脚本。推荐做法是：在你自己的调度器里，每天执行一次刷新命令。

```bash
bash ~/.openclaw/skills/xiaodu-control/scripts/refresh_xiaodu_mcp_token.sh --refresh-if-within-days 7
```

如果你的 OAuth 凭据文件不在默认路径，也可以这样跑：

```bash
bash ~/.openclaw/skills/xiaodu-control/scripts/refresh_xiaodu_mcp_token.sh \
  --config /path/to/xiaodu-mcp-oauth.json \
  --refresh-if-within-days 7
```

或者：

```bash
XIAODU_MCP_OAUTH_CONFIG=/path/to/xiaodu-mcp-oauth.json \
bash ~/.openclaw/skills/xiaodu-control/scripts/refresh_xiaodu_mcp_token.sh --refresh-if-within-days 7
```

### Linux

可以把上面的命令接到你的 `cron` 或 `systemd timer`。

### Windows

建议把下面这条命令接到计划任务：

```text
python %USERPROFILE%\.openclaw\skills\xiaodu-control\scripts\refresh_xiaodu_mcp_access_token.py --config %USERPROFILE%\.mcporter\xiaodu-mcp-oauth.json --refresh-if-within-days 7
```

## 第六步：刷新后的验证

每次自动刷新或手动刷新后，都可以用这几条验证：

```bash
mcporter list xiaodu --schema
mcporter call xiaodu.list_user_devices --output json

mcporter list xiaodu-iot --schema
mcporter call xiaodu-iot.GET_ALL_DEVICES_WITH_STATUS --output json
```

## 常见边界

- `xiaodu` 智能屏 MCP 走 HTTP MCP
- `xiaodu-iot` 走官方 `dueros-iot-mcp` 的 stdio server
- 两个 server 虽然配置形式不同，但通常可以复用同一个小度 MCP 平台 `ACCESS_TOKEN`
- 这套 skill 默认用 `~/.mcporter/xiaodu-mcp-oauth.json` 存放刷新凭据，但这只是默认值，不是平台强制名称
- 如果 `npx -y dueros-iot-mcp` 首次启动很慢，先耐心等一次；如果握手仍然超时，再看 [`troubleshooting.md`](troubleshooting.md)
- 如果 `refresh_token` 成功刷新过一次，必须保存新返回的 `refresh_token`
- 不要把 `AppKey / SecretKey / refresh_token` 跟 skill 一起公开分发
