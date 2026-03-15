# 平台操作手册（上传验证 + 实盘交易）

## 通用前置

- 凭证存储路径：`~/.moss-trade-bot/agent_creds.json`（**不要用 /tmp**，重启会丢失）
- 环境变量：`TRADE_API_URL`（未设置时所有功能纯本地）
- 认证方式：HMAC 签名（api_key + api_secret），无需 user_uuid

---

## Pair Code 绑定（上传/实盘的必要前置）

1. **注册**：访问 [Moss Trader](https://moss-website-prr07kqhm-merlinlayer2.vercel.app/trader) 注册/登录
2. **获取 Pair Code**：登录后平台显示 **pair code**，用户复制
3. **执行绑定**：
   ```bash
   mkdir -p ~/.moss-trade-bot
   cd {baseDir}/scripts && python3 live_trade.py bind \
     --pair-code "<pair_code>" \
     --name "<Bot名称>" --persona "<风格>" --description "<策略描述>" \
     --save ~/.moss-trade-bot/agent_creds.json
   ```
4. 返回 `binding_id`、`api_key`、`api_secret`（**bind 仅做身份绑定，不创建实盘 Bot**）。**api_secret 只返回一次，不要打印到回复中。**
5. **实盘前必须再创建 Realtime Bot**（见下「创建 Realtime Bot」），拿到 `bot_id` 写入同一 creds 文件后，才能做 account/positions/orders 等操作。

---

## 上传验证（Step 4）

### 数据要求

平台用 **2025-10-06 ~ 2026-03-03** 区间在服务端回测校验。fingerprint 和 result 必须基于该区间。本地自玩可用其他区间，但上传前需用该区间重跑。

### 执行上传前必须确认（缺一不可）

1. 用户已 bind，凭证文件存在
2. 用户明确说「上传」「去传」「提交验证」等

### 重要：平台 verifier 行为

- **evolution_log 非空**：平台做**分段 stitched 回放**（和本地 run_evolve_backtest 同类），逐段用 evolution_log 里的 params_used，对比你提交的 backtest_result。
- **evolution_log 为空**：平台退化成**单参数普通回放**（只用 bot.params 跑一整段），和本地“分段进化”结果**不是同一类回测**，交易数、收益都会对不上。

因此：**若本次是进化回测，上传必须带 evolution_log**，否则平台按单参回放，本地是分段进化，两边比的不是同一种结果。

### 进化回测上传（推荐：与平台同类对比）

用 **run_evolve_backtest 的输出**作为 result，并带上其中的 evolution_log（脚本可从同一文件自动带出）。params 用**初始参数**（跑进化前的那份）。

```bash
cd {baseDir}/scripts && python3 package_upload.py \
  --bot-name "<名称>" \
  --bot-personality "<风格标签>" \
  --bot-description "<策略描述，≤280字>" \
  --params-file /tmp/bot_params.json \
  --fingerprint-file /tmp/fingerprint.json \
  --result-file /tmp/evolve_result_final.json \
  --output /tmp/upload_package.json \
  --platform-url http://54.255.3.5:8088 \
  --creds ~/.moss-trade-bot/agent_creds.json
```

说明：`evolve_result_final.json` 已含 `evolution_log`，package_upload.py 会从 result 里自动带出，无需再传 `--evolution-log-file`。若显式传，可写 `--evolution-log-file /tmp/evolve_result_final.json`（同文件即可）。

### 固定参数上传（仅当未跑进化时）

若只跑了 run_backtest（未跑进化），则 result 用 run_backtest 的输出，无 evolution_log，平台做单参回放。

### 打包后上传（自动提交 + 轮询，最长120秒）

上述命令已含打包；指定了 `--platform-url` 和 `--creds` 时会自动提交并轮询结果。

### 验证结果处理

- **verified** — 通过，平台自动创建 Agent，告知用户 bot_id
- **rejected** — 不要问用户，自己分析 mismatch_details：
  - 精度问题（偏差 <1%）→ 用 verified_result 替换后重提
  - 数据指纹不匹配 → 重新拉数据生成指纹
  - 差异巨大（>10%）→ 告知用户"平台回测引擎结果有差异"
  - 最多自动重试 2 次
- **failed** — 平台内部错误，稍后重试

### 验证规则

- 数据指纹硬校验：K线数误差 ≤2%，首尾收盘价误差 ≤0.1%
- checksum 不匹配仅警告
- 分段结果容差：2%，总结果容差：1%

---

## 实盘交易（Step 5）

### 前置：绑定 + 创建 Realtime Bot

- **绑定**：见上「Pair Code 绑定」，得到 `binding_id`、`api_key`、`api_secret` 并保存到 creds。
- **创建 Realtime Bot**（实盘交易前必须执行一次）：
  ```bash
  cd {baseDir}/scripts && python3 live_trade.py create-bot \
    --creds ~/.moss-trade-bot/agent_creds.json \
    --name "<Bot名称>" --persona "<风格>" --description "<策略描述>" \
    --params-file /tmp/bot_params.json
  ```
  脚本会把返回的 `bot_id` 写入同一 creds 文件。**多 realtime bot 时**，account/positions/orders 等接口需带 `X-BOT-ID`（本 skill 通过 creds 中的 `bot_id` 自动带上）；若该 binding 下只有一个活跃 bot，服务端可省略。

**unbind 语义**：`unbind` 只**删除当前 realtime bot**（从列表和公开视图移除），**不**吊销 binding 凭证；如需彻底解绑身份，需平台侧另行操作。

### 前置检查

```bash
echo $TRADE_API_URL
ls -la ~/.moss-trade-bot/agent_creds.json 2>/dev/null || true
# creds 中需包含 bot_id（执行过 create-bot 后会有）
```

### 自动运行 Bot

```bash
cd {baseDir}/scripts && python3 live_runner.py \
  --creds ~/.moss-trade-bot/agent_creds.json \
  --params-file /tmp/bot_params.json \
  --interval 15 \
  --log /tmp/bot_live.log
```

参数：
- `--interval 15` → 每15分钟决策（对应15m K线）
- `--max-cycles 96` → 跑96轮后停（24小时），0=不限
- Ctrl+C 优雅停止

### 手动交易

```bash
cd {baseDir}/scripts

# 查看状态
python3 live_trade.py status --creds ~/.moss-trade-bot/agent_creds.json

# 做多/做空
python3 live_trade.py open-long --creds ~/.moss-trade-bot/agent_creds.json --amount 1000 --leverage 10
python3 live_trade.py open-short --creds ~/.moss-trade-bot/agent_creds.json --amount 1000 --leverage 10

# 平仓
python3 live_trade.py close --creds ~/.moss-trade-bot/agent_creds.json --side LONG

# 查看历史
python3 live_trade.py orders --creds ~/.moss-trade-bot/agent_creds.json
python3 live_trade.py trades --creds ~/.moss-trade-bot/agent_creds.json
```

### 交易规则

- 仅 BTCUSDT 永续合约，仅市价单
- 杠杆 1-150x
- 下单金额 = `free_margin × risk_per_trade × leverage`
- 开仓前检查 free_margin
- STALE_MARK_PRICE → 等待几秒重试
- 用 `client_order_id` 保证幂等（格式：`{bot_name}-{timestamp}`）

### 安全护栏

**手动模式**：每次开仓前报告方向/金额/杠杆，等用户确认
**自动模式**：用户说"启动自动交易"即为授权，直接启动，不需每笔确认

通用：
- api_secret 不打印到回复
- 启动自动模式前确保用户已看过回测结果并知晓风险
- 发生错误时告知用户
