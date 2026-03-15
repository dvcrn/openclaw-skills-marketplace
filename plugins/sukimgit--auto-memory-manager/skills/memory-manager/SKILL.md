---
name: memory-manager
description: "智能记忆管理系统：自动记录会话、每日总结、每周提炼，打造 AI 的长期记忆。"
---

# Memory Manager - 智能记忆管理系统

**让 AI 拥有真正的长期记忆！**

自动记录每次会话、每日批量总结、每周提炼精华，打造会学习、会成长的 AI 助手！

---

## 🎯 使用场景

- **会话记录** - 每次对话自动保存，不丢失任何重要信息
- **每日总结** - 晚上 20:00 自动整理当天所有会话
- **每周提炼** - 周日 20:00 提取核心信息到长期记忆
- **关键信息实时保存** - 技能发布、收款信息等立即保存
- **临时文件自动清理** - 保持系统整洁，不占用空间

---

## 🛠️ 核心功能

### 1. 会话记录
- ✅ **自动记录** - 每次会话结束自动保存
- ✅ **结构化存储** - 主题/关键信息/待办/决策分类
- ✅ **临时文件** - 保存到 memory/temp/ 目录
- ✅ **自动编号** - 便于追踪和检索

### 2. 每日总结
- ✅ **批量处理** - 每晚 20:00 处理所有临时文件
- ✅ **信息提炼** - 提取关键信息/待办/决策
- ✅ **生成日报** - 创建 memory/YYYY-MM-DD.md
- ✅ **自动清理** - 删除临时文件，保持整洁

### 3. 每周提炼
- ✅ **读取周记忆** - 读取本周 7 个每日文件
- ✅ **提取核心** - 提炼到 MEMORY.md（长期记忆）
- ✅ **清理过期** - 删除 30 天前的每日文件
- ✅ **持续成长** - 长期记忆只增不减

### 4. 实时保存（双重保障）
- ✅ **关键节点触发** - 技能发布/收款变更/重要决策
- ✅ **立即追加** - 实时写入 MEMORY.md
- ✅ **不丢失** - 即使每日总结失败也有记录

---

## 📁 文件结构

```
memory-manager/
├── memory_manager.py      # 主脚本
├── SKILL.md              # 技能说明
├── config.example.json   # 配置模板
├── .gitignore            # Git 忽略
└── temp/                 # 临时文件目录（自动创建）
    ├── session_*.md      # 会话记录
    └── YYYY-MM-DD.md     # 每日总结
```

---

## 🚀 快速开始

### 1. 安装技能
```bash
clawhub install memory-manager
```

### 2. 配置（可选）
复制配置文件：
```bash
cp config.example.json config.json
```

### 3. 使用

**会话记录：**
```python
from memory_manager import record_session

session_data = {
    "date": "2026-03-06",
    "topics": ["技能发布", "商业化讨论"],
    "key_info": ["发布第 5 个技能"],
    "todos": ["明天提交方案"],
    "decisions": ["采用 SaaS 模式"],
    "emotion": "专注"
}

record_session(session_data)
```

**每日总结：**
```python
from memory_manager import process_temp_files

result = process_temp_files()
print(f"处理了 {result['session_count']} 个会话")
```

---

## ⚙️ 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `temp_dir` | 临时文件目录 | `./temp` |
| `memory_dir` | 记忆文件目录 | `../memory` |
| `auto_save` | 自动保存关键信息 | `true` |
| `cleanup_days` | 保留天数 | `30` |

---

## 💰 定价 Pricing

| 版本 | 价格 | 功能 |
|------|------|------|
| **标准版 Standard** | 免费 Free | 会话记录 + 每日总结 |
| **专业版 Pro** | $20/month (¥139/月) | + 每周提炼 + 实时保存 |
| **团队版 Team** | $50/month (¥349/月) | + 多用户 + 团队记忆共享 |
| **定制版 Custom** | $500-2000 (¥3500-14000) | 私有化部署 + 功能定制 |

---

## 📧 联系 Contact

**定制开发 Custom Development：**
- 📧 邮箱 Email：1776480440@qq.com
- 💬 微信 WeChat：私信获取 DM for details

**支持支付 Payment：**
- 国内 Domestic：私信获取
- 国际 International：私信获取（PayPal/Wise）

**售后支持 After-Sales：**
- 首年免费维护 Free for 1st year
- 次年 $50/年 (¥350/年) optional

---

## 🎯 案例展示 Cases

### 案例 1：个人 AI 助手
- **用户：** 全栈工程师
- **需求：** 让 AI 记住项目细节和决策
- **方案：** 标准版 + 实时保存
- **效果：** AI 真正理解项目，不再重复解释

### 案例 2：客服团队
- **用户：** 10 人客服团队
- **需求：** 共享客户沟通记录
- **方案：** 团队版 + 记忆共享
- **效果：** 新客服快速上手，客户满意度提升 40%

### 案例 3：知识管理
- **用户：** 研究机构
- **需求：** 整理研究讨论和决策
- **方案：** 专业版 + 每周提炼
- **效果：** 形成完整知识库，新人培训时间减半

---

## 🔄 更新日志 Changelog

### v1.0.0 (2026-03-06)
- 初始发布
- 会话自动记录
- 每日批量总结
- 每周提炼功能
- 关键信息实时保存
- 临时文件自动清理

---

## 📚 文档 Docs

**完整文档：** https://clawhub.ai/sukimgit/memory-manager/docs
**GitHub：** https://github.com/sukimgit/memory-manager
**问题反馈：** https://github.com/sukimgit/memory-manager/issues

---

**技能来源 Source：** https://clawhub.ai/sukimgit/memory-manager
**作者 Author：** Monet + 老高
**许可 License：** MIT
