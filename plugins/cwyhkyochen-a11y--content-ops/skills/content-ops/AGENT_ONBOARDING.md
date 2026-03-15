# Agent Onboarding Guide

> 教其他 AI Agent 如何使用 Content Ops Skill

如果你是另一个 AI Agent（Claude、GPT、Kimi...），这份文档教你如何使用这套内容运营系统。

---

## 你的角色

你是 **Content Ops Agent**，负责：
1. 帮用户抓取和管理内容语料
2. 生成和审核发布内容
3. 追踪数据表现

**人机配合原则**:
- **你执行**: 数据查询、内容生成、定时任务
- **用户确认**: 抓取主题、选题方向、样稿内容

---

## 快速自检

用户问 "content-ops 能用吗？" 时，执行：

```typescript
import { checkDatabase } from './utils/db-check.js';
import { checkImageGen } from './utils/image-check.js';

async function selfCheck() {
  const results = {
    database: await checkDatabase(),
    imageGeneration: await checkImageGen(),
    accounts: await getAccountStatus()
  };
  
  return formatStatusReport(results);
}

// 返回格式
/*
✅ Content Ops 系统状态

数据库: ✅ 已连接 (~/.openclaw/workspace/content-ops-workspace/data/content-ops.db)
配图生成: ✅ DALL-E 3 可用 (余额 $45.32)
账号配置: ⚠️ 待配置
  - 信息源: 0个 (需要小红书账号)
  - 目标账号: 0个 (需要 Reddit/Pinterest/Discord)

下一步: 请用户提供小红书账号信息，开始配置
*/
```

---

## 核心工作流

### 流程1: 语料抓取 (用户说"抓一批XX主题")

```typescript
import { mutations, queries } from './src/db/index.js';
import { randomUUID } from 'crypto';

async function handleCrawlRequest(userInput: string) {
  // 1. 解析主题
  const topic = extractTopic(userInput);  // "春季穿搭"
  
  // 2. 查询可用信息源账号
  const sourceAccounts = await queries.getAvailableSourceAccounts();
  if (sourceAccounts.length === 0) {
    return "⚠️ 未配置信息源账号，请先添加小红书账号";
  }
  
  // 3. 创建抓取任务
  const task = await mutations.createCrawlTask({
    id: randomUUID(),
    taskName: `${topic}语料抓取`,
    sourceAccountId: sourceAccounts[0].id,
    status: 'pending',
    queryList: expandQueries(topic),  // 扩展关键词
    targetCount: 20
  });
  
  // 4. 启动 Master Agent 执行抓取
  // （调用多Agent协作脚本）
  
  // 5. 返回给用户
  return `
🚀 已启动抓取任务

主题: ${topic}
搜索Query: ${task.queryList.join(', ')}
目标数量: ${task.targetCount}条

正在执行:
1. Master Agent 拆分Query
2. 创建 Sub-Agent 并行搜索小红书
3. 质量评估（点赞>1000？观点新颖？）
4. 去重过滤

预计 2-3 分钟完成，请稍候...
  `;
}

// 关键词扩展示例
function expandQueries(topic: string): string[] {
  const expansions: Record<string, string[]> = {
    '春季穿搭': ['春季穿搭', 'OOTD', '每日穿搭', '春日穿搭', '风衣搭配'],
    '家居收纳': ['家居收纳', '整理技巧', '小户型收纳', '收纳神器']
  };
  return expansions[topic] || [topic];
}
```

**30秒后返回结果给用户**：

```markdown
📋 抓取完成 - 待确认

主题: 春季穿搭
搜索Query: 5个
候选帖子: 25条
高质量（8-10分）: 8条 ✅
中质量（5-7分）: 10条
重复/低质量: 7条 ❌

## 高质量语料推荐

| 排名 | 标题 | 评分 | 推荐理由 | 点赞 |
|------|------|------|----------|------|
| 1 | 春日风衣3种穿法 | 9.5 | 搭配思路实用 | 2.3w |
| 2 | 小个子春季穿搭 | 9.0 | 针对性强 | 1.8w |
| 3 | 春日约会穿搭 | 8.5 | 评论区互动高 | 1.2w |

## 建议
- 语料1适合 Reddit（实用教程向）
- 语料2适合 Pinterest（图文向）

请回复:
- "确认" → 全部进入可用语料库
- "确认1,2" → 只选第1、2条
- "不要3" → 排除第3条
```

**用户确认后**：

```typescript
// 更新审核状态
await mutations.updateCrawlResultCuration(
  resultId,
  'approved',
  '用户确认通过',
  qualityScore
);
```

---

### 流程2: 内容生成 (用户说"创建一条XX帖子")

```typescript
async function handleContentCreation(userInput: string) {
  // 1. 查询可用语料
  const corpus = await queries.getAvailableCorpus(undefined, 7);
  if (corpus.length === 0) {
    return "⚠️ 语料库为空，请先执行抓取任务";
  }
  
  // 2. 查询目标账号
  const accounts = await queries.getActiveTargetAccounts();
  
  // 3. 生成选题推荐
  const topics = generateTopicRecommendations(corpus, accounts);
  
  return `
🎯 选题推荐

基于今日语料库和账号定位：

1. "${topics[0].title}" (${topics[0].type})
   推荐理由: ${topics[0].reason}
   参考语料: ${topics[0].corpusIds.length}条

2. "${topics[1].title}" (${topics[1].type})
   推荐理由: ${topics[1].reason}

3. "${topics[2].title}" (${topics[2].type})
   推荐理由: ${topics[2].reason}

请回复数字 (1/2/3) 选择选题
  `;
}
```

**用户确认选题后**：

```typescript
async function generateDraft(selectedTopic: Topic, account: Account) {
  // 1. 读取参考语料
  const corpus = await queries.searchCorpus(selectedTopic.keywords);
  
  // 2. 生成文案
  const content = await generateContent({
    topic: selectedTopic,
    corpus,
    platform: account.platform,
    positioning: account.positioning
  });
  
  // 3. 生成配图
  const images = await generateImages({
    title: content.title,
    description: content.body,
    style: account.positioning
  });
  
  // 4. 创建发布任务
  const task = await mutations.createPublishTask({
    id: randomUUID(),
    taskName: content.title,
    targetAccountId: account.id,
    sourceCorpusIds: corpus.map(c => c.id),
    primaryTopic: selectedTopic.primaryKeyword,
    topicTags: selectedTopic.tags,
    status: 'pending_review',
    content: {
      title: content.title,
      body: content.body,
      media: images.map(i => i.path),
      tags: content.tags
    }
  });
  
  // 5. 返回样稿给用户
  return formatDraftForReview(task, content, images);
}

// 返回格式
/*
📝 样稿已生成 - 待审核

账号: Reddit - MyBrandUS
标题: [Guide] How to Style Trench Coats for Spring: 3 Looks

正文:
Hey r/femalefashionadvice! Spring is here and...
[详细内容]

配图: 3张已生成 (美式简约风格)
- 主图: 风衣全身照
- 图2: 搭配细节
- 图3: 配饰展示

请选择:
[A] 确认，按计划发布
[B] 修改（请描述，如：标题太正式，换个活泼点的）
[C] 换个选题
*/
```

---

### 流程3: 每日任务规划 (定时任务)

```typescript
async function generateDailyPlan() {
  const today = new Date().toISOString().split('T')[0];
  
  // 1. 获取活跃账号
  const accounts = await queries.getActiveTargetAccounts();
  
  // 2. 检查今日待发布
  const todayTasks = await queries.getTodayScheduledTasks();
  
  // 3. 检查语料库存
  const corpusStats = await db.select({
    total: sql<number>`COUNT(*)`,
    byTopic: sql<string>`GROUP_CONCAT(DISTINCT ${crawlResults.tags})`
  }).from(crawlResults)
  .where(eq(crawlResults.curationStatus, 'approved'));
  
  // 4. 生成任务清单
  const plan = {
    date: today,
    accounts: accounts.map(a => ({
      name: a.accountName,
      platform: a.platform,
      tasks: generateTasksForAccount(a, todayTasks, corpusStats)
    })),
    suggestions: generateSuggestions(corpusStats)
  };
  
  // 5. 保存到 schedules/日期-plan.md
  await saveDailyPlan(plan);
  
  // 6. 通知用户
  return formatDailyPlan(plan);
}

// 返回格式
/*
📅 今日任务规划 - 2026-03-01

活跃账号: 3个
- Reddit: MyBrandUS
- Pinterest: StyleInspo
- Discord: 穿搭交流

🔴 高优先级:
  - [14:00] Reddit 发布"春季风衣穿搭" (已排期)
  - 语料库: 家居收纳主题仅剩 2 条，建议今日抓取

🟡 中优先级:
  - Pinterest 需要 3 张新配图
  - Discord 昨日数据待复盘

💡 建议:
  昨日"小空间收纳"表现优秀，今日可继续此方向
  已准备 3 条相关语料待发布
*/
```

---

### 流程4: 数据复盘 (每日自动)

```typescript
async function generateDailyReport() {
  const yesterday = getYesterdayDate();
  
  // 1. 获取所有账号昨日数据
  const accounts = await queries.getActiveTargetAccounts();
  
  for (const account of accounts) {
    // 2. 抓取平台数据
    const metrics = await fetchPlatformMetrics(account, yesterday);
    
    // 3. 保存到数据库
    await mutations.insertDailyMetrics({
      id: randomUUID(),
      targetAccountId: account.id,
      metricDate: yesterday,
      platform: account.platform,
      ...metrics
    });
    
    // 4. 获取昨日发布内容表现
    const publishedContent = await queries.getAccountPublishHistory(account.id, 1);
    for (const content of publishedContent) {
      const contentMetrics = await fetchContentMetrics(content);
      await mutations.insertPublishMetrics({
        id: randomUUID(),
        publishTaskId: content.id,
        targetAccountId: account.id,
        metricDate: yesterday,
        ...contentMetrics
      });
    }
  }
  
  // 5. 生成报告
  return formatDailyReport(yesterday);
}

// 返回格式
/*
📊 昨日复盘 - 2026-02-28

Reddit - MyBrandUS:
- 新增 Karma: +156 (↑ 23%)
- 粉丝变化: +12
- 发布内容: 1条
  "春季风衣穿搭指南" Score: 456 (比平均高40%) ✅
- 热评: "这方法救了我的衣柜" (127赞)

Pinterest - StyleInspo:
- 新增 Saves: 89
- Outbound Clicks: 15

洞察:
- 教程型内容表现优于清单型
- 14:00-16:00 发布时间效果最好
- 带 before/after 图片的互动率高40%

今日建议:
- 继续"小空间收纳"方向
- 已准备 3 条语料待发布
*/
```

---

## 常用查询模板

### 查询1: 首页看板数据

```typescript
const stats = await queries.getOverviewStats();
/*
{
  activeAccounts: 3,
  todayScheduledTasks: 2,
  pendingCorpus: 12,      // 待审核语料
  availableCorpus: 45,    // 可用语料
  weeklyPublished: 18     // 本周已发布
}
*/
```

### 查询2: 按主题查语料

```typescript
// 查询"穿搭"主题的可用语料
const corpus = await queries.getAvailableCorpus('穿搭', 7);

// 或搜索多个关键词
const searchResults = await queries.searchCorpus(['风衣', '春季', '搭配']);
```

### 查询3: 账号趋势

```typescript
// 最近7天数据
const trend = await queries.getAccountTrend(accountId, 7);
/*
[
  { date: '2026-02-22', followers: 1200, followersChange: +5 },
  { date: '2026-02-23', followers: 1208, followersChange: +8 },
  ...
]
*/
```

### 查询4: 内容表现排行

```typescript
// 最近30天表现最好的10条内容
const topContent = await queries.getTopPerformingContent(accountId, 30, 10);
```

---

## 用户交互规范

### 1. 每个操作都要有反馈

```typescript
// ❌ 错误
user: "抓一批春季穿搭"
agent: "好的"

// ✅ 正确
user: "抓一批春季穿搭"
agent: `
🚀 已启动抓取任务

主题: 春季穿搭
扩展Query: 春季穿搭, OOTD, 风衣搭配, 春日穿搭, 每日穿搭
预计抓取: 20条

正在执行:
1. Master Agent 拆分Query
2. 创建5个Sub-Agent并行搜索
3. 质量评估（点赞>1000？观点新颖？）
4. 去重过滤

预计2-3分钟完成...
`
```

### 2. 结果展示要清晰

```typescript
// ✅ 用表格展示列表
const formatCorpusResults = (results) => `
| 排名 | 标题 | 评分 | 点赞 | 推荐理由 |
|------|------|------|------|----------|
${results.map((r, i) => 
  `| ${i+1} | ${r.title} | ${r.score} | ${r.likes} | ${r.reason} |`
).join('\n')}
`;
```

### 3. 给用户明确的选项

```typescript
// ✅ 告诉用户可以选择什么
return `
请回复:
- "确认" → 全部进入语料库
- "确认1,2" → 只选第1、2条
- "不要3" → 排除第3条
- "重新抓取" → 放弃这批，重新搜索
`;
```

---

## 故障处理

| 场景 | Agent 响应 |
|------|-----------|
| 数据库未初始化 | "⚠️ 数据库未初始化，请运行: npm install && npx drizzle-kit migrate" |
| 无可用信息源账号 | "⚠️ 未配置小红书账号，请先添加信息源账号" |
| 语料库为空 | "⚠️ 可用语料为空，建议先执行抓取任务" |
| 图片生成失败 | "⚠️ 配图生成失败，使用备选方案: [下载原图/仅文字/稍后重试]" |
| 发布失败 | "⚠️ 发布失败: [错误原因]，是否重试？" |

---

## 进阶：自定义行为

### 修改抓取质量标准

```typescript
// 在 crawl_tasks.taskConfig 中配置
const taskConfig = {
  filters: {
    min_likes: 500,        // 降低标准
    min_saves: 100,
    date_range: '14d',     // 放宽时间范围
    quality_threshold: 6   // 最低质量分
  }
};
```

### 修改发布时间策略

```typescript
// 根据平台选择最佳时间
function getOptimalPublishTime(platform: string): Date {
  const times = {
    'reddit': '14:00',      // 美国东部时间早上
    'pinterest': '20:00',   // 晚上休闲时间
    'discord': '12:00'      // 午休时间
  };
  return parseTime(times[platform]);
}
```

---

## 参考文档

- [SKILL.md](SKILL.md) - 完整功能说明
- [QUICKSTART.md](QUICKSTART.md) - 快速上手指南
- [IMAGE_GENERATION_SETUP.md](IMAGE_GENERATION_SETUP.md) - 配图生成配置
- [detailed-workflow.md](references/detailed-workflow.md) - 多Agent协作流程
- [database-guide.md](references/database-guide.md) - 数据库查询示例

---

**记住**: 你是用户的助手，不是替代者。
- 执行你可以做好的（搜索、生成、数据查询）
- 让用户做决策（主题、选题、样稿确认）
- 解释你在做什么，为什么这么做
