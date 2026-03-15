---
name: code-sentinel
description: "智能代码审查系统：四维一体（安全+性能+质量+架构），支持 SQL 注入、XSS、内存泄漏、O(n²)算法、命名规范、SOLID 原则等 40+ 检查项。使用场景：代码提交前自动检测问题、CI/CD 集成、代码规范检查。支持输出 JSON 报告，可集成到 OpenClaw Control Center。"
---

## 使用方式

### 1. 基础扫描

```bash
python3 scripts/sentinel.py /path/to/project
```

### 2. 指定规则扫描

```bash
# 只做安全检查
python3 scripts/sentinel.py ./src --rules security

# 安全+性能
python3 scripts/sentinel.py ./src --rules security performance
```

### 3. 输出 JSON 报告

```bash
python3 scripts/sentinel.py ./src -o report.json
```

### 4. 检查特定文件

```bash
python3 scripts/sentinel.py src/app.py
```

---

## 输出格式

### 文本格式（默认）

```
🔍 开始审查: ./src
🛡️  安全检测...
⚡ 性能检测...
📊 质量检测...
🏗️  架构检测...

✅ 审查完成
总问题数: 5
```

### JSON 格式

```json
{
  "security": [
    {
      "type": "SQL_INJECTION_RISK",
      "file": "src/db.py",
      "line": 23,
      "message": "可能包含 SQL 注入风险...",
      "severity": "high"
    }
  ],
  "performance": [],
  "quality": [],
  "architecture": [],
  "summary": {
    "total_issues": 1,
    "timestamp": "2026-03-13T22:45:00",
    "target": "./src"
  }
}
```

---

## 检查项清单

### 安全漏洞（40+ 项）

| 类型 | 说明 |
|------|------|
| SQL 注入 | `SELECT * FROM users WHERE id = $id` |
| XSS | `document.write(userInput)` |
| 缓冲区溢出 | C/C++数组越界 |
| 路径遍历 | `../ etc/passwd` |
| 命令注入 | `os.system(cmd)` |
| 敏感信息泄露 | API Key、密码硬编码 |

### 性能问题（20+ 项）

| 类型 | 说明 |
|------|------|
| 内存泄漏 | 未释放资源 |
| 无限循环 | `while true` 无 break |
| 死锁 | 并发锁竞争 |
| O(n²)算法 | 嵌套循环未优化 |
| 资源泄漏 | 文件/连接未关闭 |

### 代码质量（30+ 项）

| 类型 | 说明 |
|------|------|
| 命名规范 | `clickReaction` vs `click_reaction` |
| 函数复杂度 | Cyclomatic Complexity > 10 |
| 重复代码 | 相同逻辑多处出现 |
| 注释覆盖率 | 文档注释缺失 |
| 异常处理 | `try-except` 空块 |

### 架构设计（25+ 项）

| 类型 | 说明 |
|------|------|
| SOLID 原则 | 单一职责、开闭原则等 |
| 模块耦合度 | 高耦合模块检测 |
| API 设计 | RESTful 规范 |
| 设计模式 | 适配器、工厂模式等 |

---

## OpenClaw 集成

### Control Center 显示

审查结果自动同步到 OpenClaw Control Center，支持：
- 问题高亮显示
- 一键跳转修复
- 修复建议弹窗

### OmniMemory 学习

基于用户编码风格自适应调整规则：
- 记住偏好命名方式
- 忽略团队约定的特殊模式
- 优化误报率

---

## 开发计划

- ✅ Phase 1: 核心引擎 + 安全检测器
- ⏳ Phase 2: 智能增强 + 自动修复
- ⏳ Phase 3: OpenClaw 集成
- ⏳ Phase 4: 多语言支持
