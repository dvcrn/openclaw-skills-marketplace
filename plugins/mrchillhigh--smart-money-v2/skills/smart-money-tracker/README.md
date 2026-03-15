# Smart Money Tracker - OpenClaw Skill

聪明钱追踪系统 - 每次调用需支付 0.001 USDT

## 功能特性

### 1. 大额交易追踪
- **实时监控** - 追踪链上超过设定阈值的大额转账
- **多币种支持** - 支持 ETH, USDT, USDC, BNB, SOL 等主流代币
- **阈值设置** - 可自定义触发金额阈值

### 2. 巨鲸地址监控
- **已知巨鲸库** - 内置知名巨鲸/机构地址列表
- **地址监控** - 监控特定地址的转入转出
- **异常行为检测** - 检测大额/异常交易

### 3. 机构资金流向
- **机构追踪** - 追踪做市商/机构的资金动向
- **交易所监控** - 监控交易所充提行为
- **净流入分析** - 计算各币种净流入/流出

### 4. 代币持仓分析
- **多链持仓** - 查询地址在各链的代币持仓
- **持仓分布** - 分析持仓代币的分布情况
- **价值估算** - 按当前价格估算持仓价值

### 5. 历史交易记录
- **交易历史** - 查询指定地址的历史交易
- **时间筛选** - 支持按时间范围筛选
- **交易类型** - 区分充值、提现、DEX交易

### 6. 趋势分析
- **资金流向** - 24h/7d/30d 资金流向趋势
- **热力图** - 显示活跃度热力图
- **对比分析** - 多地址/多币种对比

## 部署到 ClawHub

### 安装 CLI
```bash
npm i -g clawhub
```

### 登录
```bash
clawhub login
```

### 发布技能
```bash
cd smart-money-tracker
clawhub publish ./ --slug smart-money-tracker --name "Smart Money Tracker" --version 1.0.0 --tags latest
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SKILLPAY_API_KEY | SkillPay API Key | sk_4fcce5e... |
| SKILL_ID | 技能ID | 9eb32e1d-... |
| DEBUG | 调试模式 | true |

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/transactions/large` | GET | 获取大额交易 |
| `/api/whale/{address}` | GET | 追踪巨鲸地址 |
| `/api/flow/{chain}` | GET | 资金流向分析 |
| `/api/portfolio/{address}` | GET | 持仓分析 |
| `/api/history/{address}` | GET | 历史交易记录 |
| `/api/trend/{token}` | GET | 趋势分析 |
| `/api/watchlist` | POST | 添加监控 |

## 价格说明

- 每次 API 调用：**0.001 USDT**
- 支付通过 SkillPay 安全处理
- 支持 USDT TRC20 网络支付

## 技术栈

- **后端**: Python FastAPI
- **支付**: SkillPay.me API

## 目录结构

```
smart-money-tracker/
├── SKILL.md              # 技能说明文件
├── README.md             # 说明文档
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
└── api/
    └── main.py          # 主应用程序
```
