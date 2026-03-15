"""
统计数据
生成工作统计报告
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta


def get_task_stats(days: int = 30) -> dict:
    """
    获取任务统计
    
    :param days: 统计最近多少天
    :return: 统计数据
    """
    tasks_file = Path("D:\\OpenClawDocs\\reminders\\tasks.json")
    if not tasks_file.exists():
        return {"error": "任务文件不存在"}
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 统计
    total_tasks = len(data.get("reminders", []))
    completed_tasks = len(data.get("completed", []))
    
    # 按状态分类
    pending = [t for t in data.get("reminders", []) if t.get("status") == "pending"]
    completed = [t for t in data.get("reminders", []) if t.get("status") == "completed"]
    
    # 按优先级分类
    high_priority = [t for t in data.get("reminders", []) if t.get("priority") == "high"]
    normal_priority = [t for t in data.get("reminders", []) if t.get("priority") == "normal"]
    low_priority = [t for t in data.get("reminders", []) if t.get("priority") == "low"]
    
    # 有依赖的任务
    with_dependencies = [t for t in data.get("reminders", []) if t.get("depends_on")]
    
    return {
        "period_days": days,
        "total": total_tasks,
        "completed": completed_tasks,
        "pending": len(pending),
        "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0,
        "by_priority": {
            "high": len(high_priority),
            "normal": len(normal_priority),
            "low": len(low_priority)
        },
        "with_dependencies": len(with_dependencies),
        "documents_generated": sum(1 for t in data.get("reminders", []) if t.get("attachments"))
    }


def get_document_stats(days: int = 30) -> dict:
    """
    获取文档统计
    
    :param days: 统计最近多少天
    :return: 统计数据
    """
    base_dirs = [
        "D:\\OpenClawDocs\\temp",
        "D:\\OpenClawDocs\\projects",
        "D:\\OpenClawDocs\\meetings"
    ]
    
    stats = {
        "total": 0,
        "by_category": {
            "temp": 0,
            "projects": 0,
            "meetings": 0
        },
        "by_type": {
            "md": 0,
            "docx": 0,
            "pdf": 0
        },
        "total_size": 0
    }
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for base_dir in base_dirs:
        base_path = Path(base_dir)
        if not base_path.exists():
            continue
        
        category = base_path.name
        
        for file in base_path.rglob("*"):
            if file.is_file():
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if mtime >= cutoff_date:
                    stats["total"] += 1
                    
                    if category in stats["by_category"]:
                        stats["by_category"][category] += 1
                    
                    suffix = file.suffix.lower()
                    if suffix in ['.md']:
                        stats["by_type"]["md"] += 1
                    elif suffix in ['.docx']:
                        stats["by_type"]["docx"] += 1
                    elif suffix in ['.pdf']:
                        stats["by_type"]["pdf"] += 1
                    
                    stats["total_size"] += file.stat().st_size
    
    stats["total_size_mb"] = round(stats["total_size"] / 1024 / 1024, 2)
    
    return stats


def get_meeting_stats(days: int = 30) -> dict:
    """
    获取会议统计
    
    :param days: 统计最近多少天
    :return: 统计数据
    """
    meetings_dir = Path("D:\\OpenClawDocs\\meetings")
    if not meetings_dir.exists():
        return {"error": "会议目录不存在"}
    
    cutoff_date = datetime.now() - timedelta(days=days)
    meetings = []
    
    for item in meetings_dir.iterdir():
        if item.is_dir():
            # 从目录名提取日期
            try:
                dir_name = item.name
                date_str = dir_name[:8]  # YYYYMMDD
                meeting_date = datetime.strptime(date_str, "%Y%m%d")
                
                if meeting_date >= cutoff_date:
                    files = list(item.rglob("*"))
                    meetings.append({
                        "name": item.name,
                        "date": meeting_date.strftime("%Y-%m-%d"),
                        "files": len(files)
                    })
            except:
                continue
    
    meetings.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "period_days": days,
        "total_meetings": len(meetings),
        "meetings": meetings,
        "avg_files_per_meeting": round(sum(m["files"] for m in meetings) / len(meetings), 1) if meetings else 0
    }


def generate_summary_report(days: int = 30) -> str:
    """
    生成总结报告
    
    :param days: 统计天数
    :return: 报告文本
    """
    task_stats = get_task_stats(days)
    doc_stats = get_document_stats(days)
    meeting_stats = get_meeting_stats(days)
    
    report = f"""📊 **工作统计报告**（最近{days}天）

## 任务统计
- 任务总数：{task_stats.get('total', 0)}
- 已完成：{task_stats.get('completed', 0)}
- 进行中：{task_stats.get('pending', 0)}
- 完成率：{task_stats.get('completion_rate', 0)}%
- 生成文档：{task_stats.get('documents_generated', 0)}份

## 文档统计
- 文档总数：{doc_stats.get('total', 0)}
- 草稿（temp）：{doc_stats['by_category'].get('temp', 0)}
- 正式（projects）：{doc_stats['by_category'].get('projects', 0)}
- 会议资料：{doc_stats['by_category'].get('meetings', 0)}
- 总大小：{doc_stats.get('total_size_mb', 0)}MB

## 会议统计
- 会议总数：{meeting_stats.get('total_meetings', 0)}
- 平均每场会议文件：{meeting_stats.get('avg_files_per_meeting', 0)}份

## 时间节省估算
- 每份文档节省：约 30 分钟
- 总计节省：约 {task_stats.get('documents_generated', 0) * 0.5}小时
"""
    
    return report


# 测试
if __name__ == "__main__":
    print("=== 任务统计 ===")
    task_stats = get_task_stats(30)
    for k, v in task_stats.items():
        print(f"{k}: {v}")
    
    print("\n=== 文档统计 ===")
    doc_stats = get_document_stats(30)
    for k, v in doc_stats.items():
        print(f"{k}: {v}")
    
    print("\n=== 会议统计 ===")
    meeting_stats = get_meeting_stats(30)
    print(f"会议总数：{meeting_stats.get('total_meetings', 0)}")
