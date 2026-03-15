# 12306 API Client

一个基于 Python 的 12306 命令行脚本，支持：

- 登录（含短信验证码流程）
- 登录状态检查（已登录时返回用户关键信息）
- 查询当前账号乘车人信息
- 查询余票
- 查询中转车票
- 查询经停站
- 查询订单
- 查询候补排队状态
- 查询候补订单（进行中/已处理）
- 订票（提交订单并轮询订单号）
- 支付信息获取（尝试生成支付链接）

脚本文件：`client.py`

## 环境要求

- Python 3.9+
- 依赖：`requests`

安装依赖：

```bash
pip install requests
```

## 快速开始

先看帮助：

```bash
python3 client.py -h
python3 client.py book -h
python3 client.py transfer-ticket -h
python3 client.py route -h
python3 client.py candidate-orders -h
```

## 常用命令

### 1) 登录

先发短信验证码：

```bash
python3 client.py login --username <账号> --id-last4 <证件后4位> --send-sms
```

再带验证码登录：

```bash
python3 client.py login --username <账号> --id-last4 <证件后4位> --sms-code <6位验证码>
```

也可以直接传密码（不传则会交互输入，或读取 `KYFW_PASSWORD`）：

```bash
python3 client.py login --username <账号> --password <密码>
```

### 2) 查询登录状态

```bash
python3 client.py status
```

如果已登录，输出会包含：

- `登录状态`
- `user` 关键信息（如 `name`、`username`、`email`、`mobile`，按接口返回为准）

JSON 输出：

```bash
python3 client.py status --json
```

### 3) 查询余票

```bash
python3 client.py left-ticket --date 2026-03-23 --from 宁波 --to 宜春
```

可选参数：

- `--endpoint queryG|queryZ`（默认 `queryG`）
- `--purpose ADULT`（默认 `ADULT`）
- `--limit`（控制展示行数）

### 4) 查询中转车票

```bash
python3 client.py transfer-ticket --date 2026-03-23 --from 南部 --to 成都东
```

可选参数：

- `--middle`（指定换乘站，可不传）
- `--result-index`（分页游标，默认 `0`）
- `--can-query Y|N`（是否继续查询更多方案，默认 `Y`）
- `--show-wz`（显示无座方案；默认不显示）
- `--purpose`（乘客类型编码，默认 `00`）
- `--channel`（默认 `E`）
- `--endpoint queryG|queryZ`（默认 `queryG`）
- `--limit`（控制展示行数）

JSON 输出：

```bash
python3 client.py transfer-ticket --date 2026-03-23 --from NBE --to ICW --json
```

### 5) 查询经停站

```bash
python3 client.py route --train-code C956 --date 2026-03-23 --from 南部 --to 南充北
```

可选参数：

- `--train-code`（车次号，如 `C956`；会自动解析 `train_no`）
- `--train-no`（直接传列车内部 `train_no`）
- `--endpoint queryG|queryZ`（`--train-code` 模式下用于解析，默认 `queryG`）
- `--purpose`（`--train-code` 模式下用于解析，默认 `ADULT`）
- `--limit`（最多展示多少站，默认 `200`）
- `--json`（输出原始 JSON）

参数说明：

- `--train-no` 和 `--train-code` 二选一，至少传一个。
- 传 `--train-code` 时，脚本会先走一次余票查询自动解析 `train_no`。

### 6) 查询当前账号乘车人

```bash
python3 client.py passengers
```

可选参数：

- `--limit`（最多展示多少个乘车人）
- `--json`（输出原始 JSON）

### 7) 查询订单

```bash
python3 client.py orders --where G
```

说明：

- `--where G`：未出行/近期
- `--where H`：历史订单

若 cookie 未登录，可额外提供 `--username`（及必要时的登录参数）自动补登录。

### 8) 候补相关查询

候补排队状态：

```bash
python3 client.py candidate-queue
```

候补订单（默认查进行中）：

```bash
python3 client.py candidate-orders
```

查已处理候补订单：

```bash
python3 client.py candidate-orders --processed --start-date 2026-03-11 --end-date 2026-04-09
```

可选参数：

- `candidate-orders --processed`（查已处理记录，不加则查进行中）
- `candidate-orders --page-no`（页码，默认 `0`）
- `candidate-orders --start-date/--end-date`（日期区间）
- `candidate-orders --limit`（文本输出最多展示条数）

说明：

- 候补命令需要登录态（可沿用已有 cookie）。
- 若 cookie 失效，可额外传 `--username`（及必要时登录参数）自动补登录。

### 9) 订票

先建议用 `--dry-run` 做预检（不提交最终排队确认）：

```bash
python3 client.py book \
  --date 2026-03-23 \
  --from 宁波 \
  --to 宜春 \
  --train-code G1234 \
  --seat second_class \
  --passengers 张三 \
  --dry-run
```

确认后正式提交：

```bash
python3 client.py book \
  --date 2026-03-23 \
  --from 宁波 \
  --to 宜春 \
  --train-code G1234 \
  --seat second_class \
  --passengers 张三
```

说明：

- 当前链路可以稳定完成下单并拿到订单号。
- 脚本会尝试调用 `payOrder/paycheckNew` 返回支付链接参数。
- 实测支付环节可能无法在网页链路完成，建议在 12306 App 的“待支付订单”中完成支付。

多个乘客用逗号分隔：

```bash
--passengers 张三,李四
```

常用席别写法：

- 英文：`second_class`、`first_class`、`business`
- 中文：`二等座`、`一等座`、`硬卧` 等
- 代码：`O`、`M`、`9`、`3`、`4`、`1` 等

## 全局参数

- `--base-url`：默认 `https://kyfw.12306.cn`
- `--timeout`：请求超时（秒）
- `--cookie-file`：cookie 持久化路径（默认 `~/.kyfw_12306_cookies.json`）
- `--no-browser-headers`：关闭浏览器风格请求头仿真（默认开启）
- `--json`：输出原始 JSON

## 订票流程说明

`book` 命令内部流程为：

1. 查询余票并定位目标车次
2. `submitOrderRequest`
3. `initDc` 解析 token 和关键字段
4. 拉取乘客列表并按姓名匹配
5. `checkOrderInfo`
6. `getQueueCount`
7. `confirmSingleForQueue`
8. 轮询 `queryOrderWaitTime` 获取订单号
9. `resultOrderForDcQueue`
10. `payOrder/init` + `payOrder/paycheckNew`（尝试生成支付链接）

## 注意事项

- 12306 风控较严格，可能出现 `error.html`、排队超时、或需要额外校验。
- 部分账号可能触发滑块/图片验证码（脚本当前不自动处理该场景）。
- 即使成功返回支付参数，网页侧也可能无法完成支付；请优先在 12306 App 的待支付订单中支付。
- 本工具仅供学习与自动化辅助，请遵守 12306 平台规则并控制请求频率。
