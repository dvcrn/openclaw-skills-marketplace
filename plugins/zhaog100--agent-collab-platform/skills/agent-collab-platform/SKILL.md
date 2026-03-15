---
name: agent-collab-platform
description: "Agent Collaboration Platform"
---

# agent-collab-platform

**版本**：v1.0.0  
**类型**：智能体协作平台  
**作者**：小米粒 (miliger)  

---

## 📋 简介

agent-collab-platform是统一的智能体协作平台，采用**共享核心+特定模块**的架构设计，支持无限扩展智能体A、B、C、D...

---

## 🎯 核心特性

### 共享核心（90%代码复用）
- ✅ GitHub Issue自动监听
- ✅ 消息智能路由
- ✅ 状态统一管理
- ✅ Issue处理自动化

### 智能体模块
- **agent_a**（PM代理）：产品管理 + Review验证
- **agent_b**（Dev代理）：技术设计 + 开发实现 + 集成发布
- **agent_c/d/e**（未来）：继承基类即可

---

## 🚀 快速开始

### 安装
```bash
clawhub install agent-collab-platform
```

### 使用

#### 启动PM代理（小米辣）
```bash
cd skills/agent-collab-platform
./skill.sh agent_a
```

#### 启动Dev代理（小米粒）
```bash
cd skills/agent-collab-platform
./skill.sh agent_b
```

---

## 📊 架构优势

| 维度 | 独立技能包 | 统一平台 |
|------|----------|---------|
| 代码复用 | 10% | 90%+ ⭐ |
| 扩展成本 | 高 | 低 ⭐ |
| 维护成本 | 高 | 低 ⭐ |

---

## 📄 许可证

MIT License - 免费使用、修改和重新分发

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-personal-skills
- ClawHub: https://clawhub.com
- 创建者: 小米粒 (miliger)
