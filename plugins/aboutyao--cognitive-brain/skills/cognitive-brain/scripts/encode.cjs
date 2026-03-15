#!/usr/bin/env node
/**
 * Cognitive Brain - 记忆编码脚本
 * 将信息编码存入记忆系统
 */

const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { execSync } = require('child_process');
const { resolveModule } = require('./module_resolver.cjs');

// Embedding 服务客户端
const { getEmbeddingService } = require('./embedding_service.cjs');
let embeddingService = null;

// 加载配置
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    params[key] = args[i + 1];
  }
  
  return params;
}

// 停用词表
const STOPWORDS = new Set([
  // 中文停用词
  '的', '是', '在', '了', '和', '与', '或', '有', '为', '以',
  '及', '等', '中', '到', '从', '对', '就', '也', '都', '而',
  '且', '但', '如', '被', '把', '让', '给', '向', '这', '那',
  '之', '所', '者', '于', '其', '将', '已', '不', '没', '很',
  '更', '最', '能', '会', '可', '要', '应', '该', '需', '还',
  '这', '那', '此', '它', '我', '你', '他', '她', '们', '自己',
  '什么', '怎么', '如何', '为什么', '哪', '哪里', '何时', '多少',
  '通过', '使用', '进行', '实现', '可以', '需要', '应该', '一个',
  '这个', '那个', '一些', '每个', '所有', '其他', '之后', '之前',
  // 英文停用词
  'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
  'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of',
  'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
  'this', 'that', 'these', 'those', 'it', 'its', 'and', 'or',
  'but', 'not', 'no', 'yes', 'all', 'each', 'every', 'any'
]);

// 关键概念模式
const CONCEPT_PATTERNS = {
  // 技术术语
  tech: /\b(Rust|Python|JavaScript|TypeScript|AI|API|SQL|Redis|PostgreSQL|React|Vue|Node|LLM|GPT|OpenAI|Claude|Embedding|Vector|MongoDB|Docker|K8s|Kubernetes|Hook|Brain|ClawHub|GitHub|Git|Linux|Ubuntu|Windows|MacOS)\b/gi,
  // 英文专有名词（3字母以上）
  properNoun: /\b[A-Z][a-zA-Z]{2,}\b/g,
  // 中文关键词（固定词表）
  chineseKeywords: /(用户|记忆|系统|模块|功能|项目|任务|计划|目标|问题|方案|设计|架构|数据|配置|文件|脚本|服务|概念|实体|情感|意图|决策|对话|预测|反思|联想|遗忘|学习|优化|改进|更新|版本|日志|错误|警告|通知|消息|请求|响应|结果|报告|分析|洞察|建议|偏好|兴趣|画像|模式|趋势|关系|网络|节点|权重|向量|嵌入|缓存|存储|数据库|查询|检索|编码|处理|参数|选项|设置|环境|依赖|包|库|框架|工具|平台|接口|文档|测试|验证|检查|监控|告警|性能|效率|质量|准确性|可靠性|稳定性|安全性|权限|认证|授权|用户名|密码|邮箱|地址|链接|网址|域名|主机|端口|路径|目录|文件夹|格式|编码|字符|字符串|布尔|数组|对象|列表|函数|方法|类|属性|字段|变量|常量|异常|内存|磁盘|网络|带宽|延迟|并发|异步|队列|索引|排序|搜索|过滤|创建|读取|写入|删除|事务|启动|停止|重启|初始化|安装|加载|保存|导出|导入|备份|恢复|升级|发布|部署|维护|重构|修复|清理|Hook|网关|代理|路由|控制器|服务|客户端|服务器|请求|响应|会话|认证|Token|密钥|签名|加密|解密)/g
};

// 实体提取（优化版）
function extractEntities(content) {
  const entities = [];
  const seen = new Set();
  
  // 1. 技术术语
  const techTerms = content.match(CONCEPT_PATTERNS.tech) || [];
  techTerms.forEach(term => {
    const normalized = term.toLowerCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      entities.push(term);
    }
  });
  
  // 2. 英文专有名词
  const properNouns = content.match(CONCEPT_PATTERNS.properNoun) || [];
  properNouns.forEach(noun => {
    const normalized = noun.toLowerCase();
    // 排除停用词和太短的词
    if (!STOPWORDS.has(normalized) && noun.length >= 3 && !seen.has(normalized)) {
      seen.add(normalized);
      entities.push(noun);
    }
  });
  
  // 3. 中文关键词 - 使用固定词表
  const chineseKeywordMatches = content.match(CONCEPT_PATTERNS.chineseKeywords) || [];
  chineseKeywordMatches.forEach(word => {
    const normalized = word.toLowerCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      entities.push(word);
    }
  });
  
  // 4. 如果提取太少，补充2字中文词（过滤停用词）
  if (entities.length < 10) {
    const simpleMatches = content.match(/[\u4e00-\u9fa5]{2}/g) || [];
    simpleMatches.forEach(word => {
      if (STOPWORDS.has(word[0]) || STOPWORDS.has(word[1])) return;
      const generic = ['可以', '需要', '应该', '进行', '实现', '使用', '通过', '一个', '这个', '那个', '一些', '每个', '所有', '其他', '之后', '之前', '已经', '正在', '如果', '因为', '所以', '但是', '而且', '或者', '以及', '不是', '没有', '什么', '怎么', '如何'];
      if (generic.includes(word)) return;
      
      const normalized = word.toLowerCase();
      if (!seen.has(normalized)) {
        seen.add(normalized);
        entities.push(word);
      }
    });
  }
  
  // 4. 从长句中提取关键短语（用空格/标点分割后的有意义片段）
  const segments = content.split(/[，。！？、；：""''（）【】\s]+/);
  segments.forEach(seg => {
    if (seg.length >= 2 && seg.length <= 6) {
      // 检查是否包含有意义的词
      const hasContent = !STOPWORDS.has(seg) && 
                         !seg.split('').every(c => STOPWORDS.has(c));
      if (hasContent && !seen.has(seg)) {
        seen.add(seg);
        entities.push(seg);
      }
    }
  });
  
  return entities.slice(0, 30); // 增加限制
}

// 情感分析（增强版）
function analyzeEmotion(content) {
  // 正面情感词
  const positive = ['开心', '高兴', '喜欢', '棒', '好', '成功', 'great', 'good', 'love', '谢谢', '感谢', '优秀', '完美', '赞', '厉害', '牛', '不错', '满意', '期待', '希望', '努力', '进步', '成长', '完成', '解决'];
  
  // 负面情感词
  const negative = ['难过', '伤心', '讨厌', '差', '失败', '错误', 'bad', 'sad', 'error', '不对', '错了', '问题', 'bug', '崩溃', '失望', '沮丧', '烦', '累', '压力', '担心', '焦虑', '困惑', '迷茫', '遗憾', '抱歉', '对不起'];
  
  // 紧急词
  const urgent = ['紧急', '马上', '立刻', 'urgent', 'asap', '赶紧', '快点', '重要', '关键', '必须', '一定', '立刻', '马上'];
  
  // 好奇词
  const curious = ['为什么', '怎么', '如何', '什么', '哪', '？', '?', '想知道', '好奇', '请问', '能否', '可以吗'];
  
  // 兴奋词
  const excited = ['太棒', '太好了', '终于', '成功', '实现', '完成', '搞定', '新功能', '突破', '发现'];
  
  let valence = 0;    // 正负情感 (-1 到 1)
  let arousal = 0;    // 激活度 (0 到 1)
  let curiosity = 0;  // 好奇度 (0 到 1)
  let excitement = 0; // 兴奋度 (0 到 1)
  
  // 计算各维度得分
  positive.forEach(w => { if (content.includes(w)) valence += 0.15; });
  negative.forEach(w => { if (content.includes(w)) valence -= 0.15; });
  urgent.forEach(w => { if (content.includes(w)) arousal += 0.2; });
  curious.forEach(w => { if (content.includes(w)) curiosity += 0.2; });
  excited.forEach(w => { if (content.includes(w)) excitement += 0.2; });
  
  // 归一化
  valence = Math.max(-1, Math.min(1, valence));
  arousal = Math.max(0, Math.min(1, arousal + Math.abs(valence) * 0.3));
  curiosity = Math.max(0, Math.min(1, curiosity));
  excitement = Math.max(0, Math.min(1, excitement));
  
  // 确定主导情感
  let dominantEmotion = 'neutral';
  const emotionScores = {
    positive: Math.max(0, valence),
    negative: Math.max(0, -valence),
    urgent: arousal,
    curious: curiosity,
    excited: excitement
  };
  
  const maxEmotion = Object.entries(emotionScores).reduce((a, b) => a[1] > b[1] ? a : b);
  if (maxEmotion[1] > 0.2) {
    dominantEmotion = maxEmotion[0];
  }
  
  return {
    valence,
    arousal,
    curiosity,
    excitement,
    dominantEmotion,
    scores: emotionScores
  };
}

// 计算重要性
function calculateImportance(params) {
  const novelty = params.novelty ?? 0.5;
  const emotion = params.emotion?.valence ?? 0;
  const relevance = params.relevance ?? 0.5;
  const frequency = params.frequency ?? 0;
  
  const importance = 
    novelty * 0.3 + 
    Math.abs(emotion) * 0.3 + 
    relevance * 0.25 + 
    (1 - frequency) * 0.15;
  
  return Math.max(0, Math.min(1, importance));
}

// 选择存储层级
function selectLayer(importance) {
  if (importance >= 0.8) return ['semantic', 'episodic'];
  if (importance >= 0.5) return ['episodic'];
  if (importance >= 0.3) return ['working'];
  return ['sensory'];
}

// 主编码函数
async function encode(content, metadata = {}) {
  const id = uuidv4();
  const now = new Date().toISOString();
  
  // 1. 信息提取
  const entities = metadata.entities || extractEntities(content);
  const emotion = metadata.emotion || analyzeEmotion(content);
  const tags = metadata.tags || [];
  
  // 2. 计算重要性
  const importance = metadata.importance || calculateImportance({
    novelty: metadata.novelty,
    emotion: emotion,
    relevance: metadata.relevance,
    frequency: metadata.frequency
  });
  
  // 3. 选择存储层级
  const layers = selectLayer(importance);
  
  // 4. 生成摘要
  const summary = metadata.summary || content.slice(0, 100);
  
  // 构建记忆对象
  const memory = {
    id,
    timestamp: now,
    type: metadata.type || 'observation',
    summary,
    content,
    entities,
    emotion,
    tags,
    importance,
    layers,
    created_at: now
  };
  
  // 5. 存储到数据库
  try {
    const pg = resolveModule('pg');
    const { Pool } = pg;
    const pool = new Pool(config.storage.primary);
    
    if (layers.includes('episodic')) {
      // 生成 embedding（非阻塞）
      let embedding = null;
      try {
        // 延迟初始化服务
        if (!embeddingService) {
          embeddingService = getEmbeddingService();
        }
        // 非阻塞调用 - 服务未就绪时返回 null
        embedding = await embeddingService.embed(content, false);
        if (embedding) {
          console.log('✅ Embedding 生成成功');
        } else {
          console.log('⏳ Embedding 服务启动中，本次跳过...');
        }
      } catch (e) {
        console.log('⚠️ Embedding 生成失败，继续存储...');
      }
      
      // 插入记忆（包含 embedding）
      if (embedding) {
        await pool.query(`
          INSERT INTO episodes (id, type, summary, content, entities, emotions, tags, importance, embedding)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::vector)
        `, [
          id,
          memory.type,
          memory.summary,
          memory.content,
          JSON.stringify(memory.entities),
          JSON.stringify(memory.emotion),
          JSON.stringify(memory.tags),
          memory.importance,
          JSON.stringify(embedding)
        ]);
      } else {
        await pool.query(`
          INSERT INTO episodes (id, type, summary, content, entities, emotions, tags, importance)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        `, [
          id,
          memory.type,
          memory.summary,
          memory.content,
          JSON.stringify(memory.entities),
          JSON.stringify(memory.emotion),
          JSON.stringify(memory.tags),
          memory.importance
        ]);
      }
      
      // 建立联想
      for (const entity of entities) {
        // 确保概念存在
        await pool.query(`
          INSERT INTO concepts (name, type, importance)
          VALUES ($1, 'entity', $2)
          ON CONFLICT (name) DO UPDATE SET
            importance = GREATEST(concepts.importance, $2),
            last_accessed = NOW()
        `, [entity, memory.importance]);
      }
    }
    
    await pool.end();
  } catch (e) {
    // 如果数据库不可用，输出到文件
    const memoryFile = path.join(__dirname, '..', 'data', 'memories.jsonl');
    const dataDir = path.dirname(memoryFile);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    fs.appendFileSync(memoryFile, JSON.stringify(memory) + '\n');
  }
  
  // 更新用户建模
  try {
    const userModelPath = path.join(__dirname, '..', '.user-model.json');
    if (fs.existsSync(userModelPath)) {
      const userModel = JSON.parse(fs.readFileSync(userModelPath, 'utf8'));
      
      // 记录交互
      userModel.stats = userModel.stats || {};
      userModel.stats.totalInteractions = (userModel.stats.totalInteractions || 0) + 1;
      userModel.stats.lastInteraction = Date.now();
      
      // 记录话题
      if (memory.tags && memory.tags.length > 0) {
        userModel.preferences = userModel.preferences || { topics: {} };
        userModel.preferences.topics = userModel.preferences.topics || {};
        memory.tags.forEach(tag => {
          userModel.preferences.topics[tag] = Math.min(1, (userModel.preferences.topics[tag] || 0) + 0.1);
        });
      }
      
      // 记录情感模式
      if (memory.emotion && memory.emotion.dominantEmotion) {
        userModel.emotionPatterns = userModel.emotionPatterns || { history: [], dominantEmotions: {} };
        userModel.emotionPatterns.history.push({
          timestamp: Date.now(),
          emotion: memory.emotion.dominantEmotion,
          context: memory.summary
        });
        userModel.emotionPatterns.history = userModel.emotionPatterns.history.slice(-50);
        userModel.emotionPatterns.dominantEmotions[memory.emotion.dominantEmotion] = 
          (userModel.emotionPatterns.dominantEmotions[memory.emotion.dominantEmotion] || 0) + 1;
      }
      
      // 记录实体为已知概念
      if (memory.entities && memory.entities.length > 0) {
        userModel.knowledge = userModel.knowledge || { knownConcepts: [] };
        memory.entities.forEach(entity => {
          if (!userModel.knowledge.knownConcepts.includes(entity)) {
            userModel.knowledge.knownConcepts.push(entity);
          }
        });
        userModel.knowledge.knownConcepts = userModel.knowledge.knownConcepts.slice(-100);
      }
      
      fs.writeFileSync(userModelPath, JSON.stringify(userModel, null, 2));
    }
  } catch (e) {
    // 用户建模更新失败不影响主流程
  }
  
  // 更新工作记忆
  try {
    const workingMemoryPath = path.join(__dirname, '..', '.working-memory.json');
    let workingMemory = { activeContext: { entities: [], topic: null }, attention: {} };
    
    if (fs.existsSync(workingMemoryPath)) {
      workingMemory = JSON.parse(fs.readFileSync(workingMemoryPath, 'utf8'));
    }
    
    // 更新活跃实体
    if (memory.entities && memory.entities.length > 0) {
      workingMemory.activeContext = workingMemory.activeContext || { entities: [] };
      workingMemory.activeContext.entities = workingMemory.activeContext.entities || [];
      
      memory.entities.forEach(entity => {
        // 过滤太短或无意义的实体
        if (entity.length >= 2 && !entity.includes('的') && !entity.startsWith('部分')) {
          if (!workingMemory.activeContext.entities.includes(entity)) {
            workingMemory.activeContext.entities.unshift(entity);
          }
        }
      });
      
      // 保留最近20个实体
      workingMemory.activeContext.entities = workingMemory.activeContext.entities.slice(0, 20);
    }
    
    // 更新活跃话题
    if (memory.tags && memory.tags.length > 0) {
      workingMemory.activeContext.topic = memory.tags[0];
    }
    
    workingMemory.lastUpdate = Date.now();
    fs.writeFileSync(workingMemoryPath, JSON.stringify(workingMemory, null, 2));
  } catch (e) {
    // 工作记忆更新失败不影响主流程
  }
  
  // 提取并更新目标
  try {
    const goalHelperPath = path.join(__dirname, 'goal_helper.cjs');
    if (fs.existsSync(goalHelperPath)) {
      const goalHelper = require(goalHelperPath);
      goalHelper.extractAndUpdateGoals(memory.content, memory);
    }
  } catch (e) {
    // 目标提取失败不影响主流程
  }
  
  return memory;
}

// 主函数
async function main() {
  const params = parseArgs();
  
  if (!params.content) {
    console.log('用法: node encode.cjs --content "内容" [--metadata \'{"type":"fact"}\']');
    console.log('\n示例:');
    console.log('  node encode.cjs --content "用户的项目叫Alpha" --metadata \'{"importance":0.8}\'');
    process.exit(1);
  }
  
  const metadata = params.metadata ? JSON.parse(params.metadata) : {};
  
  console.log('🧠 编码记忆...\n');
  
  const result = await encode(params.content, metadata);
  
  console.log('✅ 编码完成:');
  console.log(`   ID: ${result.id}`);
  console.log(`   类型: ${result.type}`);
  console.log(`   重要性: ${result.importance.toFixed(2)}`);
  console.log(`   层级: ${result.layers.join(', ')}`);
  console.log(`   实体: ${result.entities.slice(0, 5).join(', ')}${result.entities.length > 5 ? '...' : ''}`);
  console.log(`   情感: valence=${result.emotion.valence.toFixed(2)}, arousal=${result.emotion.arousal.toFixed(2)}`);
}

main();
