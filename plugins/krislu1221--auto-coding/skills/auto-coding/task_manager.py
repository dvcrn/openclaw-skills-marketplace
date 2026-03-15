"""
任务管理器 - 自主编码 Agent 核心组件
Task Manager for Autonomous Coding Agent
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class TaskManager:
    """任务列表管理器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.task_file = self.project_dir / "feature_list.json"
        self.progress_file = self.project_dir / "claude-progress.txt"
        self.spec_file = self.project_dir / "app_spec.txt"
    
    def create_tasks(self, tasks: list) -> bool:
        """创建任务列表"""
        try:
            self.project_dir.mkdir(parents=True, exist_ok=True)
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"创建任务列表失败：{e}")
            return False
    
    def load_tasks(self) -> list:
        """加载任务列表"""
        if not self.task_file.exists():
            return []
        try:
            with open(self.task_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载任务列表失败：{e}")
            return []
    
    def get_pending_tasks(self) -> list:
        """获取待处理任务"""
        tasks = self.load_tasks()
        return [t for t in tasks if t['status'] == 'pending']
    
    def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """根据 ID 获取任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: int, status: str, notes: str = None) -> bool:
        """更新任务状态"""
        try:
            tasks = self.load_tasks()
            for task in tasks:
                if task['id'] == task_id:
                    task['status'] = status
                    if notes:
                        task['notes'] = notes
                    task['updated_at'] = datetime.now().isoformat()
                    break
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"更新任务状态失败：{e}")
            return False
    
    def get_progress_summary(self) -> dict:
        """获取进度摘要"""
        tasks = self.load_tasks()
        if not tasks:
            return {"total": 0, "done": 0, "blocked": 0, "pending": 0, "percentage": 0}
        
        total = len(tasks)
        done = sum(1 for t in tasks if t['status'] == 'done')
        blocked = sum(1 for t in tasks if t['status'] == 'blocked')
        pending = total - done - blocked
        
        return {
            "total": total,
            "done": done,
            "blocked": blocked,
            "pending": pending,
            "percentage": round(done / total * 100, 1) if total > 0 else 0
        }
    
    def log_progress(self, message: str) -> bool:
        """记录进度日志"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.progress_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
            return True
        except Exception as e:
            print(f"记录进度失败：{e}")
            return False
    
    def save_spec(self, spec: str) -> bool:
        """保存项目规格说明"""
        try:
            with open(self.spec_file, 'w', encoding='utf-8') as f:
                f.write(spec)
            return True
        except Exception as e:
            print(f"保存规格说明失败：{e}")
            return False
    
    def load_spec(self) -> str:
        """加载项目规格说明"""
        if not self.spec_file.exists():
            return ""
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def init_git(self) -> tuple[bool, str]:
        """初始化 git 仓库"""
        import subprocess
        try:
            # 检查是否已经是 git 仓库
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, "已是 git 仓库"
            
            # 初始化 git
            subprocess.run(["git", "init"], cwd=self.project_dir, check=True, capture_output=True)
            
            # 创建 .gitignore
            gitignore = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# Node.js
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# System
.DS_Store
Thumbs.db

# Project
*.log
claude-progress.txt
"""
            with open(self.project_dir / ".gitignore", 'w') as f:
                f.write(gitignore)
            
            # 首次 commit
            subprocess.run(["git", "add", "."], cwd=self.project_dir, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: project setup"],
                cwd=self.project_dir,
                check=True,
                capture_output=True
            )
            
            return True, "Git 仓库初始化成功"
        except subprocess.CalledProcessError as e:
            return False, f"Git 操作失败：{e}"
        except Exception as e:
            return False, f"初始化失败：{e}"
    
    def git_commit(self, message: str) -> tuple[bool, str]:
        """提交 git"""
        import subprocess
        try:
            subprocess.run(["git", "add", "."], cwd=self.project_dir, check=True, capture_output=True)
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, "提交成功"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def get_status_report(self) -> str:
        """生成状态报告"""
        summary = self.get_progress_summary()
        tasks = self.load_tasks()
        
        report = []
        report.append("=" * 50)
        report.append("📊 项目进度报告")
        report.append("=" * 50)
        report.append(f"总任务数：{summary['total']}")
        report.append(f"✅ 已完成：{summary['done']}")
        report.append(f"⏳ 待处理：{summary['pending']}")
        report.append(f"🚫 已阻塞：{summary['blocked']}")
        report.append(f"📈 进度：{summary['percentage']}%")
        report.append("")
        
        # 已完成任务
        done_tasks = [t for t in tasks if t['status'] == 'done']
        if done_tasks:
            report.append("✅ 已完成任务:")
            for t in done_tasks[:10]:  # 只显示前 10 个
                report.append(f"  - {t['name']}")
            if len(done_tasks) > 10:
                report.append(f"  ... 还有 {len(done_tasks) - 10} 个")
            report.append("")
        
        # 待处理任务
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        if pending_tasks:
            report.append("⏳ 待处理任务:")
            for t in pending_tasks[:5]:  # 只显示前 5 个
                report.append(f"  - {t['name']}")
            if len(pending_tasks) > 5:
                report.append(f"  ... 还有 {len(pending_tasks) - 5} 个")
            report.append("")
        
        # 阻塞任务
        blocked_tasks = [t for t in tasks if t['status'] == 'blocked']
        if blocked_tasks:
            report.append("🚫 阻塞任务:")
            for t in blocked_tasks:
                report.append(f"  - {t['name']}: {t.get('notes', '未知原因')}")
            report.append("")
        
        report.append("=" * 50)
        return "\n".join(report)


# 测试代码
if __name__ == "__main__":
    print("运行 TaskManager 测试...")
    
    # 创建测试项目
    tm = TaskManager("/tmp/auto-coding-test-project")
    
    # 测试创建任务
    test_tasks = [
        {"id": 1, "name": "用户登录", "status": "pending", "priority": "high"},
        {"id": 2, "name": "主页", "status": "pending", "priority": "high"},
        {"id": 3, "name": "设置", "status": "pending", "priority": "medium"},
    ]
    assert tm.create_tasks(test_tasks), "创建任务失败"
    print("✅ 创建任务测试通过")
    
    # 测试加载任务
    tasks = tm.load_tasks()
    assert len(tasks) == 3, "加载任务数量错误"
    print("✅ 加载任务测试通过")
    
    # 测试更新状态
    assert tm.update_task_status(1, "done", "测试完成"), "更新状态失败"
    task = tm.get_task_by_id(1)
    assert task['status'] == 'done', "状态更新未生效"
    print("✅ 更新状态测试通过")
    
    # 测试进度摘要
    summary = tm.get_progress_summary()
    assert summary['done'] == 1, "已完成数量错误"
    assert summary['pending'] == 2, "待处理数量错误"
    print("✅ 进度摘要测试通过")
    
    # 测试日志记录
    assert tm.log_progress("测试进度日志"), "记录日志失败"
    print("✅ 日志记录测试通过")
    
    # 测试状态报告
    report = tm.get_status_report()
    assert "项目进度报告" in report, "状态报告格式错误"
    print("✅ 状态报告测试通过")
    
    print("\n🎉 所有 TaskManager 测试通过!")
