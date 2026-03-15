#!/usr/bin/env node
/**
 * Cognitive Brain - 目标管理快捷接口
 * 用于在记忆编码时自动管理目标
 */

const goalManagement = require('./goal_management.cjs');

/**
 * 从记忆内容中提取并管理目标
 */
function extractAndUpdateGoals(content, metadata = {}) {
  // 加载目标
  goalManagement.load();
  
  // 检查是否包含目标相关关键词
  const goalKeywords = ['目标', '完成', '实现', '计划', '要做', '需要', '希望', '想'];
  const hasGoal = goalKeywords.some(kw => content.includes(kw));
  
  if (hasGoal) {
    // 尝试提取目标描述
    const sentences = content.split(/[。！？\n]/);
    
    sentences.forEach(sentence => {
      if (goalKeywords.some(kw => sentence.includes(kw))) {
        // 检查是否已存在相似目标
        const existingGoals = goalManagement.getActiveGoals();
        const isDuplicate = existingGoals.some(g => 
          g.description.includes(sentence) || sentence.includes(g.description)
        );
        
        if (!isDuplicate && sentence.length > 5) {
          // 创建新目标
          goalManagement.createGoal(sentence.slice(0, 100), {
            priority: metadata.importance > 0.8 ? 'high' : 'medium',
            category: 'extracted'
          });
          console.log(`🎯 创建新目标: ${sentence.slice(0, 50)}...`);
        }
      }
    });
  }
  
  // 检查是否有目标需要更新进度
  const completionKeywords = ['完成了', '实现了', '解决了', '做好了', '成功了'];
  const hasCompletion = completionKeywords.some(kw => content.includes(kw));
  
  if (hasCompletion) {
    const activeGoals = goalManagement.getActiveGoals();
    activeGoals.forEach(goal => {
      // 简单匹配：如果内容包含目标描述的一部分
      if (goal.description.split(/[，。]/).some(part => 
        part.length > 3 && content.includes(part)
      )) {
        goalManagement.updateProgress(goal.id, Math.min(100, goal.progress + 25));
        console.log(`✅ 目标进度更新: ${goal.description.slice(0, 30)}... -> ${goal.progress + 25}%`);
      }
    });
  }
  
  return goalManagement.getActiveGoals();
}

/**
 * 获取当前活跃目标摘要
 */
function getActiveGoalsSummary() {
  const goals = goalManagement.getActiveGoals();
  
  if (goals.length === 0) {
    return '当前没有活跃目标';
  }
  
  return goals.map((g, i) => 
    `${i + 1}. ${g.description.slice(0, 40)}... (${g.progress}%)`
  ).join('\n');
}

/**
 * 导出
 */
module.exports = { extractAndUpdateGoals, getActiveGoalsSummary };

// 命令行接口
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(getActiveGoalsSummary());
  } else {
    const goals = extractAndUpdateGoals(args.join(' '));
    console.log(JSON.stringify(goals, null, 2));
  }
}
