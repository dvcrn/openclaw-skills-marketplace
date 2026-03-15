<div align="center">

<img src="./assets/banner.png" alt="Agent Memento Banner" width="100%">

# 🧠 Agent Memento

**面向大模型的“记碎式”自动化生产兵工厂**

*“不要去造一个企图记住一切的 AI，我们要造一个让 AI 每 5 分钟醒来重新精读图纸的系统。”*

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![ClawHub](https://img.shields.io/badge/ClawHub-Install-ff69b4.svg)](https://clawhub.com/yangwenyu2/agent-memento)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](./README.md) | [简体中文](./README_zh.md)

</div>

---

## ⚡ The "Aha!" Problem：聊天框造不出航空母舰

当你让 AI 智能体在一个无限延长的聊天框里造一个庞大的项目，前 10 分钟的代码如魔法般美妙。但当代码规模超过 2000 行后，魔法变成了梦魇：
- **上下文失忆症 (Context Amnesia)**：它忘了自己一小时前定义的接口，开始凭空捏造 API。
- **“看起来挺好”幻觉 (The "LGTM" Delusion)**：它自信满满地说“我修好了 Bug”，但代码根本跑不通。
- **OOM 核爆 (The OOM Nuke)**：为了修一个错字，它试图在一次对话里直接重写整个 3000 行的文件，最终算爆显存导致进程宿主（Gateway）崩溃死机。

**结论：持续不断的冗长对话，是对长线工程的最致命毒药。**

## 💡 The Solution：记忆碎片执行法 (Memento Execution)

灵感来自诺兰电影《记忆碎片》(Memento)。我们彻底抛弃并摧毁了“全知全能的超级 Agent”。
我们用一支**无情、失忆、极短命的 Tick Worker（滴答工人）军队**来取代它。它们活着的唯一目的，就是读同一张实体图纸，去敲下一颗钉子，物理验证，然后赴死（休眠）。

### ⚙️ 它是怎么工作的？(双态智能分离)

| 模式 | 角色 | 职责 | 记忆力 |
| :--- | :--- | :--- | :--- |
| **🏛️ 架构师态** | 你 + 主控 AI | 在日常对话中讨论全局架构，将目标切割并写入 `MASTER_PLAN.md`。 | 无上限 (人类大脑) |
| **🔨 泥瓦匠态** | Cron 守护进程 | 每 5 分钟在后台唤醒一个没有上下文的新 Agent，只做一件事，证明它管用，然后死掉。 | 5 分钟 (零上下文) |

#### Memento 强制注入的铁血纪律：
1. **外科手术级防爆 (Surgical Edits)**：只允许使用精确替换（sed 级别），绝不允许覆写全文引起 OOM 崩溃。
2. **拒绝脑内验算 (Evidence-Based)**：必须在控制台拿到成功的 `Exit 0` 退出码（`npm test` / `curl`）。拿不到，死也不许给自己打 `[x]` 勾。
3. **拒绝静默空转 (Anti-Ghosting)**：如果卡死，死前必须在 `TICK_STATUS.md` 黑匣子里写下残骸日志。

### 🕹️ 观测级驾驭 (无 Prompt 干预法)
厌倦了对着聊天框大吼大叫“你刚才写偏了！重写！”？ 
有了 Memento 机制，干预这个黑盒不再需要 Prompt。你只需要像修改备忘录一样静静地把 `MASTER_PLAN.md` 里的勾去掉，或改一句需求。下一个被唤醒的 Tick Worker 会立即遵从这套崭新的宇宙法则，像变道的湍流般顺着你的新图纸奔涌。

---

## 🚀 极速部署 (One-Line Scaffold)

在 OpenClaw 生态里撕毁聊天窗流派，平地拉起属于你的 Memento 自动化兵工厂：

### 1. 从 ClawHub 安装
```bash
clawhub install agent-memento
```

### 2. 初始化项目结构
```bash
cd ~/.openclaw/workspace
bash skills/agent-memento/scripts/init_memento.sh 你的大项目名称
```

它会自动为你完成积木铺设：
1. 注入 `projects/你的项目/docs/MASTER_PLAN.md`（你的全图景大纲图纸）。
2. 构建 `TICK_STATUS.md`（死前黑匣子）。
3. 生成一个**自带军规 System Prompt 的唤醒脚本**： `scripts/你的项目_tick.sh`。

### 3. 释放自动化洪流
在 `MASTER_PLAN.md` 里填好你想造什么，然后挂到 crontab 里：
```bash
# 加入 crontab
*/5 * * * * bash /root/.openclaw/workspace/scripts/你的项目_tick.sh
```

**然后去睡觉。醒来验收一栋每一块砖都被测试验证过的高塔。**

---

## 🛠 前置依赖
- 正确安装了 [OpenClaw CLI](https://github.com/openclaw/openclaw)。
- （强烈建议）项目里最好有测试脚手架 (Jest, PyTest)，让 Worker 能严格遵从证据驱动纪律。

## 📜 License
MIT License.
