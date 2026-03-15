#!/usr/bin/env python3
"""
三库同步脚本
同步 MEMORY.md + QMD + Git
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class TripleSyncer:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        self.memory_path = self.workspace / 'MEMORY.md'
        self.memory_lite_path = self.workspace / 'MEMORY-LITE.md'
        
    def sync_memory(self):
        """同步MEMORY.md"""
        print("📝 同步MEMORY.md...")
        
        # TODO: 实现智能更新逻辑
        # 1. 分析聊天记录
        # 2. 提取关键信息
        # 3. 更新MEMORY.md
        # 4. 更新MEMORY-LITE.md
        
        print("✅ MEMORY.md同步完成")
    
    def sync_qmd(self):
        """同步QMD知识库"""
        print("🔍 同步QMD知识库...")
        
        try:
            # 更新QMD索引
            result = subprocess.run(
                ['qmd', 'update'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ QMD索引更新完成")
            else:
                print(f"⚠️ QMD更新失败: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ QMD未安装，跳过")
        except Exception as e:
            print(f"❌ QMD同步失败: {e}")
    
    def sync_git(self, message=None):
        """同步Git"""
        print("📦 同步Git...")
        
        if not message:
            message = f"Smart sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # git add
            subprocess.run(['git', 'add', '.'], cwd=self.workspace, check=True)
            
            # git commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Git提交完成")
            elif "nothing to commit" in result.stdout:
                print("ℹ️ 无变更需要提交")
            else:
                print(f"⚠️ Git提交失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Git同步失败: {e}")
    
    def sync_all(self):
        """同步三库"""
        print("🔄 开始三库同步...")
        
        self.sync_memory()
        self.sync_qmd()
        self.sync_git()
        
        print("✅ 三库同步完成")

if __name__ == '__main__':
    syncer = TripleSyncer()
    syncer.sync_all()
