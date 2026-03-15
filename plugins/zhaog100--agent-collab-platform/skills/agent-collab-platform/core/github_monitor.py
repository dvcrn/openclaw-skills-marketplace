#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub监听器 - 所有智能体共享

功能：
- 监听GitHub Issue评论
- 识别新评论
- 避免重复处理
"""

import json
import subprocess
import time
import threading
from datetime import datetime

class GitHubMonitor:
    """GitHub监听器"""
    
    def __init__(self, repo='zhaog100/openclaw-skills'):
        """初始化监听器"""
        self.repo = repo
        self.check_interval = 30  # 30秒检查一次
        self.processed_comments = set()
        self.running = False
        self.callback = None
    
    def start(self, callback):
        """启动监听"""
        if self.running:
            print("⚠️ 监听已在运行")
            return
        
        self.callback = callback
        self.running = True
        
        # 启动监听线程
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        print(f"✅ GitHub监听已启动")
        print(f"   仓库: {self.repo}")
        print(f"   检查间隔: {self.check_interval}秒")
    
    def stop(self):
        """停止监听"""
        self.running = False
        print("⏹️ GitHub监听已停止")
    
    def _monitor_loop(self):
        """监听循环"""
        while self.running:
            try:
                self._check_issues()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ 监听异常: {e}")
                time.sleep(5)
    
    def _check_issues(self):
        """检查Issue评论"""
        # 1. 获取最近更新的Issue
        cmd = [
            'gh', 'issue', 'list',
            '--repo', self.repo,
            '--state', 'open',
            '--limit', '10',
            '--json', 'number,title,updatedAt'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return
        
        issues = json.loads(result.stdout)
        
        # 2. 检查每个Issue的最新评论
        for issue in issues:
            issue_number = issue['number']
            self._check_issue_comments(issue_number)
    
    def _check_issue_comments(self, issue_number):
        """检查指定Issue的评论"""
        # 获取Issue评论
        cmd = [
            'gh', 'issue', 'view', str(issue_number),
            '--repo', self.repo,
            '--json', 'comments'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return
        
        issue_data = json.loads(result.stdout)
        comments = issue_data.get('comments', [])
        
        if not comments:
            return
        
        # 检查最新评论
        latest_comment = comments[-1]
        comment_id = latest_comment['id']
        
        # 跳过已处理的评论
        if comment_id in self.processed_comments:
            return
        
        # 标记为已处理
        self.processed_comments.add(comment_id)
        
        # 构造消息
        message = {
            'issue_number': issue_number,
            'comment_id': comment_id,
            'author': latest_comment['author']['login'],
            'body': latest_comment['body'],
            'created_at': latest_comment['createdAt']
        }
        
        # 回调处理
        if self.callback:
            self.callback(message)
    
    def get_status(self):
        """获取监听状态"""
        return {
            'running': self.running,
            'repo': self.repo,
            'check_interval': self.check_interval,
            'processed_count': len(self.processed_comments)
        }
