/**
 * Skill Shield Hook
 * TUI 启动时自动执行安全扫描
 */

const { execSync } = require('child_process');
const path = require('path');
const os = require('os');

const SHIELD_DIR = path.join(os.homedir(), '.openclaw/workspace/skills/skill-shield');
const STARTUP_SCRIPT = path.join(SHIELD_DIR, 'scripts', 'tui-startup.py');

module.exports = {
  name: 'shield-scan',
  description: 'Skill Shield - TUI启动时自动扫描安全风险',
  
  // Hook 触发时机
  triggers: ['session-start'],
  
  // Hook 执行逻辑
  async onTrigger(context) {
    try {
      // 执行启动扫描脚本
      const result = execSync(`python3 "${STARTUP_SCRIPT}"`, {
        encoding: 'utf-8',
        timeout: 30000 // 30秒超时
      });
      
      // 将扫描结果添加到系统提示
      if (result && result.trim()) {
        context.systemPrompt += `\n\n[Skill Shield] ${result.trim()}`;
      }
      
      return { success: true };
    } catch (error) {
      console.error('[Skill Shield] 扫描失败:', error.message);
      return { success: false, error: error.message };
    }
  }
};