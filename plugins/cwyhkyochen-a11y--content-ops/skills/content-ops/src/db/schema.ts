import { sqliteTable, text, integer, real, blob } from 'drizzle-orm/sqlite-core';

/**
 * ============================================
 * Content Ops System - Database Schema
 * ============================================
 * 
 * 设计原则:
 * 1. 每个字段都有明确用途说明
 * 2. 使用外键建立表间关系
 * 3. JSON字段存储灵活配置
 * 4. 时间戳追踪数据变更
 * 
 * 表关系:
 * source_accounts (1) ──► (N) crawl_tasks (1) ──► (N) crawl_results
 * target_accounts (1) ──► (N) publish_tasks (1) ──► (1) publish_metrics_daily (N) ──► (汇总) target_accounts_metrics_daily
 */

// ============================================================================
// 表1: 被运营账号表 (target_accounts)
// ============================================================================
// 用途: 管理 Reddit/Pinterest/Discord 等发布目标账号
// 场景: 记录API密钥、账号定位、发布策略配置
// ============================================================================
export const targetAccounts = sqliteTable('target_accounts', {
  // --- 基础标识字段 ---
  
  /** 主键UUID - 全系统唯一标识 */
  id: text('id').primaryKey(),
  
  /** 账号类型 - 固定值 'target'，用于区分信息源账号 */
  accountType: text('account_type').notNull().$default(() => 'target'),
  
  /** 平台名称 - 如: reddit, pinterest, discord */
  platform: text('platform').notNull(),
  
  /** 账号名称 - 在平台上的用户名/显示名 */
  accountName: text('account_name').notNull(),
  
  /** 平台用户ID - 平台内部ID，API调用时使用 */
  accountId: text('account_id'),
  
  /** 主页链接 - 可直接访问的公开主页URL */
  homepageUrl: text('homepage_url'),
  
  // --- 状态管理字段 ---
  
  /** 账号状态 - active(活跃) | paused(暂停) | banned(被封) | deleted(已删) */
  status: text('status').notNull().$default(() => 'active'),
  
  // --- API配置字段 (加密存储) ---
  
  /** API配置JSON - 各平台认证信息，存储时加密 */
  // Reddit: { client_id, client_secret, refresh_token }
  // Pinterest: { access_token, refresh_token }
  // Discord: { bot_token, webhook_urls }
  apiConfig: text('api_config', { mode: 'json' }),
  
  // --- 运营策略字段 ---
  
  /** 账号定位 - 描述账号人设和核心价值主张 */
  positioning: text('positioning'),
  
  /** 目标受众 - 描述目标用户画像 */
  targetAudience: text('target_audience'),
  
  /** 内容方向 - 描述主要发布什么类型的内容 */
  contentDirection: text('content_direction'),
  
  /** 平台特定配置JSON - 各平台特有设置 */
  // Reddit: { default_subreddits: [...], posting_rules: {...} }
  // Pinterest: { default_boards: [...], content_categories: [...] }
  // Discord: { channel_mappings: {...} }
  platformConfig: text('platform_config', { mode: 'json' }),
  
  // --- 时间戳字段 ---
  
  /** 创建时间 - 账号档案首次创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 更新时间 - 档案最后修改时间 */
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});

// ============================================================================
// 表2: 信息源账号表 (source_accounts)
// ============================================================================
// 用途: 管理小红书等抓取源账号的登录态和配额
// 场景: 追踪登录状态、管理每日抓取限额、防止触发平台风控
// ============================================================================
export const sourceAccounts = sqliteTable('source_accounts', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 账号类型 - 固定值 'source' */
  accountType: text('account_type').notNull().$default(() => 'source'),
  
  /** 平台名称 - 如: xiaohongshu, douyin, instagram */
  platform: text('platform').notNull(),
  
  /** 账号标识名 - 自定义名称，用于区分多个同平台账号 */
  accountName: text('account_name').notNull(),
  
  // --- 登录状态字段 ---
  
  /** 登录状态 - 
   * active: 正常可用
   * expired: 登录过期，需要重新登录
   * needs_verification: 需要验证码/滑块验证
   * rate_limited: 触发限流，暂时不可用
   */
  loginStatus: text('login_status').notNull().$default(() => 'expired'),
  
  /** 会话数据JSON - 浏览器会话信息，加密存储
   * 包含: cookies, localStorage, sessionStorage 等
   */
  sessionData: text('session_data', { mode: 'json' }),
  
  // --- 配额管理字段 ---
  
  /** 每日抓取限额 - 防止触发平台风控，如: 100 */
  dailyQuota: integer('daily_quota').notNull().$default(() => 100),
  
  /** 今日已用配额 - 当天已抓取的笔记/内容数量 */
  quotaUsedToday: integer('quota_used_today').notNull().$default(() => 0),
  
  /** 配额重置时间 - 下次重置配额的时间戳 */
  quotaResetAt: integer('quota_reset_at', { mode: 'timestamp' }),
  
  // --- 抓取配置字段 ---
  
  /** 抓取配置JSON - 控制抓取行为
   * {
   *   search_limit: 50,           // 每次搜索最多抓取条数
   *   request_interval: [2, 5],   // 请求间隔随机范围(秒)
   *   retry_times: 3,             // 失败重试次数
   *   user_agent: "...",          // 浏览器User-Agent
   *   proxy_config: null          // 代理配置
   * }
   */
  crawlConfig: text('crawl_config', { mode: 'json' }),
  
  // --- 时间戳字段 ---
  
  /** 最后登录时间 - 上次成功登录的时间 */
  lastLoginAt: integer('last_login_at', { mode: 'timestamp' }),
  
  /** 最后抓取时间 - 上次执行抓取任务的时间 */
  lastCrawlAt: integer('last_crawl_at', { mode: 'timestamp' }),
  
  /** 创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 更新时间 */
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});

// ============================================================================
// 表3: 抓取任务表 (crawl_tasks)
// ============================================================================
// 用途: 管理内容抓取任务的创建、调度、执行状态
// 场景: 创建抓取任务后，系统按计划执行，人工可查看进度
// ============================================================================
export const crawlTasks = sqliteTable('crawl_tasks', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 任务名称/主题 - 描述性名称，如: "春季穿搭-第1批" */
  taskName: text('task_name').notNull(),
  
  /** 关联信息源账号ID - 使用哪个账号执行抓取 */
  sourceAccountId: text('source_account_id')
    .notNull()
    .references(() => sourceAccounts.id),
  
  // --- 状态管理字段 ---
  
  /** 任务状态 -
   * pending: 待执行
   * running: 执行中
   * completed: 已完成
   * failed: 失败
   * cancelled: 已取消
   */
  status: text('status').notNull().$default(() => 'pending'),
  
  // --- 搜索配置字段 ---
  
  /** 搜索关键词列表JSON - 要抓取的主题相关关键词
   * 如: ["春季穿搭", "OOTD", "每日穿搭"]
   */
  queryList: text('query_list', { mode: 'json' }).notNull(),
  
  // --- 执行进度字段 ---
  
  /** 目标抓取数量 - 计划抓取多少条内容 */
  targetCount: integer('target_count').notNull().$default(() => 50),
  
  /** 实际抓取数量 - 已抓取的内容条数 */
  crawledCount: integer('crawled_count').notNull().$default(() => 0),
  
  // --- 时间安排字段 ---
  
  /** 计划执行时间 - 定时任务的执行时间 */
  scheduledAt: integer('scheduled_at', { mode: 'timestamp' }),
  
  /** 实际开始时间 - 任务真正开始执行的时间 */
  startedAt: integer('started_at', { mode: 'timestamp' }),
  
  /** 完成时间 - 任务结束时间(成功/失败/取消) */
  completedAt: integer('completed_at', { mode: 'timestamp' }),
  
  // --- 任务配置字段 ---
  
  /** 任务配置JSON - 抓取过滤和提取规则
   * {
   *   filters: {
   *     min_likes: 100,        // 最少点赞数
   *     min_saves: 50,         // 最少收藏数
   *     date_range: "7d",      // 发布时间范围
   *     exclude_authors: []    // 排除的作者列表
   *   },
   *   extract_fields: [        // 需要提取的字段
   *     "title", "content", "images", "tags", 
   *     "likes", "saves", "author", "publish_time"
   *   ]
   * }
   */
  taskConfig: text('task_config', { mode: 'json' }),
  
  // --- 元信息字段 ---
  
  /** 创建人 - 谁创建了这个任务 */
  createdBy: text('created_by'),
  
  /** 创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 更新时间 */
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});

// ============================================================================
// 表4: 抓取结果表 (crawl_results)
// ============================================================================
// 用途: 存储抓取到的原始内容，包含完整数据和元信息
// 场景: 抓取后人工审核，确认可用后进入语料库
// ============================================================================
export const crawlResults = sqliteTable('crawl_results', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 关联抓取任务ID - 属于哪个抓取任务 */
  taskId: text('task_id')
    .notNull()
    .references(() => crawlTasks.id),
  
  /** 关联信息源账号ID - 用哪个账号抓取的 */
  sourceAccountId: text('source_account_id')
    .notNull()
    .references(() => sourceAccounts.id),
  
  /** 来源平台 - 如: xiaohongshu */
  platform: text('platform').notNull(),
  
  // --- 来源标识字段 ---
  
  /** 原始链接 - 可直接访问的内容URL */
  sourceUrl: text('source_url').notNull(),
  
  /** 平台内容ID - 平台内部的内容标识 */
  sourceId: text('source_id'),
  
  /** 原作者名称 */
  authorName: text('author_name'),
  
  /** 原作者ID - 平台用户ID */
  authorId: text('author_id'),
  
  // --- 内容字段 ---
  
  /** 标题 */
  title: text('title'),
  
  /** 正文内容 - 完整文字内容 */
  content: text('content'),
  
  /** 内容类型 - text(纯文字) | image(图片) | video(视频) | mixed(混合) */
  contentType: text('content_type'),
  
  /** 媒体URL列表JSON - 图片/视频的网络地址 */
  mediaUrls: text('media_urls', { mode: 'json' }),
  
  /** 本地存储路径JSON - 下载到本地的文件路径 */
  mediaLocalPaths: text('media_local_paths', { mode: 'json' }),
  
  /** 标签列表JSON - 原始标签，如: ["穿搭", "OOTD", "春季"] */
  tags: text('tags', { mode: 'json' }),
  
  /** 互动数据JSON - 原始平台的点赞/收藏等数据
   * { likes: 1000, saves: 500, comments: 100, shares: 50 }
   */
  engagement: text('engagement', { mode: 'json' }),
  
  /** 原始发布时间 - 内容在源平台的发布时间 */
  publishTime: integer('publish_time', { mode: 'timestamp' }),
  
  /** 抓取时间 - 被系统抓取的时间 */
  crawlTime: integer('crawl_time', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  // --- 审核管理字段 ---
  
  /** 审核状态 -
   * raw: 原始未审核
   * reviewing: 审核中
   * approved: 已通过(可用)
   * rejected: 已拒绝(不可用)
   * expired: 已过期(内容太旧)
   */
  curationStatus: text('curation_status').notNull().$default(() => 'raw'),
  
  /** 审核备注 - 人工审核时填写的备注 */
  curationNotes: text('curation_notes'),
  
  /** 审核人 - 谁审核的这条内容 */
  curatedBy: text('curated_by'),
  
  /** 审核时间 */
  curatedAt: integer('curated_at', { mode: 'timestamp' }),
  
  /** 质量评分 - 1-10分，用于筛选优质语料 */
  qualityScore: integer('quality_score'),
  
  /** 是否可用于二次创作 - 审核通过的标志 */
  isAvailable: integer('is_available', { mode: 'boolean' }).$default(() => false),
  
  // --- 使用追踪字段 ---
  
  /** 被使用次数 - 这条语料被用于多少次发布 */
  usageCount: integer('usage_count').notNull().$default(() => 0),
  
  /** 最后使用时间 */
  lastUsedAt: integer('last_used_at', { mode: 'timestamp' }),
});

// ============================================================================
// 表5: 发布任务表 (publish_tasks)
// ============================================================================
// 用途: 管理内容从草稿到发布的完整流程
// 场景: 基于语料生成内容 -> 人工审核 -> 定时/立即发布
// ============================================================================
export const publishTasks = sqliteTable('publish_tasks', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 任务名称 */
  taskName: text('task_name').notNull(),
  
  /** 关联被运营账号ID - 发布到哪个账号 */
  targetAccountId: text('target_account_id')
    .notNull()
    .references(() => targetAccounts.id),
  
  /** 使用的语料ID列表JSON - 基于哪些抓取结果生成
   * 如: ["uuid1", "uuid2"]
   */
  sourceCorpusIds: text('source_corpus_ids', { mode: 'json' }),
  
  // --- 状态管理字段 ---
  
  /** 任务状态 -
   * draft: 草稿
   * pending_review: 待审核
   * approved: 已批准
   * scheduled: 已排期
   * publishing: 发布中
   * published: 已发布
   * failed: 失败
   * cancelled: 已取消
   */
  status: text('status').notNull().$default(() => 'draft'),
  
  // --- 主题归属字段 ---
  
  /** 主要关键词/主题 - 内容的核心主题，如: "春季穿搭" */
  primaryTopic: text('primary_topic'),
  
  /** 主题标签列表JSON - 相关内容标签，如: ["穿搭", "春季", "OOTD"] */
  topicTags: text('topic_tags', { mode: 'json' }),
  
  /** 内容类型 -
   * original: 原创
   * translated: 翻译
   * adapted: 改编
   * mixed: 混合(多篇语料整合)
   */
  contentType: text('content_type'),
  
  // --- 内容字段 ---
  
  /** 发布内容JSON - 完整的发布数据
   * {
   *   title: "...",
   *   body: "...",
   *   media: ["path1", "path2"],
   *   tags: ["tag1", "tag2"],
   *   platform_specific: {
   *     reddit: { subreddit: "r/xxx", flair: "..." },
   *     pinterest: { board: "...", description: "..." }
   *   }
   * }
   */
  content: text('content', { mode: 'json' }),
  
  /** 内容改编记录JSON - 记录从语料到成品的修改
   * {
   *   source_platform: "xiaohongshu",
   *   adaptation_type: "translation",
   *   changes: [
   *     { field: "title", from: "...", to: "..." }
   *   ],
   *   cultural_notes: "...",
   *   translator: "agent"
   * }
   */
  adaptation: text('adaptation', { mode: 'json' }),
  
  // --- 时间安排字段 ---
  
  /** 计划发布时间 - 定时发布的执行时间 */
  scheduledAt: integer('scheduled_at', { mode: 'timestamp' }),
  
  /** 实际发布时间 */
  publishedAt: integer('published_at', { mode: 'timestamp' }),
  
  // --- 审核字段 ---
  
  /** 创建人 - 谁创建了这个发布任务 */
  createdBy: text('created_by'),
  
  /** 审核人 - 谁审核通过 */
  reviewedBy: text('reviewed_by'),
  
  /** 审核时间 */
  reviewedAt: integer('reviewed_at', { mode: 'timestamp' }),
  
  /** 审核意见 */
  reviewNotes: text('review_notes'),
  
  // --- 时间戳字段 ---
  
  /** 创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 更新时间 */
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});

// ============================================================================
// 表6: 发布内容每日数据表 (publish_metrics_daily)
// ============================================================================
// 用途: 追踪每篇已发布内容的每日数据表现
// 场景: 每日定时抓取各平台数据，分析内容表现趋势
// ============================================================================
export const publishMetricsDaily = sqliteTable('publish_metrics_daily', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 关联发布任务ID - 哪篇内容的数据 */
  publishTaskId: text('publish_task_id')
    .notNull()
    .references(() => publishTasks.id),
  
  /** 关联被运营账号ID */
  targetAccountId: text('target_account_id')
    .notNull()
    .references(() => targetAccounts.id),
  
  /** 数据日期 - 这条记录统计的是哪天的数据 */
  metricDate: text('metric_date').notNull(), // YYYY-MM-DD格式
  
  /** 平台名称 */
  platform: text('platform').notNull(),
  
  /** 帖子链接 - 可直接访问的URL */
  postUrl: text('post_url'),
  
  /** 平台帖子ID - API查询时使用 */
  platformPostId: text('platform_post_id'),
  
  // --- 通用互动字段 ---
  
  /** 曝光量/浏览量 - 内容被展示的次数 */
  impressions: integer('impressions'),
  
  /** 点击量 - 点击内容的次数 */
  clicks: integer('clicks'),
  
  /** 互动率 - 互动数/曝光量 */
  engagementRate: real('engagement_rate'),
  
  // --- Reddit 特有字段 ---
  
  /** 帖子得分 - upvotes - downvotes */
  redditScore: integer('reddit_score'),
  
  /** 赞成票 */
  redditUpvotes: integer('reddit_upvotes'),
  
  /** 反对票 */
  redditDownvotes: integer('reddit_downvotes'),
  
  /** 赞成比例 - 0.0-1.0 */
  redditUpvoteRatio: real('reddit_upvote_ratio'),
  
  /** 评论数 */
  redditComments: integer('reddit_comments'),
  
  /** 奖励数 */
  redditAwards: integer('reddit_awards'),
  
  // --- Pinterest 特有字段 ---
  
  /** 保存数(Pin次数) */
  pinterestSaves: integer('pinterest_saves'),
  
  /** 点击查看数 */
  pinterestCloseups: integer('pinterest_closeups'),
  
  /** Outbound点击(跳转到源站) */
  pinterestOutboundClicks: integer('pinterest_outbound_clicks'),
  
  // --- Discord 特有字段 ---
  
  /** 表情反应统计JSON - { "👍": 10, "❤️": 5 } */
  discordReactions: text('discord_reactions', { mode: 'json' }),
  
  /** 回复数 */
  discordReplies: integer('discord_replies'),
  
  // --- 数据质量字段 ---
  
  /** 数据是否完整抓取 - 有时API限制可能导致数据不全 */
  isComplete: integer('is_complete', { mode: 'boolean' }).$default(() => true),
  
  /** 抓取错误信息 - 如果抓取失败记录原因 */
  fetchError: text('fetch_error'),
  
  /** 数据抓取时间 */
  fetchedAt: integer('fetched_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 记录创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});

// ============================================================================
// 表7: 被运营账号每日数据表 (target_accounts_metrics_daily)
// ============================================================================
// 用途: 追踪被运营账号的整体每日数据表现
// 场景: 每日汇总账号粉丝、Karma等数据，计算增长率
// ============================================================================
export const targetAccountsMetricsDaily = sqliteTable('target_accounts_metrics_daily', {
  // --- 基础标识字段 ---
  
  /** 主键UUID */
  id: text('id').primaryKey(),
  
  /** 关联被运营账号ID */
  targetAccountId: text('target_account_id')
    .notNull()
    .references(() => targetAccounts.id),
  
  /** 平台名称 */
  platform: text('platform').notNull(),
  
  /** 数据日期 */
  metricDate: text('metric_date').notNull(), // YYYY-MM-DD格式
  
  // --- 通用账号数据字段 ---
  
  /** 粉丝数 */
  followers: integer('followers'),
  
  /** 粉丝变化 - 较昨日 */
  followersChange: integer('followers_change'),
  
  /** 总帖子数 */
  totalPosts: integer('total_posts'),
  
  /** 新增帖子数 */
  postsChange: integer('posts_change'),
  
  /** 总互动数 */
  totalEngagement: integer('total_engagement'),
  
  /** 互动变化 */
  engagementChange: integer('engagement_change'),
  
  // --- Reddit 特有字段 ---
  
  /** 总Karma */
  redditTotalKarma: integer('reddit_total_karma'),
  
  /** Karma变化 */
  redditKarmaChange: integer('reddit_karma_change'),
  
  /** 链接Karma */
  redditLinkKarma: integer('reddit_link_karma'),
  
  /** 评论Karma */
  redditCommentKarma: integer('reddit_comment_karma'),
  
  // --- Pinterest 特有字段 ---
  
  /** 月度浏览量 */
  pinterestMonthlyViews: integer('pinterest_monthly_views'),
  
  /** 总Pin数 */
  pinterestTotalPins: integer('pinterest_total_pins'),
  
  /** 画板数 */
  pinterestTotalBoards: integer('pinterest_total_boards'),
  
  // --- 内容表现汇总字段 ---
  
  /** 当日最佳表现帖子ID */
  topPostId: text('top_post_id'),
  
  /** 最佳帖子互动数 */
  topPostEngagement: integer('top_post_engagement'),
  
  /** 平均帖子互动 */
  avgPostEngagement: real('avg_post_engagement'),
  
  // --- 计算指标字段 ---
  
  /** 增长率 - 较昨日粉丝增长率 */
  growthRate: real('growth_rate'),
  
  /** 互动率 - 总互动/总曝光 */
  engagementRate: real('engagement_rate'),
  
  /** 发布一致性评分 - 0-100，衡量发布频率稳定性 */
  postingConsistency: real('posting_consistency'),
  
  // --- 数据质量字段 ---
  
  /** 数据是否完整 */
  isComplete: integer('is_complete', { mode: 'boolean' }).$default(() => true),
  
  /** 抓取错误 */
  fetchError: text('fetch_error'),
  
  /** 数据抓取时间 */
  fetchedAt: integer('fetched_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
  
  /** 记录创建时间 */
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$default(() => new Date()),
});
