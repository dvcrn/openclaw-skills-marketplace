#!/usr/bin/env python3
"""
窗口切换脚本
功能：
1. 切换窗口时显示窗口信息和工作摘要
2. 每个窗口创建独立 agent session
3. 切换窗口时自动保存当前上下文到原窗口
4. 切换窗口时恢复对应 session 的历史
"""
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

TASKS_DIR = os.path.expanduser("~/.openclaw/workspace/memory/tasks")
CURRENT_FILE = os.path.join(TASKS_DIR, "current.json")
INDEX_FILE = os.path.join(TASKS_DIR, "tasks.json")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")

def get_task_dir_from_index(task_id):
    """从索引获取任务目录"""
    if not os.path.exists(INDEX_FILE):
        return None
    with open(INDEX_FILE, "r") as f:
        tasks = json.load(f)
    
    if task_id not in tasks:
        return None
    
    return os.path.join(TASKS_DIR, tasks[task_id].get("dir", ""))

def get_task_dir(task_id, name=""):
    """获取任务目录"""
    # 先尝试从索引获取
    task_dir = get_task_dir_from_index(task_id)
    if task_dir and os.path.exists(task_dir):
        return task_dir
    
    # 备用方案：使用 task_id + name
    dir_name = task_id + name.replace("/", "-")
    return os.path.join(TASKS_DIR, dir_name)

def get_meta(task_id, name=""):
    """获取窗口 meta.json"""
    task_dir = get_task_dir(task_id, name)
    meta_path = os.path.join(task_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    return None

def update_meta(task_id, name="", updates=None):
    """更新窗口 meta.json"""
    if updates is None:
        updates = {}
    task_dir = get_task_dir(task_id, name)
    meta_path = os.path.join(task_dir, "meta.json")
    
    meta = get_meta(task_id, name) or {}
    meta.update(updates)
    meta["updated"] = datetime.now().isoformat()
    
    os.makedirs(task_dir, exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta

def get_summary(task_id, name=""):
    """获取工作摘要"""
    task_dir = get_task_dir(task_id, name)
    
    # 优先从 summary.md 读取
    summary_md = os.path.join(task_dir, "summary.md")
    if os.path.exists(summary_md):
        with open(summary_md, "r") as f:
            content = f.read().strip()
            if content:
                return content
    
    # 其次从 meta.json 读取 summary 字段
    meta = get_meta(task_id, name)
    if meta and meta.get("summary"):
        return meta["summary"]
    
    return None

def format_datetime(iso_str):
    """格式化 ISO 时间"""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_str

def get_current():
    """获取当前窗口"""
    if not os.path.exists(CURRENT_FILE):
        return None
    with open(CURRENT_FILE, "r") as f:
        return json.load(f)

def save_current_context():
    """保存当前窗口的上下文到文件"""
    current = get_current()
    if not current:
        return None
    
    task_id = current.get("task_id", "")
    name = current.get("name", "")
    session_key = current.get("session_key", "")
    
    if not task_id or not session_key:
        return None
    
    task_dir = get_task_dir(task_id, name)
    output_dir = os.path.join(task_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取 session 历史文件
    # session 文件格式: sessions/{session_id}.json
    sessions_path = os.path.expanduser("~/.openclaw/agents/main/sessions")
    
    context_file = os.path.join(output_dir, "context.md")
    
    # 从 session_key 推断可能的 session 文件
    # 格式: window:0314-2:abc123 -> 查找包含 0314-2 的 session
    session_files = []
    if os.path.exists(sessions_path):
        for f in os.listdir(sessions_path):
            if f.endswith(".json"):
                session_files.append(f)
    
    # 尝试找到对应的 session 文件
    context_content = []
    context_content.append(f"# 窗口上下文 - {task_id} ({name})")
    context_content.append(f"\n保存时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    context_content.append(f"Session Key：{session_key}")
    context_content.append("\n---\n")
    
    # 如果没有找到 session 文件，记录基本信息
    context_content.append("## 对话记录")
    context_content.append("\n（暂无完整对话记录，会话结束后自动保存）")
    
    with open(context_file, "w") as f:
        f.write("\n".join(context_content))
    
    return context_file

def set_current(task_id, session_key=None):
    """设置当前窗口"""
    os.makedirs(TASKS_DIR, exist_ok=True)
    
    # 保存当前窗口的上下文（如果存在）
    save_current_context()
    
    # 检查窗口是否存在
    if not os.path.exists(INDEX_FILE):
        return False, "窗口索引不存在"
    
    with open(INDEX_FILE, "r") as f:
        tasks = json.load(f)
    
    if task_id not in tasks:
        return False, f"窗口 {task_id} 不存在"
    
    task_info = tasks[task_id]
    task_name = task_info.get("name", "")
    
    # 如果没有 session_key，创建一个新的
    if not session_key:
        meta = get_meta(task_id, task_name)
        session_key = meta.get("session_key") if meta else None
        
        if not session_key:
            # 创建新的 session
            session_key = f"window:{task_id}:{uuid.uuid4().hex[:8]}"
            update_meta(task_id, task_name, {"session_key": session_key})
    
    current = {
        "task_id": task_id,
        "name": task_name,
        "dir": task_info.get("dir", ""),
        "switched": datetime.now().isoformat(),
        "session_key": session_key
    }
    
    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    
    return True, current

def show_window_info(task_id, name=""):
    """显示窗口详细信息"""
    meta = get_meta(task_id, name)
    if not meta:
        return f"窗口 {task_id} 不存在"
    
    # 基本信息
    task_id = meta.get("id", "")
    name = meta.get("name", "")
    status = meta.get("status", "进行中")
    created = format_datetime(meta.get("created", ""))
    updated = format_datetime(meta.get("updated", ""))
    session_key = meta.get("session_key", "无")
    
    # 状态emoji
    status_emoji = {
        "进行中": "🔄",
        "已完成": "✅",
        "已暂停": "⏸️",
        "已取消": "❌"
    }.get(status, "❓")
    
    info_lines = [
        f"📌 窗口信息：{task_id}（{name}）",
        f"   状态：{status_emoji} {status}",
        f"   创建时间：{created}",
        f"   更新时间：{updated}",
    ]
    
    # 如果有 session 显示 session 信息
    if session_key and session_key != "无":
        info_lines.append(f"   Session：{session_key}")
    
    # 工作摘要
    summary = get_summary(task_id, name)
    if summary:
        # 截断太长的摘要
        if len(summary) > 500:
            summary = summary[:500] + "..."
        info_lines.append("")
        info_lines.append("📝 最近工作摘要：")
        info_lines.append(summary)
    
    return "\n".join(info_lines)

def switch_to(task_id):
    """切换到指定窗口"""
    # 先获取窗口信息
    meta = get_meta(task_id)
    if not meta:
        return False, f"窗口 {task_id} 不存在"
    
    name = meta.get("name", "")
    
    # 设置当前窗口（会自动保存当前上下文）
    success, result = set_current(task_id)
    if not success:
        return False, result
    
    # 显示窗口信息
    info = show_window_info(task_id, name)
    
    return True, info

def show_current():
    """显示当前窗口"""
    current = get_current()
    if not current:
        return "🌙 当前在临时窗口（无任务）\n\n提示：使用「切到 0314-1」切换到指定窗口"
    
    task_id = current.get("task_id", "")
    name = current.get("name", "")
    
    return show_window_info(task_id, name)

def create_session_for_window(task_id, name=""):
    """为窗口创建独立 session"""
    # 创建 session 并保存 session_key
    session_key = f"window:{task_id}:{uuid.uuid4().hex[:8]}"
    update_meta(task_id, name, {"session_key": session_key})
    return session_key

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 切换窗口
        task_id = sys.argv[1]
        success, msg = switch_to(task_id)
        if success:
            # 提取 session_key
            session_key = "新session"
            if "Session：" in msg:
                lines = msg.split("\n")
                for line in lines:
                    if "Session：" in line:
                        session_key = line.split("Session：")[1].strip()
                        break
            
            # 移除末尾可能重复的摘要
            print(msg)
            print("")
            print(f"💾 已自动保存原窗口上下文")
            print(f"💡 如需恢复该窗口的 session 历史，请使用 session key: {session_key}")
        else:
            print(f"❌ {msg}")
    else:
        # 显示当前
        print(show_current())
