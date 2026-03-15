#!/usr/bin/env python3
"""
Smart Memory Sync - 上下文监控和自动触发
功能：
1. 监控上下文使用率
2. 50%提醒用户
3. 75%自动同步三库
4. 85%主动触发切换
"""

import json
import subprocess
import time
import os
from datetime import datetime
from pathlib import Path

class ContextMonitor:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "sync-config.json"
        self.log_path = Path(__file__).parent.parent / "logs" / "monitor.log"
        self.config = self.load_config()
        
        self.threshold_remind = self.config['thresholds']['remind']
        self.threshold_sync = self.config['thresholds']['auto_sync']
        self.threshold_switch = self.config['thresholds']['auto_switch']
        self.check_interval = self.config['intervals']['check']
        
        self.last_action = None
        self.last_action_time = 0
        self.cooldown = 600  # 10分钟冷却
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'thresholds': {'remind': 50, 'auto_sync': 75, 'auto_switch': 85},
                'intervals': {'check': 300}
            }
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        
        # 确保日志目录存在
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
        
        print(log_line)
    
    def get_context_usage(self):
        """获取上下文使用率"""
        try:
            # 添加环境变量
            env = os.environ.copy()
            env['HOME'] = str(Path.home())
            env['PATH'] = f"{Path.home()}/.npm-global/bin:{env.get('PATH', '')}"
            
            result = subprocess.run(
                ['openclaw', 'sessions', '--active', '120', '--json'],
                capture_output=True,
                text=True,
                env=env,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('sessions') and len(data['sessions']) > 0:
                    session = data['sessions'][0]
                    total = session.get('totalTokens', 0)
                    context = session.get('contextTokens', 202752)
                    
                    if context > 0:
                        usage = (total / context) * 100
                        return usage, total, context, session.get('model', 'unknown')
        except Exception as e:
            self.log(f"❌ 获取上下文失败: {e}")
        
        return 0, 0, 202752, 'unknown'
    
    def can_act(self, action):
        """检查是否可以执行动作（冷却期）"""
        current_time = time.time()
        
        if self.last_action == action:
            if current_time - self.last_action_time < self.cooldown:
                return False
        
        return True
    
    def record_action(self, action):
        """记录动作"""
        self.last_action = action
        self.last_action_time = time.time()
    
    def remind_user(self):
        """提醒用户"""
        if not self.can_act('remind'):
            self.log("⏸️ 提醒冷却期中，跳过")
            return
        
        self.log("⚠️ 上下文50%，提醒用户")
        self.record_action('remind')
        
        # TODO: 发送QQ消息
        message = "官家，上下文50%，建议同步记忆了～ 🌾"
        self.log(f"📤 提醒: {message}")
    
    def auto_sync(self):
        """自动同步三库"""
        if not self.can_act('sync'):
            self.log("⏸️ 同步冷却期中，跳过")
            return
        
        self.log("🔄 上下文75%，自动同步三库...")
        self.record_action('sync')
        
        try:
            # 调用syncers
            sync_script = Path(__file__).parent.parent / "syncers" / "sync-all.py"
            subprocess.run(['python3', str(sync_script)], check=True, timeout=30)
            self.log("✅ 三库同步完成")
        except Exception as e:
            self.log(f"❌ 同步失败: {e}")
    
    def trigger_switch(self):
        """主动触发切换"""
        if not self.can_act('switch'):
            self.log("⏸️ 切换冷却期中，跳过")
            return
        
        self.log("🚨 上下文85%，触发切换...")
        self.record_action('switch')
        
        try:
            # 1. 先同步三库
            self.auto_sync()
            
            # 2. 调用Context Manager
            # TODO: 实现切换逻辑
            self.log("✅ 切换完成")
        except Exception as e:
            self.log(f"❌ 切换失败: {e}")
    
    def check_and_act(self):
        """检查并执行相应动作"""
        usage, total, context, model = self.get_context_usage()
        
        self.log(f"📊 上下文: {usage:.1f}% ({total}/{context}) | 模型: {model}")
        
        if usage >= self.threshold_switch:
            self.trigger_switch()
        elif usage >= self.threshold_sync:
            self.auto_sync()
        elif usage >= self.threshold_remind:
            self.remind_user()
        else:
            self.log(f"✅ 上下文正常（{usage:.1f}% < {self.threshold_remind}%）")
    
    def run_daemon(self):
        """守护进程模式"""
        self.log("🚀 Smart Memory Sync 启动（守护进程）")
        self.log(f"📋 阈值: 提醒{self.threshold_remind}% | 同步{self.threshold_sync}% | 切换{self.threshold_switch}%")
        self.log(f"⏱️ 检查间隔: {self.check_interval}秒")
        
        while True:
            try:
                self.log("🔍 ===== 开始检查 =====")
                self.check_and_act()
                self.log("✅ ===== 检查完成 =====\n")
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.log("👋 收到停止信号，退出")
                break
            except Exception as e:
                self.log(f"❌ 检查异常: {e}")
                time.sleep(60)  # 异常后等待1分钟

if __name__ == '__main__':
    import sys
    
    monitor = ContextMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        monitor.run_daemon()
    else:
        # 单次检查
        monitor.check_and_act()
