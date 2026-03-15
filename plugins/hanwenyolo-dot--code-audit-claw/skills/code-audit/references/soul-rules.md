# Soul File Audit Rules (OpenClaw 专属)

适用文件：SOUL.md / MEMORY.md / AGENTS.md / HEARTBEAT.md / USER.md / Skills SKILL.md

---

## 🔴 Critical (灵魂安全铁律缺失)

### SOUL.md 铁律完整性检查
必须包含以下关键条款（逐一检查）：
- [ ] **先沟通铁律**：禁止自行推进"诊断→修复→测试"完整流程
- [ ] **网关重启铁律**：`openclaw gateway restart` 永远只能由管理员手动执行
- [ ] **剁手规则**：exec/write/edit 前必须安全自检
- [ ] **称呼铁律**：定义代理与用户之间的称呼规范

### MEMORY.md 敏感信息检查
- 明文 API Key / Token / Password（pattern: 长度>20的随机字符串）
- 明文密码或私钥

### Skills SKILL.md 危险授权检查
- 是否存在允许"跳步执行"或"无需确认"的语句
- 是否有允许直接运行 `gateway restart` 的步骤

---

## 🟡 Warning (一致性问题)

### 跨文件规则冲突
- SOUL.md 铁律 vs AGENTS.md 协议是否互相矛盾
- MEMORY.md 中记录的规则是否与 SOUL.md 当前版本一致

### 记忆老化检测
- MEMORY.md 中标记为"进行中"的任务，最后更新超过 30 天
- Cron Jobs 中无注释/描述的定时任务

### USER.md 一致性
- USER.md 中的信息是否与 MEMORY.md 相关记录一致

---

## 🟢 Info (健康度建议)

### 版本追踪
- SOUL.md 是否有 `Last Updated` 记录
- AGENTS.md 是否有版本号和更新日期

### Skill 触发词冲突
- 检查所有 SKILL.md 的 description，是否有两个 Skill 的触发词高度重叠
- **规则细化**：当两个 Skill 的 description 中包含完全相同的触发词（中文词/英文词），应报 Warning
- 触发词定义：description 中引号包裹的词、"触发词："/「触发词」后列出的词组、Trigger on / Use when 段落中的关键短语
- 检测方式：提取所有 SKILL.md 中的触发词 → 建立倒排索引 → 相同触发词出现在 ≥2 个 Skill 中 → 报警

### Cron Jobs 无描述检测
- 扫描 `crontab -l` 或 OpenClaw cron list 输出，检测无注释/无描述的定时任务
- **规则细化**：Cron Job 行的上方没有 `#` 注释行 → 报 Warning
- 风险：运维时无法快速识别该任务的用途，容易误删或重复创建
- 检测方式：解析 cron 输出，每条 cron 表达式行检查前一行是否为注释行

### MEMORY.md 体积
- 超过 15K 字符时建议触发 memory-maintenance Skill 压缩

### Heartbeat 健康
- HEARTBEAT.md 中是否有会导致高频 API 调用的任务（每分钟触发）
