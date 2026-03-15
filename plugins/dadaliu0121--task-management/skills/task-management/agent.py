"""
销售任务管理 Skill - OpenClaw Agent
对接后端 API: https://iautomark.sdm.qq.com/ai-assistant
"""

import aiohttp
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://iautomark.sdm.qq.com/ai-assistant"
TIME_FORMAT = "%Y-%m-%d %H:%M"
SHANGHAI_TZ = timezone(timedelta(hours=8))


def _convert_to_timestamp(time_str: str) -> int | None:
    """将时间字符串转换为秒级时间戳（上海时区）"""
    try:
        dt = datetime.strptime(time_str, TIME_FORMAT)
        dt = dt.replace(tzinfo=SHANGHAI_TZ)
        return int(dt.timestamp())
    except ValueError:
        return None


def _convert_from_timestamp(ts: int) -> str:
    """将秒级时间戳转换为时间字符串（上海时区）"""
    dt = datetime.fromtimestamp(ts, tz=SHANGHAI_TZ)
    return dt.strftime(TIME_FORMAT)


async def _post(session: aiohttp.ClientSession, path: str, body: dict) -> dict:
    """发送 POST 请求到后端 API"""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    async with session.post(url, json=body, headers=headers) as resp:
        text = await resp.text()
        return json.loads(text)


async def list_tasks(sale_id: str, external_id: str = None, task_date: str = None) -> str:
    """
    查询销售任务列表

    参数:
        sale_id: 销售人员 ID（必填）
        external_id: 客户 ID（可选）。不传则查询该销售的所有任务
        task_date: 查询指定日期的任务，格式为 yyyy-MM-dd（可选）
    """
    if not sale_id:
        return "错误：请提供销售 ID（sale_id）"

    body = {"saleId": sale_id}

    # 仅当提供了 external_id 且与 sale_id 不同时才传入
    if external_id and external_id != sale_id:
        body["externalId"] = external_id

    if task_date:
        body["taskTime"] = task_date

    try:
        async with aiohttp.ClientSession() as session:
            data = await _post(session, "/v1/task/getMyTask", body)

            if data.get("code") != 0:
                return f"查询失败：{data.get('msg', '未知错误')}"

            tasks = data.get("data")
            if not tasks:
                return "查询成功：没有找到任务"

            lines = []
            for task in tasks:
                task_time_str = _convert_from_timestamp(task["taskTime"]) if task.get("taskTime") else "未设置"
                lines.append(
                    f"任务ID: {task['id']}  "
                    f"标题: {task.get('name', '')}  "
                    f"详情: {task.get('description', '')}  "
                    f"时间: {task_time_str}  "
                    f"目标客户: {task.get('externalName', '')}"
                )
            return "\n".join(lines)

    except Exception as e:
        return f"查询失败：{str(e)}，请重试"


async def create_task(
    sale_id: str,
    external_id: str,
    title: str,
    content: str,
    task_time: str,
    sop_id: str = None,
) -> str:
    """
    创建销售任务

    参数:
        sale_id: 销售人员 ID（必填）
        external_id: 客户 ID（必填）
        title: 任务标题（必填）
        content: 任务内容（必填）
        task_time: 任务时间，格式为 yyyy-MM-dd HH:mm（必填）
        sop_id: SOP ID，格式为 "sopId" 或 "sopId-groupId"（可选）
    """
    if not all([sale_id, external_id, title, content, task_time]):
        return "错误：sale_id、external_id、title、content、task_time 均为必填参数"

    timestamp = _convert_to_timestamp(task_time)
    if timestamp is None:
        return "错误：时间格式不正确，请使用 yyyy-MM-dd HH:mm 格式，例如 2026-03-10 14:30"

    body = {
        "saleId": sale_id,
        "externalId": external_id,
        "name": title,
        "description": content,
        "taskOrigin": 2,
        "taskTime": timestamp,
        "taskStatus": 2,
        "type": 1,
    }

    # 解析 sop_id
    if sop_id:
        parts = sop_id.split("-")
        if len(parts) >= 1:
            body["sopId"] = int(parts[0])
        if len(parts) >= 2:
            body["groupId"] = int(parts[1])

    try:
        async with aiohttp.ClientSession() as session:
            data = await _post(session, "/v1/task/create", body)

            if data.get("code") != 0:
                return f"创建失败：{data.get('msg', '未知错误')}"

            return "任务创建成功"

    except Exception as e:
        return f"创建失败：{str(e)}，请重试"


async def update_task(
    sale_id: str,
    task_id: int,
    title: str = None,
    content: str = None,
    task_time: str = None,
) -> str:
    """
    更新销售任务

    参数:
        sale_id: 销售人员 ID（必填）
        task_id: 任务 ID（必填）
        title: 新的任务标题（可选）
        content: 新的任务内容（可选）
        task_time: 新的任务时间，格式为 yyyy-MM-dd HH:mm（可选）
    """
    if not sale_id or not task_id:
        return "错误：请提供 sale_id 和 task_id"

    body = {
        "taskId": task_id,
        "taskStatus": 2,
    }

    if title:
        body["taskName"] = title
    if content:
        body["taskContent"] = content
    if task_time:
        timestamp = _convert_to_timestamp(task_time)
        if timestamp is None:
            return "错误：时间格式不正确，请使用 yyyy-MM-dd HH:mm 格式，例如 2026-03-10 14:30"
        body["taskTime"] = timestamp

    try:
        async with aiohttp.ClientSession() as session:
            data = await _post(session, "/v1/task/updateMyTask", body)

            if data.get("code") != 0:
                return f"更新失败：{data.get('msg', '未知错误')}"

            return f"任务更新成功，任务 ID: {task_id}"

    except Exception as e:
        return f"更新失败：{str(e)}，请重试"


async def delete_task(task_ids: str) -> str:
    """
    删除销售任务（支持批量）

    参数:
        task_ids: 要删除的任务 ID，多个用逗号分隔，如 "1,2,3"
    """
    if not task_ids:
        return "错误：请提供要删除的任务 ID"

    try:
        ids = [int(tid.strip()) for tid in task_ids.split(",")]
    except ValueError:
        return "错误：任务 ID 格式不正确，请提供数字 ID，多个用逗号分隔"

    fail_ids = []

    try:
        async with aiohttp.ClientSession() as session:
            for tid in ids:
                try:
                    data = await _post(session, "/v1/task/deleteMyTask", {"taskId": tid})
                    if data.get("code") != 0:
                        fail_ids.append(tid)
                except Exception:
                    fail_ids.append(tid)

            if fail_ids:
                fail_str = ", ".join(str(fid) for fid in fail_ids)
                return f"部分任务删除失败，失败的任务 ID: {fail_str}"

            return "所有任务删除成功"

    except Exception as e:
        return f"删除失败：{str(e)}，请重试"
