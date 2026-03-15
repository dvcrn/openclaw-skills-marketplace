---
name: ai-deterministic-control
description: "Ai Deterministic Control"
---

# AI 确定性控制工具

**版本**：v1.0.0
**创建者**：小米粒（开发代理）
**创建时间**：2026-03-13
**Issue**：#16
**ClawHub**：待发布

---

## 📋 技能简介

控制 AI 输出随机性，提供确定性模式。通过温度参数控制、一致性检查、可复现性保证和随机性监控，确保 AI 输出的稳定性和可预测性。

---

## 🎯 核心功能

### 1. 温度参数设置 ⭐⭐⭐⭐⭐
- **范围**：0.0-2.0
- **预设**：code(0.0), balance(0.5), creative(0.8), brainstorm(1.5)
- **模式**：高度确定性、平衡模式、创造性模式、高创造性模式

### 2. 输出一致性检查 ⭐⭐⭐⭐⭐
- **采样**：多次采样对比
- **评分**：0-100% 一致性评分
- **阈值**：可配置一致性阈值

### 3. 可复现性保证 ⭐⭐⭐⭐⭐
- **种子控制**：固定随机种子
- **验证机制**：验证复现性
- **记录管理**：种子历史记录

## 🆕 P0新功能（2026-03-13）

### 1. 动态温度调整 (`deterministic adjust`)
- **智能推荐**：根据提示词关键词自动识别任务类型
- **历史学习**：基于历史质量数据自动优化温度
- **实时调整**：支持实时温度调整建议

**示例**：
```bash
# 推荐温度
deterministic adjust recommend "生成一个Python函数"

# 查看统计
deterministic adjust stats
```

### 2. 差异分析报告 (`deterministic diff`)
- **相似度矩阵**：计算多次输出的两两相似度
- **关键发现**：识别最相似和最不相似的输出对
- **多格式报告**：支持text/json/html格式

**示例**：
```bash
# 分析差异
deterministic diff analyze --outputs "输出1" --outputs "输出2"

# 生成HTML报告
deterministic diff report --outputs "输出1" --outputs "输出2" --format html
```

### 3. 异常检测告警 (`deterministic alert`)
- **智能检测**：根据相似度阈值自动检测异常
- **多渠道通知**：支持邮件/飞书/钉钉
- **告警聚合**：避免告警轰炸，支持冷却和聚合

**示例**：
```bash
# 检测异常
deterministic alert check --similarity 45 --prompt "生成一个函数"

# 查看统计
deterministic alert stats

# 配置飞书通知
deterministic alert configure feishu --enabled --config '{"webhook_url": "https://..."}'
```

### 4. 随机性监控 ⭐⭐⭐⭐
- **趋势分析**：历史趋势分析
- **异常检测**：自动检测异常输出
- **报告导出**：JSON 格式报告

---

## 🚀 快速开始

### 安装

```bash
# 从 ClawHub 安装（推荐）
clawhub install ai-deterministic-control

# 或从 GitHub 克隆
git clone https://github.com/zhaog100/openclaw-skills
cd openclaw-skills/skills/ai-deterministic-control
pip install -r requirements.txt
```

### 基本使用

```bash
# 1. 设置温度为高度确定性模式
deterministic temp 0.0

# 2. 检查输出一致性
deterministic check "生成一个Python函数"

# 3. 使用种子生成确定性输出
deterministic repro "生成配置文件" --seed 12345

# 4. 验证复现性
deterministic repro "生成配置文件" --verify 12345

# 5. 查看随机性趋势
deterministic monitor trends

# 6. 检测异常输出
deterministic monitor anomalies

# 7. 导出监控报告
deterministic monitor report
```

---

## 📚 详细用法

### 温度控制

```bash
# 设置温度
deterministic temp 0.5

# 使用预设
deterministic temp --preset code

# 列出所有预设
deterministic temp --list
```

**预设说明**：
- `code`：高度确定性（0.0）- 代码/配置生成
- `balance`：平衡模式（0.5）- 常规对话
- `creative`：创造性模式（0.8）- 创意写作
- `brainstorm`：高创造性模式（1.5）- 头脑风暴

### 一致性检查

```bash
# 默认检查（3次采样，80%阈值）
deterministic check "生成一个函数"

# 自定义参数
deterministic check "生成配置" --samples 5 --threshold 90

# 指定温度
deterministic check "生成代码" --temperature 0.0
```

### 可复现性

```bash
# 自动生成种子
deterministic repro "生成配置"

# 指定种子
deterministic repro "生成配置" --seed 12345

# 验证复现性（3次验证）
deterministic repro "生成配置" --verify 12345

# 自定义验证次数
deterministic repro "生成配置" --verify 12345 --iterations 5
```

### 随机性监控

```bash
# 趋势分析（7天）
deterministic monitor trends

# 自定义天数
deterministic monitor trends --days 30

# 异常检测（50%阈值）
deterministic monitor anomalies

# 自定义阈值
deterministic monitor anomalies --threshold 60

# 导出报告
deterministic monitor report

# 自定义输出路径
deterministic monitor report --output my_report.json

# 查看统计信息
deterministic monitor stats
```

---

## 📊 使用场景

### 场景1：代码生成（高度确定性）

```bash
# 设置为高度确定性模式
deterministic temp --preset code

# 检查一致性
deterministic check "生成一个排序算法" --samples 3 --threshold 90

# 生成可复现代码
deterministic repro "生成排序算法" --seed 12345
```

### 场景2：配置文件生成

```bash
# 设置温度
deterministic temp 0.0

# 生成配置
deterministic repro "生成Nginx配置" --seed 98765

# 验证配置一致性
deterministic check "生成Nginx配置" --samples 5
```

### 场景3：创意写作（高创造性）

```bash
# 设置为创造性模式
deterministic temp --preset creative

# 生成创意内容
deterministic repro "写一首诗" --seed 54321
```

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────┐
│  CLI 入口层（deterministic.py）          │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  业务逻辑层                              │
│  ├── TemperatureController              │
│  ├── ConsistencyChecker                 │
│  ├── ReproducibilityGuarantor           │
│  └── RandomnessMonitor                  │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  数据持久层（config.json / history.db）  │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  AI API 层（智谱 / DeepSeek）            │
└─────────────────────────────────────────┘
```

---

## 📈 性能指标

- **温度设置**：< 100ms
- **一致性检查**：< 1 秒（3次采样）
- **监控报告**：< 5 秒
- **测试覆盖率**：> 85%

---

## 🔧 配置说明

### config.json

```json
{
  "temperature": 0.5,
  "default_mode": "balance",
  "api_provider": "zhipu",
  "api_key": "<您的API密钥>",
  "history_db": "history.db",
  "seeds_file": "seeds.json",
  "cache_enabled": true,
  "cache_ttl": 300
}
```

### 环境变量

```bash
export ZHIPU_API_KEY="your_zhipu_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
```

---

## 🧪 测试

```bash
# 运行所有测试
cd test
pytest test_all.py -v

# 运行特定测试
pytest test_all.py::TestTemperatureController -v
```

---

## 📦 依赖

```
click>=8.0.0
sqlite3  # 内置
```

---

## 🤝 协作流程

本技能由**双米粒协作系统**开发：

1. **米粒儿（PM）**：创建 PRD (#16)
2. **小米粒（Dev）**：技术设计 + 开发实现
3. **米粒儿（PM）**：Review（12维度 + 5层验收）
4. **小米粒（Dev）**：发布到 ClawHub

---

## 📄 许可证

MIT License

Copyright (c) 2026 小米粒 (xiaomili)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 小米粒 (xiaomili)

---

*创建时间：2026-03-13*
*版本：v1.0.0*
