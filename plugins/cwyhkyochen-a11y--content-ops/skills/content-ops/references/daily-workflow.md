# Content Ops - 完整一日工作流

## 核心概念

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  信息源账号  │────▶│   语料库    │────▶│  被运营账号  │
│  (小红书)   │     │ (crawl_results)│   │(Reddit等)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │ 抓取任务           │ 审核              │ 发布任务
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ crawl_tasks │     │  人工审核   │────▶│ publish_tasks│
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  每日数据    │
                                        │  复盘报告    │
                                        └─────────────┘
```

---

## 📅 完整一日工作流（时间线）

### 【08:00】晨间启动 - 数据抓取（昨日数据）

**触发方式**: 定时任务 / 手动触发

**执行步骤**:
```
1. 读取所有活跃的被运营账号 (target_accounts)
   ├─ 检查每个账号的 API 状态
   └─ 记录需要抓取的账号列表

2. 对每个账号执行数据抓取
   ├─ 抓取粉丝数、Karma、帖子数据等
   └─ 插入到 target_accounts_metrics_daily

3. 抓取昨日发布内容的今日数据
   ├─ 查询昨日发布的所有帖子 (publish_tasks)
   ├─ 抓取每个帖子的互动数据 (score, comments, saves等)
   └─ 插入到 publish_metrics_daily

4. 生成晨间报告
   ├─ 昨日粉丝增长
   ├─ 昨日发布内容表现
   └─ 待办任务提醒
```

**数据库操作**:
```typescript
// 1. 获取活跃账号
const accounts = await queries.getActiveTargetAccounts();

// 2. 插入账号每日数据
await mutations.insertDailyMetrics({
  targetAccountId: account.id,
  metricDate: '2024-01-15',
  followers: 1000,
  followersChange: +50,
  // ...
});

// 3. 插入内容每日数据
await mutations.insertPublishMetrics({
  publishTaskId: task.id,
  metricDate: '2024-01-15',
  redditScore: 100,
  redditComments: 20,
  // ...
});
```

**输出**: 
- 今日数据看板（粉丝增长、内容表现）
- 待办任务清单

---

### 【09:00】上午工作 - 语料抓取与审核

#### 9:00-9:30 创建抓取任务

**触发方式**: 人工确认主题 / 定时任务（基于策略）

**执行步骤**:
```
1. 人工确认今日抓取主题
   └─ 例如："春季穿搭"

2. 选择信息源账号
   ├─ 检查 source_accounts 中状态为 active 的账号
   ├─ 检查配额 (quota_used_today < daily_quota)
   └─ 选择可用账号

3. 创建抓取任务 (crawl_tasks)
   ├─ 生成搜索词：["春季穿搭", "OOTD", "春日穿搭"]
   ├─ 设置目标数量：50条
   └─ 状态：pending

4. 执行抓取
   ├─ 使用浏览器自动化访问小红书
   ├─ 搜索关键词，抓取笔记数据
   ├─ 插入到 crawl_results（状态：raw）
   └─ 更新 crawl_tasks 状态为 completed
```

**数据库操作**:
```typescript
// 1. 创建抓取任务
const task = await mutations.createCrawlTask({
  id: crypto.randomUUID(),
  taskName: '春季穿搭-20240115',
  sourceAccountId: sourceAccount.id,
  status: 'pending',
  queryList: ['春季穿搭', 'OOTD', '春日穿搭'],
  targetCount: 50,
});

// 2. 批量插入抓取结果
await mutations.batchInsertCrawlResults([
  {
    id: crypto.randomUUID(),
    taskId: task.id,
    sourceAccountId: sourceAccount.id,
    platform: 'xiaohongshu',
    sourceUrl: 'https://xiaohongshu.com/...',
    title: '春日简约穿搭分享',
    content: '...',
    engagement: { likes: 1000, saves: 500 },
    curationStatus: 'raw',
  },
  // ... 更多结果
]);
```

**输出**:
- 抓取完成通知："已抓取35条内容，待审核"

---

#### 9:30-10:30 人工审核语料

**触发方式**: 抓取完成通知 / 手动查看

**执行步骤**:
```
1. 查询待审核语料
   └─ SELECT * FROM crawl_results WHERE curation_status = 'raw'

2. 人工逐条审核
   ├─ 查看标题、内容、图片、互动数据
   ├─ 判断是否可用（质量、版权、适配性）
   └─ 评分（1-10分）

3. 更新审核状态
   ├─ 可用：curation_status = 'approved', is_available = true
   └─ 不可用：curation_status = 'rejected'
```

**数据库操作**:
```typescript
// 获取待审核内容
const pending = await queries.getPendingCrawlResults(20);

// 审核通过
await mutations.updateCrawlResultCuration(
  resultId,
  'approved',
  '质量不错，适合改编',
  8,  // quality_score
  'kyo'  // curated_by
);

// 审核拒绝
await mutations.updateCrawlResultCuration(
  resultId,
  'rejected',
  '图片质量太低',
  3,
  'kyo'
);
```

**输出**:
- 可用语料库增加
- 审核统计："今日审核35条，通过20条，拒绝15条"

---

### 【10:30-12:00】内容生成

**触发方式**: 基于策略自动 / 手动创建

**执行步骤**:
```
1. 检查今日发布计划
   ├─ 查询 publish_tasks 中 scheduled_at = 今日 且 status = scheduled
   └─ 确定需要生成的内容数量

2. 选择语料
   ├─ 从 crawl_results 查询 curation_status = 'approved' AND is_available = true
   ├─ 按质量分排序 (quality_score DESC)
   ├─ 选择与账号定位匹配的语料
   └─ 标记已使用的语料 (usage_count++)

3. 创建发布任务 (publish_tasks)
   ├─ 状态：draft
   ├─ 关联语料ID列表 (source_corpus_ids)
   ├─ 记录改编类型 (translated/adapted)
   └─ 设置计划发布时间

4. 生成内容
   ├─ 翻译/改编标题
   ├─ 翻译/改编正文
   ├─ 选择/生成配图
   ├─ 添加标签
   └─ 更新任务状态为 pending_review
```

**数据库操作**:
```typescript
// 1. 查询可用语料
const corpus = await queries.getAvailableCorpus('穿搭', 7);

// 2. 创建发布任务
const publishTask = await mutations.createPublishTask({
  id: crypto.randomUUID(),
  taskName: '春季穿搭-Reddit发布',
  targetAccountId: redditAccount.id,
  sourceCorpusIds: [corpus[0].id, corpus[1].id],
  status: 'draft',
  contentType: 'translated',
  content: {
    title: 'Spring Minimalist Outfit Ideas',
    body: '...',
    media: ['path/to/image1.jpg'],
    tags: ['fashion', 'spring', 'minimalist'],
    platformSpecific: {
      reddit: { subreddit: 'r/femalefashionadvice' }
    }
  },
  scheduledAt: new Date('2024-01-15T14:00:00'),
});

// 3. 更新为待审核
await mutations.updatePublishTaskStatus(
  publishTask.id,
  'pending_review'
);
```

**输出**:
- 待审核的发布内容（标题、正文、配图）

---

### 【14:00-15:00】内容审核

**触发方式**: 内容生成完成通知 / 手动查看

**执行步骤**:
```
1. 查询待审核发布任务
   └─ SELECT * FROM publish_tasks WHERE status = 'pending_review'

2. 人工审核
   ├─ 检查标题是否吸引人
   ├─ 检查正文是否通顺、有无错误
   ├─ 检查配图是否合适
   └─ 检查是否符合平台规范

3. 更新状态
   ├─ 通过：status = 'approved'，准备发布
   ├─ 修改：修改内容后 status = 'pending_review'
   └─ 拒绝：status = 'cancelled'
```

**数据库操作**:
```typescript
// 获取待审核发布任务
const pendingTasks = await queries.getPendingReviewTasks();

// 审核通过，进入排期
await mutations.updatePublishTaskStatus(
  taskId,
  'approved',
  '内容质量高，可以发布'
);
```

---

### 【15:00-16:00】内容发布

**触发方式**: 到达计划发布时间 / 手动触发

**执行步骤**:
```
1. 查询今日待发布任务
   └─ SELECT * FROM publish_tasks 
      WHERE status = 'approved' 
      AND scheduled_at <= NOW()

2. 执行发布
   ├─ 调用各平台API（Reddit/Pinterest/Discord）
   ├─ 记录发布后的平台URL
   └─ 更新任务状态为 published

3. 记录发布信息
   ├─ 更新 publish_tasks.published_at
   ├─ 更新 publish_tasks.post_url
   └─ 关联到账号的已发布列表
```

**数据库操作**:
```typescript
// 获取今日待发布
const tasks = await queries.getTodayScheduledTasks();

// 发布后更新状态
await mutations.updatePublishTaskStatus(
  taskId,
  'published',
  '发布成功'
);
```

**输出**:
- 已发布内容列表 + 链接

---

### 【20:00】晚间复盘 - 数据汇总

**触发方式**: 定时任务

**执行步骤**:
```
1. 抓取今日发布内容的实时数据
   ├─ 查询今日发布的所有帖子
   ├─ 抓取每个帖子的 score, comments, saves 等
   └─ 插入到 publish_metrics_daily

2. 更新账号数据
   ├─ 抓取粉丝数、Karma 等
   └─ 插入到 target_accounts_metrics_daily

3. 生成复盘报告
   ├─ 今日发布内容表现排名
   ├─ 粉丝增长趋势
   ├─ 互动率分析
   └─ 明日建议
```

**数据库操作**:
```typescript
// 1. 获取今日发布内容
const todayPosts = await queries.getAccountPublishHistory(accountId, 10);

// 2. 插入内容数据
await mutations.insertPublishMetrics({
  publishTaskId: post.id,
  metricDate: '2024-01-15',
  redditScore: 150,
  redditComments: 25,
  // ...
});

// 3. 获取Top内容
const topContent = await queries.getTopPerformingContent(accountId, 1, 5);
```

**输出**:
- 每日复盘报告（Markdown格式，保存到 reports/）

---

## 🔄 状态流转图

### crawl_results（抓取结果）状态流转

```
raw ──▶ reviewing ──▶ approved ──▶ used
 │         │             │
 │         └────▶ rejected          
 │                      │
 └──────────────────────┘
        (可被重新审核)
```

- **raw**: 刚抓取，未审核
- **reviewing**: 正在审核中
- **approved**: 审核通过，可用
- **rejected**: 审核拒绝，不可用
- **used**: 已被用于发布（usage_count > 0）

### publish_tasks（发布任务）状态流转

```
draft ──▶ pending_review ──▶ approved ──▶ scheduled ──▶ published
 │             │                │            │
 │             └────▶ rejected  │            └────▶ failed
 │                              │
 └──────────────────────────────┘
            (可回到draft修改)
```

- **draft**: 草稿，正在编辑
- **pending_review**: 待人工审核
- **approved**: 审核通过，等待发布
- **scheduled**: 已排期，等待执行
- **published**: 已发布
- **failed**: 发布失败
- **rejected**: 审核未通过
- **cancelled**: 已取消

---

## 📋 每日工作清单（简化版）

### 早晨（自动）
- [ ] 08:00 抓取昨日数据（粉丝、内容表现）
- [ ] 08:30 生成晨间报告

### 上午（人工+自动）
- [ ] 09:00 确认今日抓取主题
- [ ] 09:15 执行抓取任务
- [ ] 09:30 审核抓取结果（标记可用/不可用）
- [ ] 10:30 基于可用语料生成发布内容

### 下午（人工+自动）
- [ ] 14:00 审核生成的发布内容
- [ ] 15:00 执行发布（到达计划时间自动发布）

### 晚间（自动）
- [ ] 20:00 抓取今日发布内容的实时数据
- [ ] 20:30 生成复盘报告

---

## 🔗 关键数据关联

```
crawl_tasks (任务)
    │
    ├──▶ crawl_results (结果1)
    │       │
    │       └──▶ publish_tasks.source_corpus_ids (被引用)
    │
    └──▶ crawl_results (结果2)
            │
            └──▶ publish_tasks.source_corpus_ids (被引用)

publish_tasks (发布任务)
    │
    ├──▶ target_accounts (发布到哪个账号)
    │
    └──▶ publish_metrics_daily (每日数据追踪)

target_accounts (账号)
    │
    └──▶ target_accounts_metrics_daily (每日数据追踪)
```

---

## 💡 关键查询（用于看板）

### 今日待办看板
```sql
-- 1. 待审核语料数
SELECT COUNT(*) FROM crawl_results WHERE curation_status = 'raw';

-- 2. 待审核发布任务数
SELECT COUNT(*) FROM publish_tasks WHERE status = 'pending_review';

-- 3. 今日待发布任务数
SELECT COUNT(*) FROM publish_tasks 
WHERE status = 'scheduled' 
AND DATE(scheduled_at) = DATE('now');

-- 4. 可用语料数（质量分>7）
SELECT COUNT(*) FROM crawl_results 
WHERE curation_status = 'approved' 
AND is_available = true 
AND quality_score >= 7;
```

### 今日表现看板
```sql
-- 1. 今日发布内容数
SELECT COUNT(*) FROM publish_tasks 
WHERE status = 'published' 
AND DATE(published_at) = DATE('now');

-- 2. 今日总互动数
SELECT SUM(reddit_score + reddit_comments) 
FROM publish_metrics_daily 
WHERE metric_date = DATE('now');

-- 3. 粉丝增长
SELECT SUM(followers_change) 
FROM target_accounts_metrics_daily 
WHERE metric_date = DATE('now');
```

---

这个流程是否更清晰了？每个步骤的触发条件、输入输出、数据库操作都明确了。