#!/usr/bin/env python3
"""
Feishu Task API Client
飞书任务管理 API 客户端

API 文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/overview
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, List, Any


class FeishuTaskClient:
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_id = app_id or os.environ.get('FEISHU_APP_ID')
        self.app_secret = app_secret or os.environ.get('FEISHU_APP_SECRET')
        self.access_token = None
        self.base_url = 'https://open.feishu.cn/open-apis'
        
    def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        url = f'{self.base_url}/auth/v3/tenant_access_token/internal'
        data = json.dumps({
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') != 0:
                raise Exception(f"Failed to get access token: {result.get('msg')}")
            self.access_token = result['tenant_access_token']
            return self.access_token
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """发送 HTTP 请求"""
        if not self.access_token:
            self.get_access_token()
            
        url = f'{self.base_url}{endpoint}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP Error {e.code}: {error_body}")
    
    def create_task(self, summary: str, **kwargs) -> Dict:
        """
        创建任务
        
        Args:
            summary: 任务标题（必填）
            description: 任务描述
            due_time: 截止时间（ISO 8601格式，如：2024-03-10T18:00:00+08:00）
            assignee_id: 执行者用户ID
            follower_ids: 关注者用户ID列表
            priority: 优先级（0=默认，1=低，2=中，3=高）
            creator_id: 创建者用户ID（如不传，则为自己创建）
            
        Returns:
            创建的任务信息
        """
        endpoint = '/task/v2/tasks'
        
        data = {'summary': summary}
        
        # 处理成员信息（可选，不传也能创建任务）
        # 注意：飞书任务API如果不传members，默认创建者为当前应用/用户
        # 如果传members，则每个member必须有id和type字段
        members = []
        
        # 如果有执行者ID，添加为执行者
        if 'assignee_id' in kwargs and kwargs['assignee_id']:
            members.append({'id': kwargs['assignee_id'], 'type': 'user', 'role': 'assignee'})
        
        # 添加关注者
        if 'follower_ids' in kwargs and kwargs['follower_ids']:
            for fid in kwargs['follower_ids']:
                members.append({'id': fid, 'type': 'user', 'role': 'follower'})
        
        # 只有当有成员时才添加 members 字段
        if members:
            data['members'] = members
        
        # 其他可选参数
        if 'description' in kwargs:
            data['description'] = kwargs['description']
        if 'due_time' in kwargs:
            # 支持 ISO 8601 格式或时间戳
            due_val = kwargs['due_time']
            if isinstance(due_val, str):
                # ISO 8601 格式，转换为时间戳（毫秒）
                import datetime
                # 解析 ISO 8601
                if '+' in due_val:
                    due_val = due_val.replace('+08:00', '')
                dt = datetime.datetime.fromisoformat(due_val)
                timestamp = int(dt.timestamp() * 1000)  # 转换为毫秒
            else:
                timestamp = int(due_val)
            data['due'] = {'timestamp': str(timestamp), 'timezone': 'Asia/Shanghai'}
        if 'priority' in kwargs:
            data['priority'] = kwargs['priority']
            
        return self._make_request('POST', endpoint, data)
    
    def get_task(self, task_id: str) -> Dict:
        """获取任务详情"""
        endpoint = f'/task/v2/tasks/{task_id}'
        return self._make_request('GET', endpoint)
    
    def update_task(self, task_id: str, **kwargs) -> Dict:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            summary: 任务标题
            description: 任务描述
            due_time: 截止时间 (ISO 8601 或时间戳)
            priority: 优先级
            completed: 是否完成
        """
        endpoint = f'/task/v2/tasks/{task_id}'
        
        task_data = {}
        update_fields = []
        
        if 'summary' in kwargs:
            task_data['summary'] = kwargs['summary']
            update_fields.append('summary')
        if 'description' in kwargs:
            task_data['description'] = kwargs['description']
            update_fields.append('description')
        if 'due_time' in kwargs:
            # 转换 due_time 格式（毫秒时间戳）
            due_val = kwargs['due_time']
            if isinstance(due_val, str):
                import datetime
                if '+' in due_val:
                    due_val = due_val.replace('+08:00', '')
                dt = datetime.datetime.fromisoformat(due_val)
                timestamp = int(dt.timestamp() * 1000)  # 转换为毫秒
            else:
                timestamp = int(due_val)
            task_data['due'] = {'timestamp': str(timestamp), 'timezone': 'Asia/Shanghai'}
            update_fields.append('due')
        if 'priority' in kwargs:
            task_data['priority'] = kwargs['priority']
            update_fields.append('priority')
        if 'completed' in kwargs:
            task_data['completed'] = kwargs['completed']
            update_fields.append('completed')
        
        data = {'task': task_data, 'update_fields': update_fields}
        return self._make_request('PATCH', endpoint, data)
    
    def delete_task(self, task_id: str) -> Dict:
        """删除任务"""
        endpoint = f'/task/v2/tasks/{task_id}'
        return self._make_request('DELETE', endpoint)
    
    def list_tasks(self, user_id: Optional[str] = None, completed: Optional[bool] = None) -> Dict:
        """
        获取任务列表
        
        Args:
            user_id: 指定用户的任务（不传则获取当前用户）
            completed: 筛选完成状态
        """
        endpoint = '/task/v2/tasks'
        params = []
        if user_id:
            params.append(f'user_id={user_id}')
        if completed is not None:
            params.append(f'completed={"true" if completed else "false"}')
            
        if params:
            endpoint += '?' + '&'.join(params)
            
        return self._make_request('GET', endpoint)


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Feishu Task CLI')
    parser.add_argument('--app-id', help='Feishu App ID')
    parser.add_argument('--app-secret', help='Feishu App Secret')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create task
    create_parser = subparsers.add_parser('create', help='Create a task')
    create_parser.add_argument('summary', help='Task title')
    create_parser.add_argument('--description', help='Task description')
    create_parser.add_argument('--due', help='Due time (ISO 8601)')
    create_parser.add_argument('--assignee', help='Assignee user ID')
    create_parser.add_argument('--priority', type=int, choices=[0,1,2,3], help='Priority (0=default,1=low,2=medium,3=high)')
    
    # Get task
    get_parser = subparsers.add_parser('get', help='Get task details')
    get_parser.add_argument('task_id', help='Task ID')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--user', help='User ID')
    list_parser.add_argument('--completed', type=bool, help='Filter by completion status')
    
    # Update task
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('--summary', help='New title')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--due', help='New due time')
    update_parser.add_argument('--priority', type=int, choices=[0,1,2,3])
    update_parser.add_argument('--completed', type=bool, help='Mark as completed')
    
    # Delete task
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', help='Task ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    client = FeishuTaskClient(app_id=args.app_id, app_secret=args.app_secret)
    
    try:
        if args.command == 'create':
            result = client.create_task(
                summary=args.summary,
                description=args.description,
                due_time=args.due,
                assignee_id=args.assignee,
                priority=args.priority
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.command == 'get':
            result = client.get_task(args.task_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.command == 'list':
            result = client.list_tasks(user_id=args.user, completed=args.completed)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.command == 'update':
            kwargs = {}
            if args.summary: kwargs['summary'] = args.summary
            if args.description: kwargs['description'] = args.description
            if args.due: kwargs['due_time'] = args.due
            if args.priority is not None: kwargs['priority'] = args.priority
            if args.completed is not None: kwargs['completed'] = args.completed
            result = client.update_task(args.task_id, **kwargs)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.command == 'delete':
            result = client.delete_task(args.task_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
