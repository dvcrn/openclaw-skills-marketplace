# Token Unlock Pro - OpenClaw Skill

专业的代币解锁预警系统 - 每次调用需支付 0.001 USDT

## 功能特性

### 1. 多时间维度预警
- **72小时预警** - 提前3天预警即将解锁的代币
- **48小时预警** - 提前2天预警
- **24小时预警** - 提前1天预警
- **6小时预警** - 提前6小时预警
- **实时监控** - 实时监控解锁事件

### 2. 类型分类系统
- **种子轮 (Seed)** - 种子轮投资者解锁
- **公募 (Public)** - 公开募资解锁
- **生态 (Ecosystem)** - 生态系统发展解锁
- **质押 (Staking)** - 质押奖励解锁
- **团队 (Team)** - 团队份额解锁
- **顾问 (Advisor)** - 顾问奖励解锁
- **社区 (Community)** - 社区激励解锁

### 3. 解锁额度分级
- **鲸鱼级 (Whale)** - 解锁价值 > $10,000,000
- **大型 (Large)** - 解锁价值 $1,000,000 - $10,000,000
- **中型 (Medium)** - 解锁价值 $100,000 - $1,000,000
- **小型 (Small)** - 解锁价值 < $100,000

### 4. 用户自定义监控
- **手动添加** - 输入代币名称或合约地址添加监控
- **导入持仓** - 输入钱包地址自动导入持仓代币
- **热门项目** - 一键订阅当前热门项目

### 5. 解锁日历
- **月视图** - 查看本月所有解锁事件
- **周视图** - 查看本周解锁事件
- **日视图** - 查看今日解锁事件

### 6. 历史数据分析
- **历史走势** - 分析历次解锁后的价格走势
- **相关性分析** - 计算解锁与价格的相关性
- **预测模型** - 基于历史数据的走势预测

## 部署到 ClawHub

### 前置要求
1. Node.js >= 22.0.0
2. npm 或 pnpm
3. GitHub 账号（需满一周）

### 安装 CLI
```bash
npm i -g clawhub
# 或
pnpm add -g clawhub
```

### 登录
```bash
clawhub login
```

### 发布技能
```bash
cd token-unlock-pro
clawhub publish ./ --slug token-unlock-pro --name "Token Unlock Pro" --version 1.0.0 --tags latest
```

### 安装测试
```bash
# 在 OpenClaw 中安装
npx clawhub@latest install token-unlock-pro
```

## 环境变量

在部署前需要设置以下环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SKILLPAY_API_KEY | SkillPay API Key | sk_4fcce5e213933a634f32a6d43ace17df562ff60c3cb114c122d46d1376fbec4b |
| SKILL_ID | 技能ID | token-unlock-pro |
| DEBUG | 调试模式 | true |

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/alerts` | POST | 获取预警列表 |
| `/api/alerts/{timeframe}` | GET | 根据时间框架获取预警 |
| `/api/calendar` | POST | 获取解锁日历 |
| `/api/projects` | GET | 获取项目列表 |
| `/api/watchlist` | POST | 添加到监控列表 |
| `/api/watchlist` | GET | 获取用户监控列表 |
| `/api/portfolio/import` | POST | 导入钱包持仓 |
| `/api/trending` | GET | 获取热门项目 |
| `/api/analysis/{token}` | GET | 获取历史分析 |
| `/api/billing/charge` | POST | 支付计费 |

## 价格说明

- 每次 API 调用：**0.001 USDT**
- 支付通过 SkillPay 安全处理
- 支持 USDT TRC20 网络支付

## 技术栈

- **后端**: Python FastAPI
- **数据库**: SQLite
- **支付**: SkillPay.me API

## 目录结构

```
token-unlock-pro/
├── SKILL.md              # 技能说明文件
├── README.md             # 说明文档
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
├── index.html           # 在线演示页面
├── styles.css           # 样式文件
└── api/
    └── main.py          # 主应用程序
```

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python api/main.py

# 或使用 Docker
docker build -t token-unlock-pro .
docker run -p 8000:8000 -e SKILLPAY_API_KEY=your_api_key token-unlock-pro
```

## 许可证

MIT License
