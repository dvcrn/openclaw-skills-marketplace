# InvAssistant — 投资组合交易信号检查系统

一个 CodeBuddy/WorkBuddy Skill，基于可配置的**「三条红线」入场过滤系统**和**「多层退出引擎」**检查投资组合交易信号。通过 Yahoo Finance 获取实时行情数据，按策略规则检查每个标的的建仓/加仓/减仓/清仓信号，并推送到企业微信、钉钉或飞书群机器人。

## 核心特性

- **三条红线入场系统** — 情绪释放、技术止跌、市场风险三重过滤条件（不是评分制）
- **多层退出引擎** — 止盈分批减仓、止损清仓、趋势破位、动量衰竭、系统性风险防守
- **配置化关注列表** — 通过 JSON 配置文件管理关注股票、入场/退出策略、参数阈值
- **多渠道推送** — 检查结果推送到企微/钉钉/飞书群机器人
- **指令触发** — 在群里 @机器人 发指令即可触发检查
- **模块化架构** — 数据获取、红线引擎、退出引擎、组合检查器独立模块

## 快速开始

### 1. 安装

```bash
# 复制到 CodeBuddy skills 目录
cp -r invassistant-skill ~/.codebuddy/skills/invassistant

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化配置

```bash
python scripts/init_config.py
```

生成 `invassistant-config.json` 默认配置文件。编辑该文件自定义你的关注列表和推送渠道。

### 3. 运行

```bash
# 全组合检查
python check_portfolio.py

# TSLA 详细分析
python check_tsla_entry.py

# 检查并推送结果
python scripts/portfolio_checker.py --push
```

或者直接对 CodeBuddy 说："检查持仓信号" / "TSLA红线检查" / "今日信号"

## 配置说明

所有配置集中在 `invassistant-config.json` 一个文件中。

### 📋 关注股票列表

配置位置：`portfolio.watchlist`

```json
{
  "portfolio": {
    "watchlist": [
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
        },
        "exit_params": {
          "cost_basis": 0,
          "take_profit_enabled": true,
          "take_profit_tiers": [
            {"gain_pct": 20, "action": "减仓1/3", "reduce_pct": 33},
            {"gain_pct": 40, "action": "再减1/3", "reduce_pct": 33}
          ],
          "stop_loss_enabled": true,
          "stop_loss_pct": -15,
          "trend_break_enabled": true,
          "trend_break_ma": 50,
          "momentum_fade_enabled": true
        }
      },
      {
        "symbol": "NVDA",
        "name": "英伟达",
        "strategy": "hold",
        "exit_params": {
          "cost_basis": 0,
          "take_profit_enabled": false,
          "stop_loss_enabled": false,
          "trend_break_enabled": true,
          "trend_break_action": "预警（HOLD标的不减仓）"
        }
      },
      {
        "symbol": "GOOGL",
        "name": "谷歌",
        "strategy": "pullback",
        "params": { "pullback_threshold": 0.06 },
        "exit_params": {
          "cost_basis": 0,
          "stop_loss_pct": -12
        }
      }
    ]
  }
}
```

**策略类型说明：**

| 类型 | 入场逻辑 | 退出逻辑 |
|------|----------|----------|
| `redline` | 三条红线全部通过 → 建仓30% | 止盈分批减仓 / 止损清仓(-15%) / 趋势破位 / 动量衰竭 |
| `hold` | 不加不减，稳定器 | 仅系统性风险时防守（趋势破位/动量衰竭仅预警不减仓） |
| `pullback` | 回调 ≥ 阈值时可小加 | 止盈减仓 / 止损清仓(-12%) / 趋势破位 / 动量衰竭 |
| `satellite` | 不动 | 较紧止损(-20%) + 宽止盈(30%) |

**添加新标的**：在 `watchlist` 数组末尾追加一个对象即可。
**删除标的**：从数组中删除对应对象。
**修改参数**：编辑 `params` 中的数值。

### 📤 推送到企微/钉钉/飞书

配置位置：`adapters`

#### 企业微信

```json
{
  "adapters": {
    "wechatwork": {
      "enabled": true,
      "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
    }
  }
}
```

**获取 Webhook URL**：企微群 → 群设置 → 群机器人 → 添加自定义机器人 → 复制 Webhook 地址

#### 钉钉

```json
{
  "adapters": {
    "dingtalk": {
      "enabled": true,
      "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
      "secret": "SEC_YOUR_SECRET"
    }
  }
}
```

**获取 Webhook URL**：钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义

**安全设置**（三选一）：
- 加签：填入 `secret` 字段
- 自定义关键词：设 "信号" "持仓" "检查"
- IP 白名单：填服务器 IP

#### 飞书

```json
{
  "adapters": {
    "feishu": {
      "enabled": true,
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK",
      "secret": "YOUR_SECRET"
    }
  }
}
```

**获取 Webhook URL**：飞书群 → 设置 → 群机器人 → 添加机器人 → 自定义机器人

**安全设置**：签名校验（推荐），填入 `secret`

#### 环境变量（优先级高于配置文件）

| 渠道 | 环境变量 |
|------|----------|
| 企微 | `WECOM_WEBHOOK_URL` |
| 钉钉 | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| 飞书 | `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET` |

#### 测试推送

```bash
python scripts/send_wecom.py --test
python scripts/send_dingtalk.py --test
python scripts/send_feishu.py --test
```

### 🤖 通过群机器人发指令

配置位置：`commands`

```json
{
  "commands": {
    "检查持仓": "full_check",
    "今日信号": "full_check",
    "TSLA红线": "tsla_detail",
    "详细分析": "tsla_detail",
    "帮助": "help"
  }
}
```

**使用方式**：在群里 @机器人 + 指令文本（如 "@InvBot 检查持仓"）

**配合 WorkBuddy Automation 使用**：

可以创建定时任务，每个工作日自动执行检查并推送：

```
频率: 每周一至周五
时间: 北京时间 09:30 (美股盘前)
命令: python scripts/portfolio_checker.py --push
```

**配合企微/钉钉/飞书 Outgoing Webhook**：

若需要在群里 @机器人 实时触发检查，需要：
1. 在群机器人后台配置 Outgoing Webhook（消息回调 URL）
2. 部署一个接收端服务（如 Flask/FastAPI），解析指令并调用 `portfolio_checker.py`
3. 具体接入方式参考各平台文档：
   - [企微群机器人回调](https://developer.work.weixin.qq.com/document/path/99110)
   - [钉钉 Outgoing 机器人](https://open.dingtalk.com/document/orgapp/custom-robots-send-group-messages)
   - [飞书自定义机器人事件回调](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)

## 项目结构

```
invassistant-skill/
├── SKILL.md                    # Skill 核心定义（触发词、工作流、逻辑说明）
├── invassistant-config.json    # 你的配置文件（gitignored，含 webhook 密钥）
├── check_portfolio.py          # 快捷入口: 全组合检查
├── check_tsla_entry.py         # 快捷入口: TSLA 红线检查
├── check_detail.py             # 快捷入口: TSLA 详细分析
├── scripts/
│   ├── init_config.py          # 初始化默认配置
│   ├── data_fetcher.py         # Yahoo Finance 数据获取（重试+限流）
│   ├── redline_engine.py       # 三条红线入场引擎（可配置参数）
│   ├── exit_engine.py          # 退出引擎（止盈/止损/趋势破位/动量衰竭/系统性风险）
│   ├── portfolio_checker.py    # 组合检查主程序（入场+退出信号分发+报告格式化）
│   ├── send_wecom.py           # 企业微信推送
│   ├── send_dingtalk.py        # 钉钉推送（支持加签）
│   └── send_feishu.py          # 飞书推送（富文本/卡片）
├── Q1_2026_交易策略.md          # 策略参考文档
├── requirements.txt            # Python 依赖
├── LICENSE                     # MIT 协议
├── CONTRIBUTING.md             # 贡献指南
└── README_zh.md                # 本文件
```

## 三条红线详解（入场系统）

> **红线是过滤条件（Filter），不是评分制（Scoring）。全部通过才可建仓，任何一条未通过 = NO-TRADE。**

### 🔴 红线1：情绪释放型下跌（最关键）

满足任一即通过：
- 单日跌幅 ≥ 4%（可配置 `emotion_drop_threshold`）
- 连续 3 天下跌（可配置 `consecutive_days`）

**没有情绪释放 → 没有情绪错配 → 没有入场理由。**

### 🔴 红线2：技术止跌信号（严格标准）

需要**真实的止跌确认**：
- 放量下跌后缩量（量能萎缩至前日 70% 以下）
- 均线强承接 = 下影线 + 收涨 + (放量 120%+ 或 强反弹 ≥ 1.5%)
- 完整 Higher Low 结构（低点A → 反弹 → 低点B > A → 2日确认）

⚠️ 注意区分：
- "价格接近均线" = 趋势中性，**不是**止跌
- "一次反弹" = 技术反弹，**不是** Higher Low
- 真正的止跌需要：下影线 + 放量承接 + 强反弹

### 🔴 红线3：市场未进入系统性风险

必须全部满足：
- QQQ 未连续 3 日暴跌
- SPX 未连续 3 日暴跌
- VIX < 25（可配置 `vix_threshold`）

## 退出系统详解

> **退出信号同样是纪律驱动（Discipline），不是情绪驱动。按优先级检查，高优先级触发后跳过低优先级。**

### 🔴 止损清仓 — 优先级 CRITICAL

浮亏超过止损线时**立即清仓**，不留余地。

| 策略类型 | 默认止损线 | 说明 |
|----------|-----------|------|
| `redline` | -15% | 建仓后若持续下跌，果断止损 |
| `pullback` | -12% | 核心标的止损稍紧 |
| `satellite` | -20% | 卫星仓允许更大波动 |
| `hold` | 不启用 | 仅在系统性风险时防守 |

配置：`exit_params.stop_loss_pct`

**重要**：需要配置 `exit_params.cost_basis`（持仓成本价）才能生效。

### 🟢 止盈减仓 — 优先级 HIGH

阶梯式止盈，**分批锁利**而非一次性出清，避免过早离场又避免利润回吐：

| 浮盈达到 | 默认动作 | 说明 |
|----------|---------|------|
| 20% | 减仓 1/3 | 锁定部分利润 |
| 40% | 再减 1/3 | 进一步锁利 |
| 80% | 仅保留底仓 | 大幅盈利后保留底仓追趋势 |

配置：`exit_params.take_profit_tiers`（可自定义阶梯数量和比例）

### 📊 趋势破位 — 优先级 HIGH

当价格**有效跌破**关键均线时减仓防守。"有效"的定义是避免假突破：

- 收盘价连续 N 日（默认 3）低于 MA50
- 期间**无**明显承接信号（下影线+收涨+放量）
- 均线拐头向下

触发后默认减仓 50%。HOLD 标的仅做预警，不实际减仓。

配置：`exit_params.trend_break_ma`, `exit_params.trend_break_confirm_days`

### 📉 动量衰竭 — 优先级 MEDIUM

上涨趋势中出现动量减弱的**早期预警**，用于在趋势反转前主动减仓：

- **量价背离**：创新高/近新高但成交量显著萎缩（近5日均量 < 20日均量的70%）
- **连续缩量**：量能连续递减超过阈值天数
- **MACD 顶背离**：价格创新高但 MACD 柱缩短

触发后默认减仓 1/3。

### 🛡️ 系统性风险防守 — 全组合层级

这是**唯一可以覆盖「永久 HOLD」策略**的退出条件。当市场进入系统性风险时，保护整个组合：

| 级别 | 触发条件 | 动作 |
|------|---------|------|
| ⚠️ 预警 | VIX 接近恐慌阈值 (≥25.5) | 提高警惕，准备防守方案 |
| 🟠 恐慌 | VIX ≥ 30 或 QQQ/SPX 连续3日每日跌≥2% | 非核心仓减半 |
| 🔴 极端 | VIX ≥ 40 | 全组合减至50% |

配置：`portfolio.systemic_risk_exit`

## 协议

MIT License - 见 [LICENSE](LICENSE)
