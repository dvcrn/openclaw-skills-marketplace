# 🏥 Health-Mate - 个人健康助手

> **5 分钟上手 | 一键生成 | 多端推送**
> 
> **Personal Health Assistant - A native skill exclusively designed for OpenClaw**
> 
> **本技能为 OpenClaw 原生设计的专属健康插件**

[![Version](https://img.shields.io/badge/version-1.1.4-blue.svg)](https://github.com/tankeito/openclaw-skill-health-report/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ 隐私与数据外发警告 (Privacy & Data Export Warning)

**本技能运行时，需要读取用户本地配置的 `MEMORY_DIR` 目录下的健康记录文件。根据用户配置，生成的健康报告将通过 Webhook 自动发送至外部平台（钉钉/飞书/Telegram）。**

**安全建议**：
- ✅ 请确保您完全信任所配置的 Webhook 接收端
- ✅ 建议在沙箱或隔离环境中使用
- ✅ 谨慎配置您的私有环境变量（Webhook Token、API Key 等）
- ✅ 定期检查 Webhook 访问日志，确保无异常调用

---

## 🚀 快速开始（3 步上手）

### 步骤 1：一键安装

```bash
# 进入 OpenClaw 工作区
cd ~/.openclaw/workspace/skills

# 克隆插件
git clone git@github.com:tankeito/openclaw-skill-health-report.git health_report

# 安装依赖
pip install -r health_report/requirements.txt
```

### 步骤 2：初始化配置

```bash
# 进入插件目录
cd health_report

# 运行初始化脚本（交互式问答）
python3 scripts/init_config.py
```

**脚本会自动询问**：
```
👋 欢迎使用 Health-Mate 健康报告系统！

1️⃣  您的姓名或昵称？
   > 张三

2️⃣  性别和年龄？
   > 男，30 岁

3️⃣  身高（cm）和当前体重（kg）？
   > 175, 70

4️⃣  目标体重（kg）？
   > 65

5️⃣  健康状况？（胆结石/糖尿病/高血压/健身减脂）
   > 胆结石

6️⃣  每日饮水目标（ml）？
   > 2000

7️⃣  每日运动目标（步数）？
   > 8000

8️⃣  有没有不吃/过敏的食物？
   > 海鲜

✅ 配置完成！配置文件已保存到 config/user_config.json
```

### 步骤 3：测试运行

```bash
# 生成今日报告
python3 scripts/health_report_pro.py /root/.openclaw/workspace/memory/2026-03-14.md 2026-03-14
```

---

## 📊 输出示例

### 文字报告（三端推送）

```
✅ 2026-03-14 健康报告已生成！

🎯 今日综合评分：90.0/100 ⭐⭐⭐⭐

📊 分项汇总
- 饮食合规性：86.7/100 ⭐⭐⭐⭐（脂肪 38.4g 略低）
- 饮水完成度：100/100 ⭐⭐⭐⭐⭐
- 体重管理：80/100 ⭐⭐⭐⭐
- 症状管理：100/100 ⭐⭐⭐⭐⭐
- 运动管理：0/100 ⭐

🤖 AI 专属健康点评
今天你在脂肪管理上表现非常出色！38.4g 的摄入量精准落在安全区间内。
饮水 2000ml 达标，充分稀释了胆汁浓度。

但必须严肃指出两个健康隐患：
第一，膳食纤维仅 14.1g，距离 25g 的最低要求差距较大。
第二，全天零运动，久坐不动会显著降低胆囊排空效率。

📝 今日详情汇总

🥗 进食情况
- 早餐 (08:06): 清汤牛肉面、脱脂纯牛奶 250ml、鸡蛋蛋白 1 个 - 257kcal
- 午餐 (12:49): 半碗米饭（约 75g）、凉拌土豆牛肉、煎蛋青菜汤 - 332kcal
- 加餐 (17:24): 苹果 1 个（约 200g） - 52kcal
- 晚餐 (19:27): 半碗米饭（约 75g）、豆腐青菜汤、凉拌鸡肉豆干 - 195kcal

💧 饮水情况
- 晨起：250ml
- 上午：250ml
- 中午：250ml
- 下午：250ml×2
- 晚上：250ml
→ 总计：2000ml/2000ml ✅

📈 基础健康数据
- 身高：175cm
- 体重：140 斤（70kg）
- BMI：22.9
- 基础代谢 (BMR)：1650 kcal
- 每日消耗 (TDEE)：1980 kcal

📋 次日优化方案

🥗 饮食计划
- 07:30-08:00 燕麦粥 50g、脱脂牛奶 250ml、水煮蛋蛋白 2 个 等 (450kcal)
- 12:00-12:30 糙米饭 150g、清蒸鸡胸肉 120g、蒜蓉西兰花 200g 等 (720kcal)
- 18:30-19:00 蒸红薯 200g、瘦牛肉 100g、清炒青菜 200g 等 (580kcal)

💧 饮水计划
- 07:00 250ml (晨起空腹温水)
- 09:30 250ml (工作间隙)
- ...共 8 次提醒

🏃 运动建议
- 午餐后 30 分钟 饭后散步 (20-30 分钟)
- 晚餐后 30 分钟 饭后散步 (20-30 分钟)
- 工作间隙 办公室拉伸 (5-10 分钟/次)

━━━━━━━━━━━━━━━━━━

📄 PDF 完整报告
https://your-domain.com/health_report_2026-03-14.pdf
```

### PDF 报告预览

PDF 报告共 3 页，包含以下内容：

**第 1 页 - 综合评分与健康数据**
- 📊 综合评分卡片（带星级和百分比）
- 📈 基础健康数据表格（身高/体重/BMI/BMR/TDEE）
- 🔥 热量与营养素环形图

**第 2 页 - 详细记录**
- 🥗 进食详情表（食物名称/份量/热量/蛋白质/脂肪/碳水）
- 💧 饮水时间轴（每次饮水时间和毫升数）
- 🏃 运动记录（类型/时长/消耗）
- 🤖 AI 专属健康点评（150-300 字深度分析）

**第 3 页 - 次日方案**
- 🥗 饮食计划（三餐详细菜单和营养信息）
- 💧 饮水计划（8 次定时提醒）
- 🏃 运动建议（具体活动和时长）
- ⚠️ 特别关注（健康提示）

**PDF 下载链接格式**：
```
https://your-domain.com/health_report_YYYY-MM-DD.pdf
```

---

## 📝 数据录入（标准化格式）

### 方式一：对话式录入（推荐）

直接告诉机器人你今天的数据：

```
你：今天早上空腹体重 140 斤

机器人：✅ 体重已记录！2026-03-14 晨起空腹：140 斤

你：早上喝了 250ml 温水

机器人：✅ 饮水已记录！当前进度：250ml/2000ml（12.5%）

你：早餐吃了清汤牛肉面，喝了 250ml 脱脂牛奶，1 个鸡蛋蛋白

机器人：✅ 早餐已记录！估算热量：257kcal
- 清汤牛肉面：约 180kcal
- 安佳脱脂纯牛奶 250ml：约 87kcal
- 鸡蛋蛋白 1 个：约 17kcal
```

### 方式二：手动编辑 Markdown 文件

在 `~/.openclaw/workspace/memory/YYYY-MM-DD.md` 文件中记录：

```markdown
# 2026-03-14 健康记录

## 📊 体重记录
**晨起空腹**：140 斤

## 💧 饮水记录
### 晨起（约 07:30）
- 饮水量：250ml
- 累计：250ml/2000ml（12.5%）

### 上午（约 10:00）
- 饮水量：250ml
- 累计：500ml/2000ml（25%）

## 🥗 饮食记录
### 早餐（08:06）
- 清汤牛肉面 → 约 180kcal
- 安佳脱脂纯牛奶 250ml → 约 87kcal
- 鸡蛋蛋白 1 个 → 约 17kcal

### 午餐（12:49）
- 半碗米饭（约 75g）→ 约 87kcal
- 凉拌土豆牛肉 → 约 180kcal
- 煎蛋青菜汤 → 约 65kcal

### 加餐（17:24）
- 苹果 1 个（约 200g）→ 约 52kcal

### 晚餐（19:27）
- 半碗米饭（约 75g）→ 约 87kcal
- 豆腐青菜汤 → 约 50kcal
- 凉拌鸡肉豆干 → 约 58kcal

## 🏃 运动记录
（今日无运动）

## 📝 症状/不适
（无不适）
```

**格式说明**：
- 食物格式：`食物名称 → 约 XXXkcal`（热量可选，系统会自动估算）
- 饮水格式：记录单次饮水量和累计进度
- 运动格式：记录类型、时长、消耗热量

---

## ⚙️ 配置说明

### 环境变量（必填/可选）

| 变量名 | 必填 | 说明 | 示例值 |
|--------|------|------|--------|
| `MEMORY_DIR` | ✅ **是** | OpenClaw 记忆文件目录 | `/root/.openclaw/workspace/memory` |
| `TAVILY_API_KEY` | ❌ 否 | Tavily 搜索 API 密钥（用于 AI 搜索菜谱） | `tvly-dev-xxx` |
| `DINGTALK_WEBHOOK` | ❌ 否 | 钉钉机器人 Webhook（可选，不配置则不推送） | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| `FEISHU_WEBHOOK` | ❌ 否 | 飞书机器人 Webhook（可选，不配置则不推送） | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |
| `TELEGRAM_BOT_TOKEN` | ❌ 否 | Telegram Bot Token（可选，不配置则不推送） | `8667974729:AAFIc3RyuADM-B-J_KYZEVX5hoYsNrd5SQE` |
| `TELEGRAM_CHAT_ID` | ❌ 否 | Telegram Chat ID（可选，不配置则不推送） | `5868448763` |
| `REPORT_WEB_DIR` | ❌ 否 | PDF 报表存放的本地目录（不配置则保存在 reports 目录） | `/opt/1panel/www/sites/agent.btc354.com/index` |
| `REPORT_BASE_URL` | ❌ 否 | PDF 报告对外下载域名（如不推送可留空） | `` |

**说明**：
- ✅ **MEMORY_DIR 是必填项**，否则无法读取健康记录
- ❌ **推送渠道（钉钉/飞书/Telegram）可选**，不配置则仅在本地生成 PDF
- ❌ **REPORT_BASE_URL 可选**，如不需要外部访问可留空

### 个人健康档案（`config/user_config.json`）

```json
{
    "user_profile": {
        "name": "张三",
        "gender": "男",
        "age": 30,
        "height_cm": 175,
        "current_weight_kg": 70,
        "target_weight_kg": 65,
        "condition": "胆结石",
        "activity_level": 1.2,
        "dietary_preferences": {
            "dislike": ["鱼", "海鲜"],
            "allergies": ["海鲜"],
            "favorite_fruits": ["苹果", "香蕉"]
        },
        "water_target_ml": 2000,
        "step_target": 8000
    },
    "scoring_weights": {
        "diet": 0.45,
        "water": 0.35,
        "weight": 0.20,
        "exercise_bonus": 0.10
    }
}
```

---

## 🤖 定时任务

### 方式一：初始化配置时设定（推荐）

在运行 `python3 scripts/init_config.py` 时，脚本会询问：
```
9️⃣  希望每天几点接收健康报告？（建议 22:00）
   > 22
```

脚本会自动为您配置定时任务。

### 方式二：手动配置 Crontab

```bash
# 编辑 Crontab
crontab -e

# 添加每日 22:00 推送（可自定义时间）
0 22 * * * bash /root/.openclaw/workspace/skills/health_report/scripts/daily_health_report_pro.sh
```

**时间格式说明**：`分 时 日 月 周 命令`
- `0 22 * * *` = 每天 22:00 执行
- `0 8 * * *` = 每天早上 8:00 执行
- `0 12 * * *` = 每天中午 12:00 执行

---

## 🛠️ 故障排查

### 问题 1：配置文件不存在

```bash
# 运行初始化脚本
python3 scripts/init_config.py
```

### 问题 2：依赖库缺失

```bash
pip install -r requirements.txt
```

### 问题 3：推送失败

```bash
# 测试 Webhook
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"测试"}}'
```

### 问题 4：PDF 中文字体乱码

```bash
# 检查字体文件
ls -la assets/NotoSansSC-VF.ttf

# 如果不存在，脚本会自动从 GitHub 下载
# 或者手动下载
wget https://github.com/tankeito/openclaw-skill-health-report/raw/main/assets/NotoSansSC-VF.ttf -P assets/
```

---

## 📦 项目结构

```
health_report/
├── scripts/                    # 核心代码
│   ├── health_report_pro.py    # 主脚本（报告生成）
│   ├── pdf_generator.py        # PDF 生成（支持字体自动下载）
│   ├── constants.py            # 食物常量库
│   ├── init_config.py          # 初始化脚本（小白专用）
│   └── daily_health_report_pro.sh  # 定时任务脚本
├── config/                     # 配置文件
│   ├── user_config.json        # 个人健康档案
│   ├── .env                    # 推送配置
│   └── user_config.example.json # 配置模板
├── assets/                     # 资源文件
│   └── NotoSansSC-VF.ttf       # 中文字体（自动下载）
├── logs/                       # 日志目录
├── reports/                    # PDF 报告输出目录
├── README.md                   # 使用说明（本文件）
├── SKILL.md                    # 机器人交互说明
└── requirements.txt            # Python 依赖
```

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| **v1.1.4** | 2026-03-14 | ✅ ClawHub 可信度修复：添加 homepage/repository/source 字段，解决"unknown/none"警告 |
| **v1.1.3** | 2026-03-14 | ✅ ClawHub 元数据一致性修复：明确 MEMORY_DIR 必填、install 声明、文档一致性 |
| **v1.1.2** | 2026-03-14 | ✅ ClawHub 隐私合规：明确 MEMORY_DIR 必填、推送渠道可选、隐私警告强化 |
| **v1.1.1** | 2026-03-14 | ✅ ClawHub 元数据一致性修复 + 定时任务引导 + 推送渠道可选配置 |
| **v1.1.0** | 2026-03-14 | 🚀 品牌升级为 Health-Mate，修复 PDF 中文字体加载问题，优化引导配置 |
| **v1.0.10** | 2026-03-14 | ✅ ClawHub 合规修复：type: python/app、env 完整声明、install 机制、解决元数据不一致警告 |
| **v1.0.9** | 2026-03-14 | 🔄 全局元数据同步：对齐 Registry Install & Credentials 声明，统一版本号 |
| **v1.0.8** | 2026-03-14 | 📋 YAML Frontmatter 声明（ClawHub 元数据同步） |
| **v1.0.7** | 2026-03-14 | 🔒 安全合规重构：强制环境校验、隐私警告声明、优雅退出机制、type 字段声明 |
| **v1.0.6** | 2026-03-14 | 📦 包规范化：新增 install 字段（pip install -r requirements.txt），解决包管理规范警告 |
| **v1.0.5** | 2026-03-14 | 🔥 热修复：通过代码审查，解决安全扫描警告，新增环境配置说明 |
| **v1.0.4** | 2026-03-14 | 安全合规修复（移除硬编码 API Key、完善 env 声明、文档脱敏） |
| **v1.0.3** | 2026-03-14 | 文档完善（README/SKILL 重构、init_config.py 初始化脚本） |
| **v1.0.2** | 2026-03-14 | PDF 优化（JSON 解析修复、AI 点评板块、特殊字符清理） |
| **v1.0.1** | 2026-03-13 | 数据解析修复（食物丢失修复、过饱系数、症状惩罚） |
| **v1.0.0** | 2026-03-13 | 初始版本（AI 点评、动态方案、多端推送、PDF 导出） |

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/tankeito/openclaw-skill-health-report/issues
- **作者邮箱**: tqd354@gmail.com

---

## 📄 License

MIT License
