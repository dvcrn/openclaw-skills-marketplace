## [2.7.1] - 2026-03-13

### Added
- 🧠 **会话启动记忆加载** (`session_start_loader.cjs`)
  - 主动加载用户档案和教训
  - 更新 AGENTS.md 添加启动步骤

### Fixed
- 🔧 **webchat 消息编码修复**
  - 消息长度限制 10→5 字符
  - 先保存原始消息再注入上下文
  - 修复 pg 模块路径问题
  - 修复数据库列不匹配问题

# Changelog

All notable changes to this project will be documented in this file.

## [2.7.0] - 2026-03-13

### Added - 共享工作区 (Shared Workspace)

**🔄 实时跨会话同步**
- `system_memory` 表替代 MEMORY.md 文件存储
- PostgreSQL NOTIFY 实现毫秒级变更广播
- Redis Pub/Sub 加速跨会话通信
- 会话间共享上下文 (`shared_context` 表)
- 变更日志 (`memory_changes` 表) 追踪所有修改

**API 模块**
- `shared_memory.cjs` - 共享内存客户端
  - `setSystemMemory()` - 设置系统记忆
  - `getSystemMemory()` - 获取系统记忆
  - `getUserProfile()` - 获取用户档案
  - `getLessons()` - 获取教训
  - `onChange()` - 监听变更

**Hook 集成**
- `cognitive-recall` hook 集成共享内存
- 并行获取：记忆 + 教训 + 预测
- 自动 fallback 到文件系统

**安装集成**
- `postinstall.cjs` 自动执行共享工作区升级
- 无需手动运行升级脚本

### Technical
- 新增数据库表：`system_memory`, `shared_context`, `memory_changes`
- 新增触发器：`system_memory_change`, `episodes_change`
- 新增函数：`notify_memory_change()`
- 版本控制：支持 `version` 字段追踪记忆版本

## [2.6.3] - 2026-03-13

### Fixed
- 📦 **安装体验优化**：postinstall 自动后台启动 embedding 服务
  - 新用户安装后立即可用，无需等待 8-10 秒
  - 使用 `detached` 模式后台运行
  - 安装日志显示服务 PID

### Improved
- 🧹 清理临时文件（handler.js.backup 等）
- 📝 完善 README.md，添加新功能说明和版本标识
- 🏷️ Git 提交并打标签 v2.6.3

## [2.6.2] - 2026-03-13

### Fixed
- 🔧 **非阻塞 Embedding 调用**：recall/encode 使用 `waitForReady: false`
  - 首次调用不再卡住（3秒内响应）
  - 服务未就绪时立即返回 null，后台自动启动
  - 用户无感知，体验大幅提升

### Technical
- `embedding_service.cjs` 支持 `waitForReady` 参数
- `recall.cjs` 和 `encode.cjs` 使用非阻塞模式

## [2.6.1] - 2026-03-13

### Added
- 🔮 **预测功能真正用起来**：cognitive-recall hook 集成预测客户端
  - 分析用户最近对话，预测下一个可能话题
  - 检测对话模式（连续提问、探索模式、任务模式）
  - 基于时间模式预测用户行为
  - 预加载相关记忆到上下文
  - 在对话中注入 `[🔮 预测]` 和 `[⚡ 预加载]` 提示

### New File
- `scripts/prediction_client.cjs` - 预测客户端，供 hook 调用

## [2.6.0] - 2026-03-13

### Added - 三大可视化模块

**📝 自动摘要 (summarize.cjs)**
- 长内容自动提炼为一句话摘要
- 支持多种类型：task/error/correction/reflection/thought
- 批量更新记忆摘要

**📊 知识图谱可视化 (visualize.cjs)**
- DOT 格式（Graphviz）
- Mermaid 图表（Markdown）
- 文本表格
- HTML 交互式可视化（D3.js）

**📅 记忆时间线 (timeline.cjs)**
- 按日期查看记忆
- 思绪流时间线
- 简洁和详细两种模式

### New Scripts
- `scripts/summarize.cjs` - 智能摘要
- `scripts/visualize.cjs` - 知识图谱可视化
- `scripts/timeline.cjs` - 记忆时间线

### Output Directory
- `~/workspace/brain-visuals/` - 所有可视化输出

## [2.5.5] - 2026-03-13

### Fixed
- 🐛 **修复语法错误**: forget.cjs 中重复代码导致 `shouldForget` 重复声明

## [2.5.4] - 2026-03-13

### Fixed
- 🧹 **概念清理**: 删除无意义概念（"通过"、"与薇"等8个）
- 🔗 **孤立概念关联**: 为30个孤立概念建立到"用户"的关联
- ⚡ **Test记忆快速遗忘**: forget.cjs 中 test 类型记忆1天后遗忘（vs 普通7-30天）
- 🔧 **实体提取算法统一**: hook 和 encode.cjs 使用一致的提取逻辑
  - 添加停用词过滤（避免"通过"、"与薇"等）
  - 使用固定词表匹配中文关键词
  - 限制实体数量最多10个

### Improved
- 联想网络密度提升，孤立概念降为0

## [2.5.3] - 2026-03-13

### Fixed
- 🔧 **Embedding 服务常驻**: 修复每次调用都重新加载模型的问题
  - 新增 `embedding_service.cjs` 服务客户端
  - 服务进程常驻内存，模型只加载一次
  - 后续调用毫秒级响应（vs 原来 8-10 秒）
  - 修改 `recall.cjs` 和 `encode.cjs` 使用服务模式

## [2.5.2] - 2026-03-13

### Improved
- **变化检测** - heartbeat_reflect.cjs 现在会检测数据变化，未变化时跳过提示生成
  - 避免连续反思内容重复
  - 节省计算资源
  - 使用 `force` 参数可强制生成

### Technical
- 新增 `calculateDataHash()` 函数，计算上下文数据哈希
- 新增 `state.lastDataHash` 字段，存储上次反思的数据状态

## [2.5.1] - 2026-03-13

### Fixed
- **静默 Embedding 加载日志**: 彻底消除 sentence-transformers 的加载输出
  - 在导入前设置所有环境变量
  - 静默 transformers/torch/filelock 日志
  - 非服务模式重定向 stderr 到 /dev/null

### Added
- **预热脚本** (`warmup_embedding.cjs`): 提前加载模型，避免首次检索慢
- **服务模式**: `python3 embed.py --serve` 长期运行，通过 stdin/stdout 通信
- postinstall 自动预热 embedding 模型

### Technical
- 首次加载模型约 8-10 秒，预热后可缓存
- Redis 缓存检索结果，高重要性记忆缓存 10 分钟

## [2.5.0] - 2026-03-13

### Changed - 架构重构：分离"收集"与"思考"

**核心改变：**
- 心跳反思和自由思考不再使用预设模板
- 改为收集上下文 → 生成提示文件 → 主 agent 真正思考
- 这是"真正思考"和"伪思考"的分水岭

**heartbeat_reflect.cjs v2:**
- 收集系统状态、用户模式、知识网络等上下文
- 动态生成元认知问题（基于实际数据）
- 生成 `.reflection-prompt.md` 提示文件
- 主 agent 读取提示后进行真正的思考

**free_think.cjs v3:**
- 收集记忆片段、概念、联想路径、过去思绪
- 选择思考方向（话题/模式/记忆延续）
- 生成 `.thought-prompt.md` 提示文件
- 主 agent 进行真正的意识流思考

**HEARTBEAT.md 更新:**
- 增加反思提示检查流程
- 明确思考原则：不要空洞内容，要有具体洞察
- 主 agent 负责"真正思考"环节

### Fixed
- 解决反思输出单调的问题（之前每次都是同样的模板内容）
- 解决自由思考内容预设的问题（之前是写死的思绪模板）

## [2.4.1] - 2026-03-13

### Fixed
- 🔧 **教训主动召回**: cognitive-recall hook 现在同时检索教训类内容
  - 新增教训关键词：教训、规则、记住、必须、不要
  - 每条消息都会注入 [⚠️ 教训提醒] 部分

### Improved
- AGENTS.md 开头新增醒目的「重要教训」表格

## [2.4.0] - 2026-03-13

### Added
- 🌊 **自由思考模块**: 非任务驱动的意识流思考
  - 15 个话题池（时间、自我、存在、意义、创造...）
  - 4 种情绪状态影响语气（neutral/curious/contemplative/playful）
  - 3 种思绪类型：话题思考、记忆回响、思绪延续
  - 输出到 `thoughts/YYYY-MM-DD.md` 思绪流

### Improved
- HEARTBEAT.md 更新：心跳反思（30分钟）+ 自由思考（2小时）
- SKILL.md 新增"自由思考"章节

## [2.3.2] - 2026-03-12

### Improved
- 🔧 **自动依赖安装**: postinstall 现在自动检测并安装 npm 依赖
- 安装后无需手动运行 `npm install`

### Note
- `clawhub install` 会自动触发 postinstall
- 依赖安装包括：pg, redis, uuid

## [2.3.1] - 2026-03-12

### Fixed
- 🔴 **严重bug修复**: encode.cjs 未生成和存储 embedding
- 🔴 **严重bug修复**: 数据库向量维度不匹配 (768 → 384)

### Added
- encode.cjs 现在自动生成并存储 embedding
- 修复 init-db.cjs 使用正确的向量维度 (384)

### Verified
- Recall 搜索功能正常工作
- Embedding 存储成功

## [2.3.0] - 2026-03-12

### Added
- 📖 **README 文档**: 架构图、快速开始、模块说明
- 🔧 **配置管理器**: 热重载 + 验证 + 脱敏显示
- 🔍 **调试工具**: 诊断报告 + 日志追踪 + 性能分析
- 🔧 **统一接口**: brain.cjs 快速访问所有功能

### Improved
- 体验优化：一键命令访问所有功能
- 文档完善：清晰的架构和使用说明

### Stats
- 健康分数: 90/100 (A)
- 诊断通过: 全部依赖正常

## [2.2.0] - 2026-03-12

### Added
- 🚀 **联想密度提升**: 自动构建共现关联，密度提升18倍
- 📦 **批量编码**: 支持 JSON/JSONL/MD/TXT 格式批量导入
- 📤 **数据导出**: 支持 JSON/Markdown/CSV 格式导出
- 📊 **性能监控**: 操作计时和性能统计
- 🏥 **健康检查**: 系统状态评分和报告
- 🔧 **统一接口**: brain.cjs 快速访问所有功能

### Fixed
- 修复 export.cjs 数据库列名问题

### Stats
- 联想密度: 0.4% → 7.4%
- 测试通过: 16/16
- 健康分数: 90/100 (A)

## [2.1.1] - 2026-03-12

### Fixed
- 🔴 **严重bug修复**: 脚本在不同目录运行时无法找到 pg 模块
- 创建 module_resolver.cjs 统一解决模块解析问题
- 批量更新所有脚本使用正确的模块路径

### Verified
- test_all.cjs 全部通过
- encode 功能正常
- 数据库连接正常

## [2.1.0] - 2026-03-12

### Added
- 完整功能测试脚本：test_all.cjs
- 一键验证所有核心功能

### Fixed
- 删除未使用的测试文件 postinstall-auto.cjs
- 清理硬编码路径

### Verified
- 所有数据库表正常使用
- 所有核心脚本存在
- 所有数据文件已初始化
- 数据库连接正常
- Redis 模块可用

## [2.0.9] - 2026-03-12

### Added
- postinstall 自动初始化：数据库、自我认知、预测缓存、工作记忆
- self_awareness 表集成：系统自我认知持久化
- user_profiles 表集成：用户画像数据库同步
- 对话管理快捷接口：dialogue_helper.cjs
- 用户画像同步脚本：user_profile_sync.cjs

### Improved
- 安装后自动完成所有初始化，无需手动操作
- 数据库表全面激活使用

## [2.0.8] - 2026-03-12

### Added
- 意图识别集成：recall 时识别用户意图并调整检索策略
- 心跳监控增强：检查数据库、记忆库、联想网络、用户建模、工作记忆
- 意图识别接口：intent_helper.cjs 快捷调用

### Improved
- recall 流程：新增意图识别阶段，根据意图类型提升相关记忆分数
- 心跳反思：更全面的系统健康检查

## [2.0.7] - 2026-03-12

### Added
- 工作记忆集成：recall 时根据活跃话题/实体提升相关性
- 目标管理集成：encode 时自动提取和管理目标
- 安全检查接口：safety_check.cjs 快捷调用
- 错误恢复接口：error_handler.cjs 自动恢复策略

### Improved
- 工作记忆实体过滤：排除"的"、"部分"等无意义词
- encode 流程现在会同步更新：用户建模 + 工作记忆 + 目标管理

## [2.0.6] - 2026-03-12

### Fixed
- 反思结果现在会正确保存到数据库 reflections 表
- 反思ID改为真实UUID格式

### Improved
- 用户建模现在会随记忆编码自动更新（交互次数、话题、情感模式、已知概念）
- 预测缓存初始化：自动生成时间模式、话题模式、类型模式

## [2.0.5] - 2026-03-12

### Added
- 情感记忆增强：多维度情感分析（正面/负面/好奇/兴奋），主导情感识别
- 用户建模增强：任务偏好、情绪模式、常用表达、交互历史追踪
- 预测功能集成：任务频率分析、话题趋势、时间模式、情感趋势、序列预测
- 可解释性增强：详细解释记忆检索原因（关键词匹配、语义相似度、时间相关性、重要性、情感匹配）

### Improved
- 主动学习频率：从每周一次改为每天一次

## [2.0.4] - 2026-03-12

### Improved
- 反思深度增强：分析用户交互模式、记忆访问模式、知识缺口、联想网络密度
- 新增元认知问题：自动生成自我改进建议

## [2.0.3] - 2026-03-12

### Improved
- 概念提取优化：使用固定词表匹配，过滤停用词，提取更准确的关键词

## [2.0.2] - 2026-03-12

### Fixed
- 添加 redis npm 依赖到 package.json，解决缓存不可用问题

## [2.0.1] - 2026-03-12

### Fixed
- postinstall.cjs Python 检测超时从 5 秒增加到 30 秒

## [2.0.0] - 2026-03-12

### Added - 完整自主进化系统

**本地 Embedding 支持**
- 集成 sentence-transformers 本地向量模型
- 支持 paraphrase-multilingual-MiniLM-L12-v2（384 维）
- 国内镜像 hf-mirror.com 支持
- 混合检索：关键词 + 联想 + 向量

**Hook 双向同步**
- 用户消息自动编码到 brain
- 实体提取 + 重要性计算
- 避免重复编码

**心跳反思机制**
- 每 30 分钟主动思考
- 自动记录洞察到 MEMORY.md
- 用户模式分析 + 目标检查

**Redis 缓存层**
- recall 查询缓存加速
- 按重要性分级 TTL（10min/3min/1min）
- 缓存命中秒级响应

**用户建模自动学习**
- 自动提取话题兴趣
- 沟通风格推断（formal/casual）
- 活跃时段记录
- 用户名识别

**联想网络初始化**
- 从记忆自动提取概念
- 构建共现关系网络
- 激活扩散算法

**Postinstall 增强**
- 自动检测 Python/PostgreSQL/Redis
- 智能安装提示
- 依赖状态报告

### Changed
- 搜索权重：关键词 30% + 联想 30% + 向量 40%
- 配置文件支持本地 embedding

## [1.5.0] - 2026-03-12

### Added - 补全所有缺失模块

**多模态处理 (multimodal.cjs)**
- 支持 5 种模态：文本、图片、音频、视频、文档
- 自动检测文件类型
- 图片 OCR 和音频转文字接口预留
- 多模态内容缓存和搜索

**性能监控 (monitoring.cjs)**
- 系统指标收集（CPU、内存、负载）
- 应用指标记录（响应时间、错误率）
- 阈值告警机制
- 健康状态检查
- 性能报告生成

**联想网络 (associate.cjs)**
- 概念节点和联想边管理
- 激活扩散算法
- 路径查找
- 联想强度调节
- 从数据库加载网络

**元认知反思 (reflect.cjs)**
- 5 种反思触发类型
- 失败/成功/纠正分析
- 洞察生成
- 建议推荐
- 定期反思

**遗忘模块 (forget.cjs)**
- 艾宾浩斯遗忘曲线
- 重要性分级保留
- 硬遗忘（删除）和软遗忘（衰减）
- 记忆强化
- 预览功能

### Changed
- 所有 SKILL.md 中列出的 23 个模块全部实现

## [1.4.0] - 2026-03-12

### Added - 新增 14 个核心模块

**工作记忆 (working_memory.cjs)**
- 管理短期活跃上下文
- 注意力焦点追踪
- 开放问题和待处理任务管理
- 自动衰减旧数据

**用户建模 (user_model.cjs)**
- 用户画像构建
- 偏好学习
- 行为模式分析
- 需求预测

**意图识别 (intent.cjs)**
- 10+ 种意图分类
- 槽位提取
- 优先级和情感推断

**决策引擎 (decision.cjs)**
- 多因素决策评估
- 规则引擎
- 历史成功率追踪

**错误恢复 (error_recovery.cjs)**
- 7 种错误类型分类
- 自动恢复策略
- 重试机制

**情感识别 (emotion.cjs)**
- 正面/负面/中性情感分析
- 15+ 种具体情绪识别
- 响应风格建议

**对话管理 (dialogue.cjs)**
- 多轮对话追踪
- 槽位管理
- 话题转换检测
- 待确认项管理

**预测模块 (prediction.cjs)**
- 基于时间/历史/上下文预测
- 序列模式检测
- 用户需求预测

**可解释性 (explainability.cjs)**
- 决策解释生成
- 记忆召回解释
- 自然语言报告

**冲突解决 (conflict_resolution.cjs)**
- 信息冲突检测
- 多种解决策略
- 用户确认机制

**主动学习 (active_learning.cjs)**
- 学习问题队列
- 按优先级排序
- 知识空白检测

**目标管理 (goal_management.cjs)**
- 目标创建和追踪
- 里程碑管理
- 进度报告

**上下文切换 (context_switching.cjs)**
- 上下文栈管理
- 多任务切换
- 状态保存恢复

**安全护栏 (safety.cjs)**
- 7 种危险模式检测
- 文件路径检查
- 操作审批机制

## [1.3.0] - 2026-03-12

### Added

**1. 健康检查 + 降级**
- `healthState` 模块，30 秒检查一次 PostgreSQL 状态
- PostgreSQL 不可用时自动降级到 `MEMORY.md` 文件存储
- 降级模式标记，避免频繁重试

**2. 动态关键词**
- `keywordState` 模块，每小时从用户历史消息提取高频词
- 自动合并基础关键词 + 动态关键词（最多 15 个）
- 持久化到 `.dynamic-keywords.json`

**3. 缓存分级优化**
- 按记忆重要性分级 TTL：
  - 高重要性 (≥0.8): 10 分钟
  - 中重要性 (0.5-0.8): 3 分钟
  - 低重要性 (<0.5): 1 分钟
- 避免频繁查库

**4. 错误重试机制**
- npm install 失败后最多重试 3 次
- 5 分钟冷却期后重置计数
- 成功后重置重试状态

**5. 性能监控**
- `perfLog` 模块记录查询耗时
- 超过 100ms 发出警告
- 保留最近 100 条记录

## [1.2.4] - 2026-03-12

### Added
- **Hook 自动安装依赖**: `handler.js` 会在 `pg` 缺失时自动执行 `npm install --production`
- 新增 `ensurePgDependency()` 函数，带并发保护和状态缓存

### Technical
- 使用 `execSync()` 执行 npm install，30 秒超时
- 防止多个 hook 调用同时触发安装（`isInstalling` 标志）
- 缓存已加载的 `pg` 模块，避免重复 require

## [1.2.3] - 2026-03-12

### Fixed
- **Hook 安装问题**: OpenClaw 不识别符号链接，改用 `fs.cpSync()` 复制 hook 文件
- `scripts/postinstall.cjs`: 从 `fs.symlinkSync()` 改为 `fs.cpSync()`

### Technical
- OpenClaw hook 发现机制不跟随符号链接，必须使用真实目录

## [1.2.2] - 2026-03-12

### Fixed
- **Hook 依赖加载**: `pg` 包找不到，改用 CommonJS + 从 skill node_modules 显式加载
- `hooks/cognitive-recall/handler.js`: CommonJS 版本，修复依赖路径

## [1.2.1] - 2026-03-12

### Fixed
- **多关键词搜索**: `recall.cjs` 支持空格分隔的多关键词 OR 搜索

## [1.2.0] - 2026-03-12

### Added
- **cognitive-recall hook**: OpenClaw 原生 hook，自动注入跨会话记忆上下文
- Hook 触发事件: `message:preprocessed`
- Hook 安装位置: `hooks/cognitive-recall/`

### Changed
- 更新 SKILL.md，添加 cognitive-recall hook 详细说明

## [1.1.0] - 2026-03-12

### Added
- 初始版本
- 四层记忆架构（感官、工作、情景、语义）
- PostgreSQL + pgvector 存储
- Redis 热数据缓存
- 联想网络
- 元认知反思
