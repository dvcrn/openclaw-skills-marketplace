#!/usr/bin/env python3
"""
对话归档系统 - 归档脚本 (v1.1)
自动归档所有对话到分类文件夹
v1.1: 添加时间戳，每天23:59自动执行
"""

import os
import json
from datetime import datetime

# 配置
ARCHIVE_DIR = "/Users/tanghao/.openclaw/workspace/conversation-archives"
CHANNEL_DIR = os.path.join(ARCHIVE_DIR, "channel-side")
WEBUI_DIR = os.path.join(ARCHIVE_DIR, "webui-side")
SEARCH_INDEX = os.path.join(ARCHIVE_DIR, "search-index.json")

def ensure_directories():
    """确保所有目录存在"""
    for d in [ARCHIVE_DIR, CHANNEL_DIR, WEBUI_DIR]:
        os.makedirs(d, exist_ok=True)

def get_session_list():
    """
    获取会话列表
    通过OpenClaw的sessions_list工具获取
    返回格式：[{"sessionKey": "...", "label": "...", "lastMessage": "..."}]
    """
    # TODO: 调用sessions_list工具
    # return sessions_list()
    return []

def get_session_history(session_key):
    """
    获取会话历史
    通过OpenClaw的sessions_history工具获取
    返回格式：{"messages": [...], "summary": "...", "generatedFiles": [...]}
    """
    # TODO: 调用sessions_history工具
    # return sessions_history(sessionKey=session_key, includeTools=True)
    return {"messages": [], "summary": "", "generatedFiles": []}

def format_timestamp(ts):
    """格式化时间戳"""
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(ts, str):
        return ts
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_channel_archive(session_key, history):
    """生成Channel端归档内容（完整对话）"""
    date = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M")

    messages = history.get("messages", [])
    message_count = len(messages)

    # 提取生成文件列表
    generated_files = history.get("generatedFiles", [])

    # 统计工具调用
    tool_calls = sum(1 for msg in messages if "Tool:" in str(msg) or "tool" in str(msg).lower())

    content = f"""# 对话归档 - Channel端（完整）

**会话ID**: {session_key}
**归档日期**: {date}
**归档时间**: {datetime.now().strftime("%H:%M:%S")}
**消息数量**: {message_count}
**工具调用**: {tool_calls}

---

## 摘要

{history.get('summary', '无摘要')}

---

## 完整对话

"""

    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        text_type = msg.get("type", "text")
        raw_ts = msg.get("timestamp")
        ts = format_timestamp(raw_ts)
        content_str = msg.get("content", "")
        tool_name = msg.get("toolName", "")
        tool_result = msg.get("toolResult", "")

        # 添加序号和时间戳
        header = f"**[{i}] {role}** | {ts}"

        if role == "tool":
            # 工具调用记录
            content += f"{header}\n```system\nTool: {tool_name}\n```\n"
            if tool_result:
                content += f"```tool-output\n{tool_result}\n```\n"
        elif isinstance(content_str, str):
            # 普通消息
            content += f"{header}\n{content_str}\n"

    content += f"""

---

## 生成文件列表

{len(generated_files)} 个文件

"""
    for i, file_path in enumerate(generated_files, 1):
        content += f"{i}. `{file_path}`\n"

    content += f"""

---

*归档于 {date} {datetime.now().strftime('%H:%M:%S')}*
*维护者: AI露娜 🌙*
"""

    return content

def generate_webui_archive(session_key, history):
    """生成WebUI端归档内容（纯文字，过滤工具调用和代码）"""
    date = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M")

    messages = history.get("messages", [])
    message_count = len(messages)

    # 提取生成文件列表
    generated_files = history.get("generatedFiles", [])

    content = f"""# 对话归档 - WebUI端（纯文字）

**会话ID**: {session_key}
**归档日期**: {date}
**归档时间**: {datetime.now().strftime("%H:%M:%S")}
**消息数量**: {message_count}

---

## 摘要

{history.get('summary', '无摘要')}

---

## 纯文字对话

（工具调用和代码块已自动过滤）

"""

    text_count = 0
    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        raw_ts = msg.get("timestamp")
        ts = format_timestamp(raw_ts)
        content_str = msg.get("content", "")

        # 过滤工具调用
        if role == "tool":
            continue

        # 过滤代码块
        if isinstance(content_str, str):
            # 移除代码块
            lines = content_str.split("\n")
            filtered_lines = []
            in_code_block = False

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if not in_code_block:
                    # 移除工具调用标记
                    if "[Tool:" not in line and "[System Message]" not in line:
                        filtered_lines.append(line)

            filtered_content = "\n".join(filtered_lines).strip()

            if filtered_content:
                # 添加序号和时间戳
                header = f"**[{text_count + 1}] {role}** | {ts}"
                content += f"{header}\n{filtered_content}\n\n"
                text_count += 1

    content += f"""
({message_count - text_count} 条非文字消息已过滤)

---

## 生成文件列表

{len(generated_files)} 个文件

"""
    for i, file_path in enumerate(generated_files, 1):
        content += f"{i}. `{file_path}`\n"

    content += f"""

---

*归档于 {date} {datetime.now().strftime('%H:%M:%S')}*
*维护者: AI露娜 🌙*
"""

    return content

def archive_session(session_key, history):
    """归档单个会话（两个版本）"""
    date = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")

    # 生成两个版本的内容
    channel_content = generate_channel_archive(session_key, history)
    webui_content = generate_webui_archive(session_key, history)

    # 文件名
    filename_base = f"{date}_session_{session_key[:12]}_{timestamp}"
    channel_filename = f"{filename_base}_channel.md"
    webui_filename = f"{filename_base}_webui.md"

    # 写入文件
    channel_filepath = os.path.join(CHANNEL_DIR, channel_filename)
    webui_filepath = os.path.join(WEBUI_DIR, webui_filename)

    with open(channel_filepath, "w", encoding="utf-8") as f:
        f.write(channel_content)

    with open(webui_filepath, "w", encoding="utf-8") as f:
        f.write(webui_content)

    # 更新搜索索引
    update_search_index(
        session_key,
        channel_filepath,
        webui_filepath,
        date,
        timestamp,
        history
    )

    return {
        "session_key": session_key,
        "channel_file": channel_filepath,
        "webui_file": webui_filepath,
        "message_count": len(history.get("messages", [])),
        "generated_files": history.get("generatedFiles", [])
    }

def update_search_index(session_key, channel_file, webui_file, date, timestamp, history):
    """更新搜索索引（JSON格式）"""
    # 读取现有索引
    if os.path.exists(SEARCH_INDEX):
        with open(SEARCH_INDEX, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"sessions": {}, "metadata": {"created_at": datetime.now().isoformat()}}

    # 提取纯文字内容用于搜索
    webui_content = generate_webui_archive(session_key, history)

    # 添加新条目
    index["sessions"][session_key] = {
        "session_key": session_key,
        "channel_file": channel_file,
        "webui_file": webui_file,
        "date": date,
        "timestamp": timestamp,
        "message_count": len(history.get("messages", [])),
        "text_message_count": webui_content.count("**[") - 1,  # 减1因为是文件头
        "generated_files": history.get("generatedFiles", []),
        "summary": history.get("summary", ""),
        "archived_at": datetime.now().isoformat()
    }

    # 更新元数据
    index["metadata"]["last_updated"] = datetime.now().isoformat()
    index["metadata"]["total_sessions"] = len(index["sessions"])

    # 保存索引
    with open(SEARCH_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 更新搜索索引")
    print(f"     总会话数: {len(index['sessions'])}")

def main():
    """主函数"""
    print("📦 对话归档系统 v1.1")
    print(f"开始归档... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")

    ensure_directories()

    # 获取会话列表
    session_list = get_session_list()

    if not session_list:
        print("⚠️  未找到会话列表。")
        print("   这可能是因为 sessions_list 工具尚未集成。")
        print("   请确保 skill 已正确配置到 OpenClaw 系统。\n")
        return

    print(f"📋 找到 {len(session_list)} 个会话\n")

    # 归档每个会话
    archived_count = 0
    for i, session in enumerate(session_list, 1):
        session_key = session.get("sessionKey", f"unknown_{i}")

        print(f"[{i}/{len(session_list)}] 归档会话: {session_key}...")

        # 获取会话历史
        history = get_session_history(session_key)

        if not history.get("messages"):
            print(f"  ⚠️  会话历史为空，跳过\n")
            continue

        # 归档（两个版本）
        result = archive_session(session_key, history)

        print(f"  ✅ Channel端: {result['channel_file']}")
        print(f"  ✅ WebUI端: {result['webui_file']}")
        print(f"  📊 消息数: {result['message_count']}")
        if result['generated_files']:
            print(f"  📁 生成文件: {len(result['generated_files'])} 个")

        print()
        archived_count += 1

    # 完成
    print(f"✅ 归档完成！共归档 {archived_count} 个会话。\n")
    print(f"📂 归档文件夹: {ARCHIVE_DIR}")
    print(f"🔍 搜索索引: {SEARCH_INDEX}\n")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
