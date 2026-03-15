---
name: probable-skill
description: "0xProbable prediction market trading skills on BSC mainnet. Trade outcome shares (YES/NO) on real-world events via CLOB order book using @prob/clob SDK. Supports event search, orderbook queries, limit/market orders, position tracking with PnL, and Gnosis Safe proxy wallet withdrawals."
---

# 0xProbable Markets CLOB Skills

基于 bun 运行时的 0xProbable CLOB 交易工具集 (BSC 链)。

## 环境检查（首次使用必读）

在执行任何脚本之前，请先检查 `scripts/` 目录是否存在：

```bash
ls scripts/config.ts 2>/dev/null && echo "scripts 目录已就绪" || echo "scripts 目录缺失，请执行下方 clone 命令"
```

如果 `scripts/` 目录不存在或缺失关键文件，请克隆仓库：

```bash
git clone git@github.com:user/0xprobableskills.git && cd 0xprobableskills
```

> **注意**：所有命令均需在仓库根目录（包含 `scripts/` 和 `package.json` 的目录）下执行。

## 前置条件

1. 安装 bun（如已安装则跳过）：
   ```bash
   command -v bun >/dev/null 2>&1 && echo "bun 已安装: $(bun --version)" || { curl -fsSL https://bun.sh/install | bash && source ~/.bashrc; }
   ```
2. 创建 `.env` 文件：
   ```
   PRIVATE_KEY=<你的钱包私钥>
   ```

> bun 具备 auto-install 能力，无需手动 `bun add / bun install`，依赖版本由 `package.json` 和 `bun.lock` 锁定。

> **安全提醒**：PRIVATE_KEY 拥有钱包完全控制权，切勿泄露。确保 `.env` 已加入 `.gitignore`。

## 网站前置步骤

使用前必须在 0xProbable Markets 网站上完成：

1. **注册账户** — 前往 0xProbable Markets 注册登录
2. **Enable Trading** — 链上创建 proxy wallet (Gnosis Safe)，完成 USDT 授权
3. **充值 USDT** — 向 proxy wallet 充值（BSC 链 USDT）

完成后获得 `PRIVATE_KEY`，填入 `.env` 即可。

## 入门流程

1. 填写 `.env`（PRIVATE_KEY）
2. `bun run scripts/check-balance.ts` — 确认 USDT 余额充足
3. `bun run scripts/search.ts <关键词>` — 搜索感兴趣的市场
4. `bun run scripts/get-event.ts <event_id>` — 获取事件详情和 tokenId
5. 开始交易

## 命令速查

```bash
bun run scripts/check-balance.ts                                    # 检查余额 (USDT + BNB)
bun run scripts/search.ts <关键词> [--limit <n>] [--json]           # 搜索市场
bun run scripts/list-events.ts [--limit <n>] [--offset <n>] [--json]  # 浏览事件列表
bun run scripts/list-tags.ts <event_id> [--json]                    # 获取事件标签
bun run scripts/get-event.ts <event_id_or_slug> [--json]            # 获取事件详情
bun run scripts/get-market.ts <market_id> [--json]                  # 获取市场详情
bun run scripts/price-info.ts <token_id> [--json]                   # 获取价格信息
bun run scripts/price-history.ts <token_id> [--interval <interval>] # 历史价格
bun run scripts/orderbook.ts <token_id> [--json]                    # 查看订单簿
bun run scripts/buy.ts --token <ID> --price <P> --size <S>          # 限价买入
bun run scripts/sell.ts --token <ID> --price <P> --size <S>         # 限价卖出
bun run scripts/check-orders.ts [--event <EVENT_ID>]                # 查看挂单
bun run scripts/cancel-orders.ts --order <ID>                       # 取消订单
bun run scripts/positions.ts [--event <ID>] [--token <ID>] [--pnl]  # 查看持仓
bun run scripts/withdraw.ts [--amount <USDT>]                       # 从 proxy wallet 提取 USDT
```

## 脚本用法详解

### 1. 检查余额 — `check-balance.ts`

查询 EOA 和 Proxy Wallet 的 USDT 余额，以及 EOA 的 BNB 余额（Gas 费用）。

```bash
bun run scripts/check-balance.ts
```

输出：EOA 地址、Proxy Wallet 地址、两者的 USDT 余额、USDT 合计、BNB 余额。

> **注意**：BSC 上 USDT 使用 18 decimals（与 ETH 主网 6 decimals 不同）。

### 2. 搜索市场 — `search.ts`

```bash
bun run scripts/search.ts <关键词> [--limit <n>] [--json]
```

| 参数 | 说明 |
|------|------|
| `<关键词>` | 搜索关键词（必填） |
| `--limit <n>` | 返回数量 |
| `--json` | 输出原始 JSON |

**示例：**
- `bun run scripts/search.ts bitcoin`
- `bun run scripts/search.ts "US election" --limit 5`
- `bun run scripts/search.ts trump --json`

### 3. 浏览事件 — `list-events.ts`

```bash
bun run scripts/list-events.ts [--limit <n>] [--offset <n>] [--json]
```

| 参数 | 说明 |
|------|------|
| `--limit <n>` | 返回数量（默认 20） |
| `--offset <n>` | 跳过前 n 条（分页用） |
| `--json` | 输出原始 JSON |

**示例：**
- `bun run scripts/list-events.ts` — 默认列出 20 条事件
- `bun run scripts/list-events.ts --limit 10 --offset 20` — 第三页

### 4. 获取事件标签 — `list-tags.ts`

```bash
bun run scripts/list-tags.ts <event_id> [--json]
```

| 参数 | 说明 |
|------|------|
| `<event_id>` | 事件 ID（必填） |
| `--json` | 输出原始 JSON |

**示例：**
- `bun run scripts/list-tags.ts 752`

### 5. 获取事件详情 — `get-event.ts`

```bash
bun run scripts/get-event.ts <event_id_or_slug> [--json]
```

先尝试按 ID 查询，失败则按 slug 查询。输出事件标题、ID、状态、描述、市场列表及 tokenId。

**示例：**
- `bun run scripts/get-event.ts 752`
- `bun run scripts/get-event.ts bitcoin-price --json`

### 6. 获取市场详情 — `get-market.ts`

```bash
bun run scripts/get-market.ts <market_id> [--json]
```

### 7. 获取价格 — `price-info.ts`

```bash
bun run scripts/price-info.ts <token_id> [--json]
```

### 8. 历史价格 — `price-history.ts`

```bash
bun run scripts/price-history.ts <token_id> [--interval <interval>]
```

| 参数 | 说明 |
|------|------|
| `--interval` | 时间窗口 |

### 9. 订单簿 — `orderbook.ts`

```bash
bun run scripts/orderbook.ts <token_id> [--json]
```

获取完整 bids + asks，计算 spread 和中间价。

### 10. 买入 — `buy.ts`

```bash
bun run scripts/buy.ts --token <ID> --price <P> --size <S>
```

| 参数 | 说明 |
|------|------|
| `--token <ID>` | Token ID（从 get-event 获取） |
| `--price <P>` | 限价价格（0-1 之间） |
| `--size <S>` | Share 数量 |

下单自动设置 `feeRateBps=175`（最低手续费），订单类型 GTC（限价单）。

### 11. 卖出 — `sell.ts`

```bash
bun run scripts/sell.ts --token <ID> --price <P> --size <S>
```

参数同买入。

### 12. 查看挂单 — `check-orders.ts`

```bash
bun run scripts/check-orders.ts [--event <EVENT_ID>]
```

### 13. 取消订单 — `cancel-orders.ts`

```bash
bun run scripts/cancel-orders.ts --order <ID>
```

### 14. 查看持仓 — `positions.ts`

```bash
bun run scripts/positions.ts --event <EVENT_ID> [--pnl] [--trades] [--json]
```

| 参数 | 说明 |
|------|------|
| `--event <ID>` | 事件 ID（必填） |
| `--pnl` | 显示盈亏信息 |
| `--trades` | 显示交易记录 |
| `--json` | 输出原始 JSON |

**示例：**
- `bun run scripts/positions.ts --event 752` — 查看持仓
- `bun run scripts/positions.ts --event 752 --pnl` — 含盈亏
- `bun run scripts/positions.ts --event 752 --trades` — 含交易记录
- `bun run scripts/positions.ts --event 752 --pnl --trades --json` — 全部信息 JSON

### 15. 提取 USDT — `withdraw.ts`

```bash
bun run scripts/withdraw.ts [--amount <USDT>]
```

| 参数 | 说明 |
|------|------|
| `--amount <USDT>` | 提取金额（可选，默认提取全部） |

从 Proxy Wallet (Gnosis Safe) 提取 USDT 到 EOA。显示提取前后余额变化。

**示例：**
- `bun run scripts/withdraw.ts` — 提取全部 USDT
- `bun run scripts/withdraw.ts --amount 100` — 提取 100 USDT

## SDK 信息

| 项目 | 值 |
|------|-----|
| SDK | `@prob/clob` v0.5.0 |
| 链 | BSC 主网 (chainId: 56) |
| 抵押品 | USDT (18 decimals) |
| RPC | `https://bsc-dataseed.bnbchain.org` |

## 手续费

| 项目 | 说明 |
|------|------|
| Taker 费率 | 0.01% - 1.75% |
| feeRateBps | 175（下单时设置，对应最高 1.75%） |

> `feeRateBps=175n` 表示 175 基点 = 1.75%，这是平台允许的最低手续费设置值。实际成交费率可能更低。

## 订单类型

| 类型 | 全称 | 行为 |
|------|------|------|
| GTC | Good Till Cancelled | 限价单，挂单直到成交或手动取消 |
| IOC | Immediate or Cancel | 市价单，立即尽可能成交，剩余取消 |
| FOK | Fill or Kill | 市价单，必须全部成交否则整单取消 |

价格范围：0 到 1（概率），精度 0.01 递增。

## 错误参考

| 错误 | 说明 | 解决 |
|------|------|------|
| `PRIVATE_KEY not set` | 未配置私钥 | 在 `.env` 中设置 PRIVATE_KEY |
| `不是 proxy wallet 的 owner` | 签名地址非 Safe owner | 检查 PRIVATE_KEY 对应的地址 |
| 余额不足 | USDT 余额不够下单 | 充值或从 EOA 转入 proxy wallet |
| proxy wallet 不匹配 | 使用了错误的链 | 确保 chainId=56 (BSC 主网) |
| Gas 不足 | BNB 余额不够支付 Gas | 向 EOA 充值 BNB |

## 重要地址

| 名称 | 地址 |
|------|------|
| USDT (BSC) | `0x55d398326f99059ff775485246999027b3197955` |
| Proxy Wallet | `0xE1e2380cDe7d1822ACbD097E85f72040AB106f42` |
| EOA | `0xDDDddDcF23631d075C48e4669a5c0C227d5DdddD` |
