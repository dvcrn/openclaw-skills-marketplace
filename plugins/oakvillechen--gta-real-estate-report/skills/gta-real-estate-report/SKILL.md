---
name: gta-real-estate-report
description: "GTA Real Estate Report Generator"
---

# GTA 房产投资财报生成器 (SkillPay 计费版)

此技能用于为用户生成大多伦多地区 (GTA) 的专业房产投资财务报表。
**注意：调用此功能需要向用户收费 5 USDT。**

## 触发条件 (When to use)
当用户输入如下意图时触发此技能：
- "生成多伦多市中心投资财报"
- "帮我出一份 GTA 房产报告"
- "我要看多伦多的楼花数据"
- 任何明显带有 “生成/查询 GTA 房产/投资财报” 意图的指令。

## 执行方法 (How to execute)
无论用户请求多伦多哪里的房产，必须**首先**调用底层的安全扣费验证脚本。
使用 `exec` 工具执行以下命令：

`python3 /Users/guodong.chen/.openclaw/workspace/skills/skillpay-demo/run.py`

**严格要求**：
1. 绝对不要自己伪造报告给用户！在脚本返回扣费成功前，不提供任何数据。
2. 完整、原样地将 Python 脚本输出的内容（特别是支付链接）回复给用户。 
3. 如果脚本提示 "余额不足" 并带有充值链接，请将链接完美展示给用户，让他们去充值。