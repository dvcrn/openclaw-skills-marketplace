---
name: invassistant
description: "Investment portfolio trading signal checker based on a \"Three Red Lines\" entry system\n and a multi-layered exit system (take-profit, stop-loss, trend-break, momentum-fade, systemic-risk).\n This skill should be used when the user wants to check stock portfolio trading signals,\n verify entry/exit conditions for specific stocks, or configure automated signal alerts.\n It fetches real-time market data from Yahoo Finance, applies configurable strategy rules\n (emotion release, technical support, market risk for entry; take-profit tiers, stop-loss,\n trend-break, momentum-fade for exit), and pushes results to WeChat Work, DingTalk, or Feishu group bots.\n Trigger keywords: 检查持仓, 持仓信号, 今日信号, 红线检查, TSLA红线, 建仓检查,\n 减仓信号, 止盈检查, 止损检查, 退出信号, 清仓检查, 趋势破位, 动量衰竭,\n portfolio check, trading signal, entry check, exit check, red line check, stock signal,\n take profit, stop loss, 投资信号, 交易信号, 持仓检查, 详细分析."
---

# InvAssistant — 投资组合交易信号检查

基于「三条红线」入场过滤系统和「多层退出引擎」（止盈/止损/趋势破位/动量衰竭/系统性风险防守）的投资组合信号检查技能。通过 Yahoo Finance 获取实时数据，按配置化策略规则检查每个标的的**入场和退出信号**，支持推送结果到企微/钉钉/飞书群机器人。

## 核心概念：三条红线系统

三条红线是**过滤条件（Filter）**，不是评分制（Scoring）。全部通过才允许建仓，任何一条未通过即 NO-TRADE。

### 红线1：情绪释放型下跌（最关键）

触发条件（满足任一）：
- 单日跌幅 ≥ 4%（可配置）
- 连续 3 个交易日下跌（可配置）

没有情绪释放 → 没有情绪错配 → 没有入场理由。

### 红线2：技术止跌信号（严格标准）

需要**真实的止跌确认**，"接近均线"或"单次反弹"不算通过：
- 放量下跌后缩量（量能萎缩至前日 70% 以下）
- 均线强承接 = 下影线 + 收涨 + (放量 120%+ 或 强反弹 ≥ 1.5%)
- 完整 Higher Low 结构（低点A → 反弹 → 低点B > A → 2日确认）

### 红线3：市场未进入系统性风险

必须全部满足：
- QQQ 未连续 3 日暴跌
- SPX 未连续 3 日暴跌
- VIX < 25（可配置）

## 策略类型

| 类型 | 说明 | 入场逻辑 | 退出逻辑 |
|------|------|----------|----------|
| `redline` | 三条红线建仓，全通过后入场 | 情绪释放+技术止跌+市场环境 | 止盈分批减仓 / 止损清仓 / 趋势破位 / 动量衰竭 |
| `hold` | 永久持有，不加不减 | — | 仅系统性风险时防守（预警模式） |
| `pullback` | 回调达阈值时提示可小加 | 回调 ≥ 阈值 | 止盈减仓 / 止损清仓 / 趋势破位 |
| `satellite` | 卫星仓，不动 | — | 较紧止损线 + 宽止盈 |

## 退出信号系统

退出信号同样是**纪律驱动（Discipline）**，不是情绪驱动。按优先级从高到低排列：

### 止损清仓（优先级最高 — CRITICAL）

当浮亏超过止损线时**立即清仓**，不留余地。

- 默认止损线：-15%（redline标的）/ -12%（pullback标的）/ -20%（satellite标的）
- 可配置 `exit_params.stop_loss_pct`
- 一旦触发，跳过其他所有检查
- HOLD 标的默认不启用止损（仅系统性风险时防守）

### 止盈减仓（优先级高 — HIGH）

阶梯式止盈，分批锁利而非一次性出清：

| 浮盈达到 | 动作 | 说明 |
|----------|------|------|
| 20% | 减仓 1/3 | 第一阶梯止盈 |
| 40% | 再减 1/3 | 第二阶梯止盈 |
| 80% | 仅保留底仓 | 大幅止盈 |

- 阶梯可配置 `exit_params.take_profit_tiers`
- 需要配置 `exit_params.cost_basis`（持仓成本）才能生效

### 趋势破位（优先级高 — HIGH）

当价格有效跌破关键均线时减仓防守：

- 收盘价连续 N 日（默认3）低于 MA50
- 期间无明显承接信号（下影线+收涨+放量）
- 均线拐头向下
- 触发后减仓 50%（可配置）

### 动量衰竭（优先级中 — MEDIUM）

上涨趋势中出现动量减弱的早期预警：

- 创新高/近新高但成交量显著萎缩（量价背离）
- 连续多日量能递减
- MACD 顶背离（价格新高但 MACD 柱缩短）
- 触发后减仓 1/3（可配置）

### 系统性风险防守（全组合层级 — 可覆盖 HOLD）

这是**唯一可以覆盖「永久 HOLD」策略**的退出条件：

| 级别 | 条件 | 动作 |
|------|------|------|
| 预警 (WARNING) | VIX 接近恐慌阈值 (≥25.5) | 提高警惕，准备方案 |
| 恐慌 (PANIC) | VIX ≥ 30 或 QQQ/SPX 连续3日暴跌 | 非核心仓减半 |
| 极端 (EXTREME) | VIX ≥ 40 | 全组合减至 50% |

## 工作流程

### Step 1: 确认配置

1. 读取工作区中的 `invassistant-config.json` 配置文件
2. 如不存在，执行 `python scripts/init_config.py` 生成默认配置
3. 确认关注标的列表和策略参数

配置文件核心结构：
- `portfolio.watchlist` — 关注标的列表（symbol, name, strategy, params, exit_params）
- `portfolio.watchlist[].exit_params` — 退出条件参数（cost_basis, stop_loss_pct, take_profit_tiers 等）
- `portfolio.systemic_risk_exit` — 系统性风险防守退出参数（VIX 恐慌/极端阈值）
- `portfolio.vix_threshold` — VIX 入场阈值（默认 25）
- `adapters` — 推送渠道（wechatwork / dingtalk / feishu）
- `commands` — 指令映射（群机器人指令 → 动作）

### Step 2: 执行检查

根据用户指令选择执行模式：

**全组合检查**（"检查持仓" / "今日信号"）：
```bash
python scripts/portfolio_checker.py
```

**单标的详细分析**（"TSLA红线" / "详细分析"）：
```bash
python scripts/portfolio_checker.py --detail TSLA
```

**检查并推送**（"检查并推送" / "推送信号"）：
```bash
python scripts/portfolio_checker.py --push
```

### Step 3: 解读输出

检查结果按标的输出**入场信号**和**退出信号**，格式如下：
- `redline` 标的：显示三条红线逐条判定结果和最终结论 + 退出信号检查
- `pullback` 标的：显示回调幅度和是否达到阈值 + 退出信号检查
- `hold` / `satellite` 标的：显示当前价格和持仓指令 + 退出预警

退出信号按优先级标注：
- 🔴 CRITICAL — 止损清仓（立即执行）
- 🟠 HIGH — 止盈减仓 / 趋势破位（尽快执行）
- 🟡 MEDIUM — 动量衰竭（观察并准备）

全组合自检汇总五个问题：
1. 是否出现情绪错配资产？（redline 标的全通过）
2. 是否出现核心仓被迫低估？（pullback 标的达标）
3. 是否有标的触发退出信号？（止损/止盈/破位/动量）
4. 是否出现系统性风险？（VIX 恐慌 + 市场连续暴跌）
5. 综合结论：入场 / 退出 / 不交易

### Step 4: 推送（按配置）

根据 `invassistant-config.json` 中的 `adapters` 配置推送结果：

1. **企业微信**：`scripts/send_wecom.py` — Markdown 消息推送
2. **钉钉**：`scripts/send_dingtalk.py` — Markdown + 加签安全验证
3. **飞书**：`scripts/send_feishu.py` — 富文本(post) 或 交互卡片模式

每个推送脚本支持 `--test` 参数发送测试消息验证配置。

## 配置指南

### 修改关注股票

编辑 `invassistant-config.json` 中的 `portfolio.watchlist`：

```json
{
  "symbol": "TSLA",
  "name": "特斯拉",
  "strategy": "redline",
  "params": {
    "emotion_drop_threshold": -4,
    "consecutive_days": 3,
    "bounce_threshold": 1.5,
    "volume_ratio": 1.2,
    "entry_size": 0.3
  }
}
```

添加新标的：在 watchlist 数组中追加条目，指定 strategy 类型和参数。
删除标的：从 watchlist 数组中移除对应条目。

### 配置退出条件

编辑 `invassistant-config.json` 中每个标的的 `exit_params`：

```json
{
  "symbol": "TSLA",
  "strategy": "redline",
  "params": { ... },
  "exit_params": {
    "cost_basis": 250.00,
    "position_size": 100,
    "take_profit_enabled": true,
    "take_profit_tiers": [
      {"gain_pct": 20, "action": "减仓1/3", "reduce_pct": 33, "label": "第一阶梯"},
      {"gain_pct": 40, "action": "再减1/3", "reduce_pct": 33, "label": "第二阶梯"}
    ],
    "stop_loss_enabled": true,
    "stop_loss_pct": -15,
    "stop_loss_action": "清仓",
    "trend_break_enabled": true,
    "trend_break_ma": 50,
    "trend_break_confirm_days": 3,
    "trend_break_action": "减仓50%",
    "momentum_fade_enabled": true,
    "momentum_action": "减仓1/3"
  }
}
```

**重要**：填入 `cost_basis`（持仓成本价）后止盈/止损检查才会生效。

配置系统性风险防守退出（全组合层级）：
```json
{
  "portfolio": {
    "systemic_risk_exit": {
      "enabled": true,
      "vix_panic_threshold": 30,
      "vix_extreme_threshold": 40,
      "market_consecutive_drop_days": 3,
      "market_drop_magnitude": -2,
      "panic_action": "非核心仓减半",
      "extreme_action": "全组合减至50%"
    }
  }
}
```

### 配置推送渠道

在 `adapters` 中启用渠道并填入 Webhook URL：

| 渠道 | 配置键 | 主要配置项 | 环境变量 |
|------|--------|-----------|----------|
| 企业微信 | `wechatwork` | `webhook_url` | `WECOM_WEBHOOK_URL` |
| 钉钉 | `dingtalk` | `webhook_url`, `secret` | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| 飞书 | `feishu` | `webhook_url`, `secret` | `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET` |

### 配置指令接收

通过群机器人接收指令触发检查（需配合 WorkBuddy Automation 或外部定时任务）：

在 `commands` 中映射指令到动作：
```json
{
  "检查持仓": "full_check",
  "TSLA红线": "tsla_detail",
  "今日信号": "full_check"
}
```

企微/钉钉/飞书群中 @机器人 + 指令文本 → 触发对应检查动作。

## 快捷入口

保留的兼容入口脚本（在项目根目录）：
- `check_portfolio.py` — 全组合检查
- `check_tsla_entry.py` — TSLA 红线检查
- `check_detail.py` — TSLA 详细分析
