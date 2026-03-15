# Smart Model v2.0

**Copyright (c) 2026 思捷娅科技 - MIT License** - 智能模型切换系统

**版本**: 2.0.0
**创建时间**: 2026-03-12
**创建者**: 小米粒（米粒儿的开发代理）
**状态**: ✅ Phase 1 MVP 完成

---

## 📋 功能概览

Smart Model v2.0 是一个智能模型切换系统，根据4个维度自动选择最优AI模型：

1. **文件类型检测** - 根据文件扩展名和内容推荐模型
2. **复杂度分析** - 4维度加权评分（长度30% + 关键词40% + 代码20% + 视觉10%）
3. **上下文监控** - 监控上下文使用率，触发预警机制
4. **AI主动检测** - 分析用户意图，判断是否需要AI主动响应

---

## 🎯 模型映射

| 复杂度得分 | 推荐模型 | 适用场景 |
|-----------|---------|---------|
| < 30 | **flash** | 简单快速响应（问候、确认） |
| 30-59 | **main** | 标准响应（一般问题） |
| 60-79 | **complex** | 复杂任务（代码、分析） |
| ≥ 80 | **complex-deep** | 深度分析（架构、设计） |

---

## 🚀 快速开始

### 基本用法

```bash
# 智能分析（推荐模型）
./smart-model-v2.sh "帮我写一个Python函数"

# 快速切换（性能优化版）
./smart-model-v2.sh --fast "在吗？"

# 系统状态
./smart-model-v2.sh --status

# 批量分析
./smart-model-v2.sh --batch file1.py file2.md file3.png
```

### 集成到其他脚本

```bash
# 在其他脚本中调用
source /root/.openclaw/workspace/skills/smart-model/smart-model-v2.sh

# 获取推荐模型
result=$(smart_model_switch "用户消息" "文件路径" "当前模型")
recommended_model=$(echo "$result" | grep -oP '"final_model": "\K[^"]+')

# 快速获取
model=$(smart_model_switch_fast "用户消息")
```

---

## 📊 4维度复杂度评分

### 长度维度（30%）

- 短消息（<50字符）：5分
- 中等消息（50-200字符）：15分
- 较长消息（200-500字符）：25分
- 长消息（≥500字符）：30分

### 关键词维度（40%）

- **高复杂度**（+10分/个）：分析、架构、设计、优化、重构...
- **中复杂度**（+5分/个）：开发、编程、代码、函数、类...
- **技术关键词**（+8分/个）：Python、JavaScript、Java...
- **任务关键词**（+6分/个）：实现、创建、编写、修改...

### 代码维度（20%）

- 包含代码块：+10分
- 包含代码关键字：+5分
- 代码文件扩展名：+5分

### 视觉维度（10%）

- 包含图片：+10分

---

## 🔧 模块说明

### 1. file_type_detector.sh（8.3KB）

**功能**：检测文件类型并推荐模型

**支持类型**：
- code（代码）→ coding
- document（文档）→ main
- image（图片）→ vision
- audio（音频）→ audio
- video（视频）→ vision
- archive（压缩包）→ main
- log（日志）→ flash
- data（数据）→ main

**关键函数**：
- `detect_file_type(file_path)` - 检测文件类型
- `get_recommended_model(file_type)` - 获取推荐模型
- `batch_detect_file_types(files)` - 批量检测

### 2. complexity_analyzer.sh（9.2KB）

**功能**：4维度复杂度评分

**关键函数**：
- `analyze_message_complexity(message)` - 分析消息复杂度
- `analyze_file_complexity(file_path)` - 分析文件复杂度
- `get_recommended_model_fast(message)` - 快速推荐

### 3. context_monitor.sh（9.1KB）

**功能**：上下文使用率监控和预警

**预警级别**：
- light（60%）- 轻度预警
- heavy（75%）- 重量预警
- critical（90%）- 严重预警

**关键函数**：
- `monitor_context()` - 执行监控
- `predict_context_trend()` - 预测趋势
- `trigger_context_cleanup()` - 触发清理

### 4. ai_detector.sh（10.8KB）

**功能**：AI主动检测和意图分析

**触发条件**：
- **AI触发**：分析、优化、设计、开发...
- **快速触发**：在吗、你好、善、对...
- **深度触发**：详细、深入、全面、系统...

**关键函数**：
- `detect_user_intent(message)` - 检测意图
- `suggest_model_switch(message)` - 模型切换建议
- `suggest_ai_behavior(message)` - AI行为建议

---

## 📈 决策优先级

模型切换决策优先级（从高到低）：

1. **文件类型驱动** - 如果有文件，优先根据文件类型推荐
2. **上下文紧急度** - 如果上下文使用率 ≥ 90%，强制切换到flash
3. **复杂度驱动** - 如果复杂度 ≥ 80，切换到complex-deep
4. **快速响应** - 如果是快速响应需求，切换到flash
5. **AI检测建议** - 根据AI检测结果推荐

---

## 🔍 日志和监控

**日志位置**：`/tmp/smart_model_logs/smart_model_YYYYMMDD.log`

**查看日志**：
```bash
# 查看今天的日志
tail -100 /tmp/smart_model_logs/smart_model_$(date +%Y%m%d).log

# 查看所有日志
ls -lh /tmp/smart_model_logs/
```

**上下文监控日志**：`/tmp/smart_model_context_monitor.log`

**预警通知**：`/tmp/smart_model_context_warning.txt`

---

## 🧪 测试

```bash
# 运行完整测试
./smart-model-v2.sh --test

# 测试结果示例
测试1：简单消息 "在吗？" → flash（快速响应）
测试2：代码任务 "帮我写一个Python函数" → coding（代码驱动）
测试3：深度分析 "请详细分析架构设计" → complex-deep（深度分析）
```

---

## 📦 文件结构

```
smart-model/
├── smart-model-v2.sh          # 主控制器（9.4KB）
├── README.md                   # 本文档
├── modules/                    # 核心模块（37.5KB）
│   ├── file_type_detector.sh  # 文件类型检测（8.3KB）
│   ├── complexity_analyzer.sh # 复杂度分析（9.2KB）
│   ├── context_monitor.sh     # 上下文监控（9.1KB）
│   └── ai_detector.sh         # AI主动检测（10.8KB）
└── logs/                       # 日志目录
    └── *.log
```

**总代码量**：1500+ 行（模块） + 300+ 行（主脚本） = 1800+ 行

---

## 🎯 Phase 1 MVP 完成情况

✅ **4个核心模块全部完成**
- [x] 文件类型检测模块
- [x] 复杂度分析模块
- [x] 上下文监控模块
- [x] AI主动检测模块

✅ **主控制器完成**
- [x] 模块加载机制
- [x] 综合决策逻辑
- [x] 快速切换API
- [x] 批量处理
- [x] 测试函数

✅ **文档和测试**
- [x] README文档
- [x] 完整测试用例
- [x] 日志系统

---

## 🚀 Phase 2 进度（2026-03-12）

**计划时间**：2026-03-12 ~ 2026-03-15

**核心功能**：
- [x] 与OpenClaw深度集成
  - ✅ openclaw_hook.sh（7.5KB）- 消息/文件/上下文钩子
  - ✅ model_switcher_api.sh（8.1KB）- 统一API接口
  - ✅ Git提交（7a22629）
- [ ] 实时上下文监控（待开发）
- [ ] 自动模型切换（待开发）
- [ ] 性能优化（待开发）

**高级功能**：
- [ ] 用户偏好学习
- [ ] 历史数据分析
- [ ] 智能预测
- [ ] 多模型协同

**当前进度**：Phase 2（2/4任务）50%完成

---

## 📝 更新日志

### v2.1.0 (2026-03-12 18:16)
- ✅ OpenClaw集成模块完成
- ✅ Model Switcher API完成
- ✅ Phase 2计划文档完成
- ✅ Git提交（7a22629）

### v2.0.0 (2026-03-12 17:55)
- ✅ 完成Phase 1 MVP
- ✅ 4个核心模块全部完成
- ✅ 主控制器完成
- ✅ 完整测试通过
- ✅ Git提交（bf25032）

---

## 👥 贡献者

- **小米粒**（开发代理）- 核心开发
- **米粒儿**（Review代理）- 代码审查（待执行）

---

**官家，Smart Model v2.0 Phase 1 MVP 已完成！** 🌾
