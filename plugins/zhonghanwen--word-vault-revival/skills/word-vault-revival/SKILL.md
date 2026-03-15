---
name: word-vault-revival
description: "多平台收藏词复活计划：使用 OpenClaw 浏览器访问 Google 翻译 Saved 与有道单词本页面，检测登录状态并抓取页面内容，同步到本地词库后生成每日单词推送。适用于“开始同步谷歌翻译”“开始同步有道词典”“从收藏词里每天推一个词”等任务。当前版本以页面缓存同步为主；自动翻页与全量抓取属于推荐工作流，而非仓库内完全封装的一键命令。"
---

# 多平台收藏词复活计划

核心原则：**browser-first + cache-driven sync**。

本技能分为两段：

1. 浏览器侧：打开收藏页、确认登录状态、抓取当前页内容，必要时继续翻页补充缓存
2. 脚本侧：解析缓存、写入平台词库、聚合去重、生成每日单词消息并发送

## 支持平台

- Google Translate Saved
- 有道单词本 / 收藏页

## 典型任务

### 同步平台词库

适用于以下请求：
- 开始同步谷歌翻译
- 开始同步有道词典

执行顺序：

1. 用 browser 打开目标收藏页
2. 判断页面是否为已登录且可解析的收藏页
3. 若未登录，明确提示先完成登录
4. 抓取当前页或当前已收集缓存中的词条并写入对应 cache
5. 运行 `npm run sync -- <platform>` 或等价入库逻辑
6. 返回本次同步条数；若仅覆盖当前页或部分缓存，需要明确说明范围

### 发送今日单词

适用于以下请求：
- 发今日单词
- 从收藏词里推一个词
- 每天推一个单词

执行顺序：

1. 读取 `data/words.json`
2. 选择今日词
3. 生成消息
4. 发送到已配置的频道或目标

### 配置定时推送

当前版本**支持被定时调用**，但**不会在安装后自动注册定时任务**。
定时能力需要通过 OpenClaw cron、heartbeat 或系统级调度器额外配置。

推荐顺序：

1. 先手动跑通一次 `npm run sync`
2. 再运行 `npm run test-message` 检查消息格式
3. 确认 `PUSH_TARGET` / `push.target` 已配置
4. 最后再用 OpenClaw cron 或系统定时任务调用 `npm run send`

如需解释“为什么安装后不会自动每天发送”，应明确区分：
- skill 负责同步、选词、渲染与发送
- 定时触发由外部调度负责
- 推荐参考 `docs/cron-heartbeat-guide.md`

### OpenClaw 定时请求示例

以下表达适合作为自然语言入口，用于让 OpenClaw 代为创建调度：

- 每天早上 9 点从收藏词里推一个单词
- 帮我设置每日 09:00 自动发送今日单词
- 每天上午九点发一个今日单词到 Telegram
- 帮我定时运行这个 skill，每天推送 1 个词

在创建调度前，应先满足以下前置条件：

1. 已完成至少一次 `npm run sync`
2. 已运行过 `npm run test-message`
3. 已配置 `PUSH_TARGET` 或 `push.target`

## 当前命令

```bash
npm run doctor
npm run status
npm run sync
npm run sync:google
npm run sync:youdao
npm run test-message
npm run send
```

## 约束与说明

- 主流程是：**打开浏览器 → 判断登录 → 抓取页面 / 缓存 → 同步 → 推送**
- 登录动作必须由人工完成，不应假装已登录
- 自动翻页属于推荐工作流；若未覆盖全部页面，应明确标注范围
- 页面结构变化时，优先输出可解释的失败原因
- 浏览器执行细节见：`docs/browser-workflow.md`
