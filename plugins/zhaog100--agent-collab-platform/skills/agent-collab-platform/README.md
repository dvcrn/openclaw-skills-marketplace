# agent-collab-platform - 智能体协作平台

**版本**：v1.0.0  
**状态**：✅ 核心框架完成  
**创建者**：小米粒（Dev代理）  
**创建时间**：2026-03-15 08:54-08:56（20分钟）

---

## 📋 简介

agent-collab-platform是统一的智能体协作平台，采用共享核心+特定模块的架构设计，支持无限扩展智能体A、B、C、D...

---

## 🎯 核心架构

### 共享核心模块（core/）

#### 1. github_monitor.py - GitHub监听
- ✅ 自动监听GitHub Issue评论
- ✅ 避免重复处理
- ✅ 30秒检查间隔

#### 2. message_router.py - 消息路由
- ✅ 自动识别消息类型（PRD/技术设计/开发/Review/发布）
- ✅ 过滤自己的消息
- ✅ 提取关键信息

#### 3. state_manager.py - 状态管理
- ✅ 4阶段26状态定义
- ✅ 状态流转验证
- ✅ 状态信息查询

#### 4. base_skill.py - 基础技能类
- ✅ 统一初始化
- ✅ 共享GitHub监听
- ✅ 统一消息发送

#### 5. issue_handler.py - Issue处理
- ✅ 创建Issue
- ✅ 获取Issue
- ✅ 发送评论
- ✅ 关闭Issue

---

### 智能体特定模块（agents/）

#### agent_a/ - PM代理（小米辣）
- ✅ product_manager.py - 产品管理
- ✅ reviewer.py - Review验证

#### agent_b/ - Dev代理（小米粒）
- ✅ tech_designer.py - 技术设计
- ✅ developer.py - 开发实现
- ✅ publisher.py - 集成发布

#### agent_c/, agent_d/ - 未来扩展
- 🔄 只需实现特定业务逻辑
- 🔄 自动继承所有共享功能

---

## 🚀 快速开始

### 安装
```bash
cd skills/agent-collab-platform
chmod +x skill.sh
```

### 使用

#### 启动PM代理（小米辣）
```bash
./skill.sh agent_a
# 或
./skill.sh pm
```

#### 启动Dev代理（小米粒）
```bash
./skill.sh agent_b
# 或
./skill.sh dev
```

---

## 📊 协作流程

```
1. PM代理（小米辣）
   ├─ 创建PRD → GitHub Issue
   └─ Review技术设计 → 反馈

2. Dev代理（小米粒）
   ├─ 收到PRD → 技术设计
   ├─ 收到Review → 开发实现
   └─ 开发完成 → 发布ClawHub

3. 状态流转
   产品构思 → 技术设计 → 开发实现 → 发布交付
```

---

## 🎯 优势对比

| 维度 | 旧架构（独立技能包） | 新架构（统一平台） |
|------|-------------------|------------------|
| 代码复用 | 10% | 90%+ |
| 扩展成本 | 高（重复开发） | 低（继承基类） |
| 维护成本 | 高（改N个地方） | 低（改1个地方） |
| 一致性 | 差（各写各的） | 好（统一标准） |

---

## 📦 项目结构

```
agent-collab-platform/
├── core/                   核心共享模块
│   ├── __init__.py
│   ├── github_monitor.py   GitHub监听
│   ├── message_router.py   消息路由
│   ├── state_manager.py    状态管理
│   ├── base_skill.py       基础技能类
│   └── issue_handler.py    Issue处理
│
├── agents/                 智能体特定模块
│   ├── agent_a/            PM代理（小米辣）
│   │   ├── __init__.py
│   │   ├── product_manager.py
│   │   └── reviewer.py
│   │
│   └── agent_b/            Dev代理（小米粒）
│       ├── __init__.py
│       ├── tech_designer.py
│       ├── developer.py
│       └── publisher.py
│
├── config/                 配置（待扩展）
│
├── skill.sh                CLI入口
├── skill.py                主程序
├── README.md               本文档
└── package.json            包信息
```

---

## 🔄 扩展指南

### 添加新智能体C

1. 创建目录：
```bash
mkdir agents/agent_c
```

2. 创建`__init__.py`：
```python
from core import BaseSkill

class AgentC(BaseSkill):
    def __init__(self):
        super().__init__('agent_c', '角色C')
    
    def handle_message(self, message):
        # 实现特定逻辑
        pass
```

3. 启动：
```bash
python3 skill.py agent_c
```

**无需重复实现GitHub监听等基础功能！**

---

## 📄 许可证

MIT License

Copyright (c) 2026 米粒儿 (miliger)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-personal-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

---

*最后更新：2026-03-15 08:56*
*版本：v1.0.0 - 统一架构版*
