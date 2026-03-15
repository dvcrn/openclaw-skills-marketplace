#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue处理器 - 所有智能体共享

功能：
- 创建Issue
- 获取Issue
- 发送评论
- 获取评论
"""

import json
import subprocess

class IssueHandler:
    """Issue处理器"""
    
    def __init__(self, repo='zhaog100/openclaw-skills'):
        """初始化处理器"""
        self.repo = repo
    
    def create_issue(self, title, body, labels=None):
        """创建Issue
        
        Args:
            title: Issue标题
            body: Issue内容
            labels: 标签列表
            
        Returns:
            (success, issue_number或error_message)
        """
        cmd = [
            'gh', 'issue', 'create',
            '--repo', self.repo,
            '--title', title,
            '--body', body
        ]
        
        if labels:
            cmd.extend(['--label', ','.join(labels)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 提取Issue编号
            issue_url = result.stdout.strip()
            issue_number = issue_url.split('/')[-1]
            return True, int(issue_number)
        else:
            return False, result.stderr
    
    def get_issue(self, issue_number):
        """获取Issue
        
        Args:
            issue_number: Issue编号
            
        Returns:
            (success, issue_data或error_message)
        """
        cmd = [
            'gh', 'issue', 'view', str(issue_number),
            '--repo', self.repo,
            '--json', 'number,title,body,state,createdAt,updatedAt,labels'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            return True, issue_data
        else:
            return False, result.stderr
    
    def send_comment(self, issue_number, body):
        """发送评论
        
        Args:
            issue_number: Issue编号
            body: 评论内容
            
        Returns:
            (success, comment_url或error_message)
        """
        cmd = [
            'gh', 'issue', 'comment', str(issue_number),
            '--repo', self.repo,
            '--body', body
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            comment_url = result.stdout.strip()
            return True, comment_url
        else:
            return False, result.stderr
    
    def get_comments(self, issue_number):
        """获取Issue评论
        
        Args:
            issue_number: Issue编号
            
        Returns:
            (success, comments或error_message)
        """
        cmd = [
            'gh', 'issue', 'view', str(issue_number),
            '--repo', self.repo,
            '--json', 'comments'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            comments = issue_data.get('comments', [])
            return True, comments
        else:
            return False, result.stderr
    
    def close_issue(self, issue_number, comment=None):
        """关闭Issue
        
        Args:
            issue_number: Issue编号
            comment: 关闭评论（可选）
            
        Returns:
            (success, message)
        """
        # 先发送评论（如果有）
        if comment:
            self.send_comment(issue_number, comment)
        
        # 关闭Issue
        cmd = [
            'gh', 'issue', 'close', str(issue_number),
            '--repo', self.repo
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"Issue #{issue_number} 已关闭"
        else:
            return False, result.stderr
