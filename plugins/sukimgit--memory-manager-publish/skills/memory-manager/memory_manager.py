#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Manager - 会话记录脚本
每次会话结束时调用，保存会话内容到临时文件
"""

import json
from datetime import datetime
from pathlib import Path
import sys

# 临时目录
TEMP_DIR = Path(__file__).parent / 'temp'

def record_session(session_data, auto_save=True):
    """
    记录会话到临时文件，并自动保存关键信息
    
    Args:
        session_data: dict，包含会话信息
        auto_save: bool，是否自动保存关键信息到 MEMORY.md
    """
    # 生成临时文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = TEMP_DIR / f"session_{timestamp}.md"
    
    # 确保临时目录存在
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成会话记录
    topics_str = '\n'.join(['- ' + topic for topic in session_data.get('topics', [])])
    key_info_str = '\n'.join(['- ' + info for info in session_data.get('key_info', [])])
    todos_str = '\n'.join(['- ' + todo for todo in session_data.get('todos', [])])
    decisions_str = '\n'.join(['- ' + decision for decision in session_data.get('decisions', [])])
    
    content = f"""# Session {timestamp} - {session_data.get('date', datetime.now().strftime("%Y-%m-%d"))}

## 时间
{session_data.get('start_time', 'N/A')} - {session_data.get('end_time', 'N/A')}

## 主题
{topics_str if topics_str else '- 无'}

## 关键信息
{key_info_str if key_info_str else '- 无'}

## 待办事项
{todos_str if todos_str else '- 无'}

## 重要决策
{decisions_str if decisions_str else '- 无'}

## 情绪状态
{session_data.get('emotion', 'N/A')}
"""
    
    # 保存到临时文件
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] Session recorded: {temp_file}")
    
    # 自动保存关键信息到 MEMORY.md（第一重保障）
    if auto_save:
        save_key_info_immediately(session_data)
    
    return temp_file

def save_key_info_immediately(session_data):
    """
    立即保存关键信息到 MEMORY.md（第一重保障）
    
    触发条件：
    - 技能发布
    - 收款信息变更
    - 重要决策
    - 任务创建/完成
    """
    key_info = session_data.get('key_info', [])
    decisions = session_data.get('decisions', [])
    todos = session_data.get('todos', [])
    
    # 检查是否需要立即保存
    need_save = False
    save_content = []
    
    # 检查关键词
    keywords = ['发布技能', '收款', '账号', '决策', '任务', '发布到 ClawHub', 'skill', 'ClawHub']
    
    for info in key_info + decisions + todos:
        if any(keyword in info for keyword in keywords):
            need_save = True
            save_content.append(f"- {info}")
    
    if need_save:
        # 追加到 MEMORY.md
        memory_file = Path(__file__).parent.parent / 'MEMORY.md'
        if not memory_file.exists():
            memory_file = Path(__file__).parent / 'MEMORY.md'
        
        if memory_file.exists():
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## 🕐 Real-time Save - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write('\n'.join(save_content))
            
            print(f"[OK] Key info saved to MEMORY.md")
        else:
            print(f"[WARN] MEMORY.md not found")

def process_temp_files():
    """
    处理所有临时文件（每日总结）
    1. 读取所有临时文件
    2. 提炼有用信息
    3. 写入正式记忆
    4. 删除临时文件
    """
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = Path(__file__).parent / 'temp' / f"{today}.md"
    
    # 获取所有临时文件
    temp_files = list(TEMP_DIR.glob("session_*.md"))
    
    if not temp_files:
        print(f"[INFO] No temp files to process")
        return None
    
    print(f"[INFO] Found {len(temp_files)} temp files")
    
    # 合并所有临时文件内容
    all_content = []
    key_info = []
    todos = []
    decisions = []
    
    for temp_file in temp_files:
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            all_content.append(content)
            
            # 简单提取关键信息
            if "## 关键信息" in content:
                key_info.append(f"From {temp_file.name}")
            if "## 待办事项" in content:
                todos.append(f"From {temp_file.name}")
            if "## 重要决策" in content:
                decisions.append(f"From {temp_file.name}")
    
    print(f"[OK] Read {len(temp_files)} sessions")
    print(f"[OK] Extracted {len(key_info)} key info")
    print(f"[OK] Extracted {len(todos)} todos")
    print(f"[OK] Extracted {len(decisions)} decisions")
    
    # 生成每日总结
    key_info_str = '\n'.join(key_info) if key_info else '- None'
    todos_str = '\n'.join(todos) if todos else '- None'
    decisions_str = '\n'.join(decisions) if decisions else '- None'
    
    summary_content = f"""# {today} - Daily Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Sessions:** {len(temp_files)}

---

## Session Summary

Total {len(temp_files)} sessions today.

---

## Key Information

{key_info_str}

---

## Todos

{todos_str}

---

## Decisions

{decisions_str}

---

## Raw Sessions

Saved to temp files, will be deleted after processing.
"""
    
    # 写入每日记忆文件
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"[OK] Daily summary written: {daily_file}")
    
    # 删除临时文件
    deleted_count = 0
    for temp_file in temp_files:
        try:
            temp_file.unlink()
            deleted_count += 1
        except Exception as e:
            print(f"[WARN] Delete failed {temp_file}: {e}")
    
    print(f"[OK] Deleted {deleted_count}/{len(temp_files)} temp files")
    
    return {
        "session_count": len(temp_files),
        "key_info_count": len(key_info),
        "todo_count": len(todos),
        "decision_count": len(decisions),
        "deleted_count": deleted_count
    }

if __name__ == "__main__":
    # 设置 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("Memory Manager - Test")
    print("=" * 60)
    
    # 测试会话记录
    test_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "start_time": datetime.now().strftime("%H:%M"),
        "end_time": datetime.now().strftime("%H:%M"),
        "topics": ["Test session", "Memory system"],
        "key_info": ["Test key info"],
        "todos": ["Test todo"],
        "decisions": ["Test decision"],
        "emotion": "Testing"
    }
    
    print("\n[Test 1] Record session...")
    temp_file = record_session(test_data)
    print(f"  Result: {temp_file}")
    
    print("\n[Test 2] Process temp files...")
    result = process_temp_files()
    if result:
        print(f"  Sessions: {result['session_count']}")
        print(f"  Key info: {result['key_info_count']}")
        print(f"  Todos: {result['todo_count']}")
        print(f"  Decisions: {result['decision_count']}")
        print(f"  Deleted: {result['deleted_count']}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
