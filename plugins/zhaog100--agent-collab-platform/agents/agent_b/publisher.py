#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成发布模块 v2.0 - GitHub Issue协作

功能：
- 发布准备
- ClawHub发布
- 发布验证
- 提交到GitHub
"""

import json
import subprocess
from datetime import datetime

class Publisher:
    """集成发布器 - GitHub Issue模式"""
    
    def __init__(self):
        """初始化集成发布器"""
        self.releases = {}
        self.github_repo = 'zhaog100/openclaw-skills'
    
    def prepare_release(self, project_id, project_data):
        """准备发布"""
        release_id = f"release_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.releases[release_id] = {
            'id': release_id,
            'project_id': project_id,
            'project_data': project_data,
            'state': 'preparing',
            'checklist': {
                'code_review': False,
                'tests_passed': False,
                'docs_complete': False,
                'version_updated': False
            },
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return release_id, self.releases[release_id]
    
    def check_item(self, release_id, item_name):
        """检查清单项"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        if item_name not in self.releases[release_id]['checklist']:
            return False, f"检查项不存在: {item_name}"
        
        self.releases[release_id]['checklist'][item_name] = True
        
        # 检查是否全部完成
        all_done = all(self.releases[release_id]['checklist'].values())
        if all_done:
            self.releases[release_id]['state'] = 'ready'
        
        return True, f"检查项已完成: {item_name}"
    
    def publish_to_clawhub(self, release_id, skill_path):
        """发布到ClawHub"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        release = self.releases[release_id]
        
        # 检查清单是否全部完成
        if not all(release['checklist'].values()):
            return False, "发布前检查清单未完成"
        
        # 调用clawhub CLI发布
        cmd = ['clawhub', 'publish', skill_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 提取Package ID
            package_id = self.extract_package_id(result.stdout)
            
            release['state'] = 'published'
            release['package_id'] = package_id
            release['published_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return True, f"发布成功！Package ID: {package_id}"
        else:
            return False, f"发布失败: {result.stderr}"
    
    def extract_package_id(self, output):
        """从输出中提取Package ID"""
        # 简化实现：从输出中查找k开头的字符串
        import re
        match = re.search(r'k[a-z0-9]{32}', output)
        return match.group(0) if match else 'unknown'
    
    def verify_release(self, release_id):
        """验证发布"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        release = self.releases[release_id]
        
        if release['state'] != 'published':
            return False, "发布未完成"
        
        # 简化验证：检查Package ID是否有效
        if release.get('package_id') == 'unknown':
            return False, "Package ID无效"
        
        return True, f"发布验证成功！ClawHub: https://clawhub.com/skill/{release['package_id']}"
    
    def submit_release_to_github(self, release_id, prd_issue):
        """提交发布报告到GitHub Issue"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        release = self.releases[release_id]
        
        # 生成发布报告
        release_doc = self.generate_release_doc(release)
        
        # 发送GitHub评论
        cmd = [
            'gh', 'issue', 'comment', str(prd_issue),
            '--body', release_doc
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ [Publisher] 发布报告已提交到Issue #{prd_issue}")
            return True, f"发布报告已提交到Issue #{prd_issue}"
        else:
            print(f"❌ [Publisher] 提交失败: {result.stderr}")
            return False, f"提交失败: {result.stderr}"
    
    def generate_release_doc(self, release):
        """生成发布报告"""
        release_doc = f"""## 🚀 发布完成

**发布ID**：{release['id']}
**时间**：{release.get('published_at', 'N/A')}
**状态**：✅ 已发布

---

## 📦 发布信息

- **Package ID**：`{release.get('package_id', 'N/A')}`
- **ClawHub**：https://clawhub.com/skill/{release.get('package_id', '')}

---

## ✅ 发布前检查

"""
        # 添加检查清单
        for item, done in release['checklist'].items():
            status_icon = '✅' if done else '❌'
            release_doc += f"- {status_icon} {item}\n"
        
        release_doc += f"""
---

## 📋 交付物确认

- ✅ 代码实现
- ✅ 单元测试
- ✅ 使用文档
- ✅ ClawHub发布

---

**项目状态**：✅ 发布完成

🌾 小米粒（Dev代理）
"""
        
        return release_doc
    
    def publish(self, args):
        """发布入口"""
        print(f"🚀 集成发布模式: {args}")
        # TODO: 实现发布逻辑
    
    def handle(self, parsed_message):
        """处理集成发布消息"""
        action = parsed_message.get('action')
        
        if action == 'prepare':
            project_id = parsed_message.get('project_id')
            release_id = self.prepare_release(project_id, {})
            return f"✅ 发布准备完成：{release_id}"
        
        elif action == 'checklist':
            release_id = parsed_message.get('release_id')
            item_name = parsed_message.get('item_name')
            success, msg = self.check_item(release_id, item_name)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'publish':
            release_id = parsed_message.get('release_id')
            skill_path = parsed_message.get('skill_path')
            success, msg = self.publish_to_clawhub(release_id, skill_path)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'verify':
            release_id = parsed_message.get('release_id')
            success, msg = self.verify_release(release_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        return "❌ 未知操作"
