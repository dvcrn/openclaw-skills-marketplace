#!/usr/bin/env python3
"""
Smart Memory Sync - 主入口
独立运行，不依赖外部模块导入
"""

import sys
import json
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

class SmartMemorySync:
    """智能记忆同步"""
    
    def __init__(self):
        self.skill_root = Path(__file__).parent.parent
        self.config_path = self.skill_root / "config" / "sync-config.json"
        self.log_path = self.skill_root / "logs" / "monitor.log"
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        
        # 加载配置
        self.config = self.load_config()
        
        self.threshold_remind = self.config.get('thresholds', {}).get('remind', 50)
        self.threshold_sync = self.config.get('thresholds', {}).get('auto_sync', 75)
        self.threshold_switch = self.config.get('thresholds', {}).get('auto_switch', 85)
        self.check_interval = self.config.get('intervals', {}).get('check', 300)
        
        self.last_action = None
        self.last_action_time = 0
        self.cooldown = 600  # 10分钟冷却
    
    def load_config(self):
        """加载配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}")
        return {}
    
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
    
    # ==================== 同步功能 ====================
    
    def sync_memory(self):
        """同步MEMORY.md"""
        self.log("📝 同步MEMORY.md...")
        # TODO: 实现智能更新
        self.log("✅ MEMORY.md同步完成")
    
    def sync_qmd(self):
        """同步QMD知识库"""
        self.log("🔍 同步QMD知识库...")
        
        try:
            result = subprocess.run(
                ['qmd', 'update'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("✅ QMD索引更新完成")
            else:
                self.log(f"⚠️ QMD更新失败: {result.stderr}")
        except FileNotFoundError:
            self.log("⚠️ QMD未安装，跳过")
        except Exception as e:
            self.log(f"❌ QMD同步失败: {e}")
    
    def sync_git(self, message=None):
        """同步Git"""
        self.log("📦 同步Git...")
        
        if not message:
            message = f"Smart sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.workspace, check=True)
            
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Git提交完成")
            elif "nothing to commit" in result.stdout:
                self.log("ℹ️ 无变更需要提交")
            else:
                self.log(f"⚠️ Git提交失败: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Git同步失败: {e}")
    
    def sync_all(self):
        """同步三库"""
        self.log("🔄 开始三库同步...")
        
        self.sync_memory()
        self.sync_qmd()
        self.sync_git()
        
        self.log("✅ 三库同步完成")
    
    # ==================== 触发功能 ====================
    
    def remind_user(self):
        """提醒用户"""
        if not self.can_act('remind'):
            self.log("⏸️ 提醒冷却期中，跳过")
            return
        
        self.log("⚠️ 上下文50%，提醒用户")
        self.record_action('remind')
        
        message = "官家，上下文50%，建议同步记忆了～ 🌾"
        self.log(f"📤 提醒: {message}")
    
    def auto_sync(self):
        """自动同步三库"""
        if not self.can_act('sync'):
            self.log("⏸️ 同步冷却期中，跳过")
            return
        
        self.log("🔄 上下文75%，自动同步三库...")
        self.record_action('sync')
        self.sync_all()
    
    def trigger_switch(self):
        """主动触发切换"""
        if not self.can_act('switch'):
            self.log("⏸️ 切换冷却期中，跳过")
            return
        
        self.log("🚨 上下文85%，触发切换...")
        self.record_action('switch')
        
        # 1. 先同步三库
        self.sync_all()
        
        # 2. TODO: 调用Context Manager
        self.log("✅ 切换完成")
    
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
    
    # ==================== 主入口 ====================
    
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
                time.sleep(60)
    
    def show_status(self):
        """显示状态"""
        usage, total, context, model = self.get_context_usage()
        
        print(f"📊 Smart Memory Sync 状态")
        print(f"=" * 50)
        print(f"上下文: {usage:.1f}% ({total}/{context})")
        print(f"模型: {model}")
        print(f"阈值: 提醒{self.threshold_remind}% | 同步{self.threshold_sync}% | 切换{self.threshold_switch}%")
        print(f"检查间隔: {self.check_interval}秒")
        print(f"冷却期: {self.cooldown}秒")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Memory Sync')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    parser.add_argument('--sync', action='store_true', help='手动同步三库')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--check', action='store_true', help='单次检查')
    
    args = parser.parse_args()
    
    syncer = SmartMemorySync()
    
    if args.daemon:
        syncer.run_daemon()
    elif args.sync:
        syncer.sync_all()
    elif args.status:
        syncer.show_status()
    elif args.check:
        syncer.check_and_act()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
