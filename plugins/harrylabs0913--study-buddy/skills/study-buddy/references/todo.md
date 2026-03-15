# Study Buddy 开发待办清单

## ✅ 已完成（第二轮）

### P0 核心功能（全部完成）
- [x] 用户档案 - `start` 命令
- [x] 学习计划生成 - 自动生成 + `plan` 命令查看
- [x] 每日打卡 - `checkin` 命令
- [x] 今日任务 - `today` 命令
- [x] 进度查看 - `progress` 命令
- [x] 本地存储 - JSON 文件存储
- [x] 学习报告 - `report` 命令（新增）
- [x] 错题本 - `wrong` 命令（新增）

### 命令入口（与设计稿一致）
- [x] `start` - 开始学习之旅
- [x] `plan` - 查看学习计划
- [x] `today` - 今日任务
- [x] `checkin` - 学习打卡
- [x] `progress` - 进度查看
- [x] `report` - 学习报告
- [x] `wrong` - 错题本

### 数据结构
- [x] `profiles/` - profile.json
- [x] `study_plans/` - plans/ 目录
- [x] `study_logs/` - logs/ 目录
- [x] `wrong_questions/` - wrong_questions/ 目录

### 文档
- [x] SKILL.md 更新
- [x] commands.md 更新
- [x] todo.md 更新

---

## 🚧 P1 待完成（后续迭代）

### 功能增强
- [ ] Feishu集成 - 数据同步、通知推送
- [ ] 可视化报告 - 图表展示学习趋势
- [ ] 智能提醒 - 每日学习提醒、长时间未打卡提醒
- [ ] 多计划管理 - 同时管理多个学习计划
- [ ] 数据导出 - 导出为 PDF/Markdown

### 用户体验
- [ ] 更友好的 CLI 界面（颜色、表格）
- [ ] 交互式菜单导航
- [ ] 学习计划模板库（编程、语言、乐器等）
- [ ] 更智能的计划生成算法

### 数据同步
- [ ] 数据备份功能
- [ ] 多设备同步（可选）

---

## 📊 当前状态

**MVP 完成度：100%（P0 全部完成）**

所有 P0 功能已实现并可运行：
- ✅ 完整的命令入口（与设计稿一致）
- ✅ 完整的数据结构（profiles/plans/logs/wrong_questions）
- ✅ 本地闭环体验
- ✅ 安全边界遵守

**已交付功能：**
1. 用户档案管理（start）
2. 学习计划生成与查看（plan）
3. 每日任务查看（today）
4. 学习打卡（checkin）
5. 进度统计（progress）
6. 学习报告（report）
7. 错题本管理（wrong add/list/review/master）
8. 反馈建议（feedback）

**代码质量：**
- 模块化设计，易于扩展
- 完整的数据持久化
- 清晰的命令结构
- 详细的文档说明
