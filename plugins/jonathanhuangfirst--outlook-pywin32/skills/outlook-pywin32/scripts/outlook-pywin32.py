#!/usr/bin/env python3
"""
Outlook PyWin32 命令行工具
用法: outlook-pywin32.py <方法名> --参数1 值1 --参数2 值2 ...
"""

import argparse
import datetime
import json
import os
import sys
import win32com.client


def get_outlook_app():
    """获取Outlook应用对象"""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        return outlook
    except Exception as e:
        print(f"错误: 无法连接Outlook - {e}")
        sys.exit(1)


def get_namespace(outlook):
    """获取MAPI命名空间"""
    return outlook.GetNamespace("MAPI")


def get_account(account: str = None):
    """
    获取邮箱账户，优先级：
    1. 传入的 account 参数
    2. 环境变量 OUTLOOK_ACCOUNT
    3. 同目录下的 config.json 文件
    """
    if account:
        return account
    
    # 从环境变量获取
    env_account = os.environ.get("OUTLOOK_ACCOUNT")
    if env_account:
        return env_account
    
    # 从 config.json 文件获取
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("outlook_account")
        except Exception:
            pass
    
    return None


def get_mail_folder(namespace, folder_name: str = "inbox", account_email: str = None):
    """
    获取指定邮箱账户的文件夹
    
    参数:
        namespace: MAPI命名空间
        folder_name: 文件夹名称
        account_email: 邮箱账户地址，为空则使用默认账户
    """
    folder_map = {
        "inbox": 6,
        "sentitems": 5,
        "drafts": 16,
        "deleteditems": 3,
        "outbox": 4,
    }
    
    folder_id = folder_map.get(folder_name.lower(), 6)
    
    if account_email:
        for account in namespace.Accounts:
            if account.SmtpAddress.lower() == account_email.lower():
                store = account.DeliveryStore
                return store.GetDefaultFolder(folder_id)
        raise Exception(f"未找到邮箱账户: {account_email}")
    else:
        return namespace.GetDefaultFolder(folder_id)


# ============ Mail 方法集合 ============

def mail_folders(account: str = None):
    """
    检查并列出邮件文件夹

    参数:
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    account = get_account(account)
    
    folder_map = {
        6: "inbox",
        5: "sentitems",
        16: "drafts",
        3: "deleteditems",
        4: "outbox",
        9: "calendar",
        10: "contacts",
        11: "journal",
        12: "notes",
        13: "tasks",
    }
    
    results = []
    
    if account:
        for acc in namespace.Accounts:
            if acc.SmtpAddress.lower() == account.lower():
                store = acc.DeliveryStore
                for folder_id, folder_name in folder_map.items():
                    try:
                        folder = store.GetDefaultFolder(folder_id)
                        results.append({
                            "name": folder_name,
                            "id": folder_id,
                            "item_count": folder.Items.Count,
                            "display_name": folder.Name,
                        })
                    except Exception:
                        continue
                break
    else:
        for folder_id, folder_name in folder_map.items():
            try:
                folder = namespace.GetDefaultFolder(folder_id)
                results.append({
                    "name": folder_name,
                    "id": folder_id,
                    "item_count": folder.Items.Count,
                    "display_name": folder.Name,
                })
            except Exception:
                continue
    
    print("邮件文件夹列表:")
    print("-" * 80)
    for r in results:
        print(f"  {r['display_name']} ({r['name']}): {r['item_count']} 项")
    
    return results


def mail_new(to: str, subject: str, body: str = "", cc: str = "", bcc: str = ""):
    """
    创建邮件并保存到草稿箱

    参数:
        --to: 收件人邮箱 (必需)
        --subject: 邮件主题 (必需)
        --body: 邮件正文
        --cc: 抄送
        --bcc: 密送
    """
    outlook = get_outlook_app()
    mail = outlook.CreateItem(0)  # 0 = MailItem

    mail.To = to
    mail.Subject = subject
    if body:
        mail.Body = body
    if cc:
        mail.CC = cc
    if bcc:
        mail.BCC = bcc

    mail.Save()
    mail.lastModificationTime = datetime.datetime.now().date().strftime("%m/%d/%Y %H:%M:%S")
    print(f"邮件已保存到草稿箱 -> {to}: {subject}")
    return {"success": True, "to": to, "subject": subject, "saved_to": "drafts"}


def mail_list(folder: str = "inbox", limit: int = 10, account: str = None):
    """
    列出文件夹中的邮件

    参数:
        --folder: 文件夹名称 (inbox/sentitems/drafts, 默认inbox)
        --limit: 返回数量 (默认10)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    account = get_account(account)
    mail_folder = get_mail_folder(namespace, folder, account)

    messages = mail_folder.Items
    messages.Sort("[ReceivedTime]", True)  # 按时间倒序

    results = []
    for i, msg in enumerate(messages):
        if i >= limit:
            break
        is_unread = msg.UnRead if hasattr(msg, "UnRead") else False
        results.append({
            "index": i + 1,
            "subject": msg.Subject,
            "sender": msg.SenderName if hasattr(msg, "SenderName") else "N/A",
            "received": str(msg.ReceivedTime) if hasattr(msg, "ReceivedTime") else "N/A",
            "unread": is_unread,
        })

    for r in results:
        status_icon = "📩" if r["unread"] else "📭"
        status_text = "未读" if r["unread"] else "已读"
        print(f"{status_icon} [{r['index']}] {r['subject']} - {r['sender']} ({r['received']}) [{status_text}]")

    return results


def mail_read(folder: str = "inbox", index: int = 1, account: str = None):
    """
    读取指定邮件内容

    参数:
        --folder: 文件夹名称 (默认inbox)
        --index: 邮件索引 (默认1, 从mail-list获取)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    account = get_account(account)
    mail_folder = get_mail_folder(namespace, folder, account)

    messages = mail_folder.Items
    messages.Sort("[ReceivedTime]", True)

    if index < 1 or index > messages.Count:
        print(f"错误: 索引 {index} 超出范围 (1-{messages.Count})")
        return None

    msg = messages(index)

    was_unread = msg.UnRead if hasattr(msg, "UnRead") else False
    
    result = {
        "subject": msg.Subject,
        "sender": msg.SenderName if hasattr(msg, "SenderName") else "N/A",
        "sender_email": msg.SenderEmailAddress if hasattr(msg, "SenderEmailAddress") else "N/A",
        "to": msg.To if hasattr(msg, "To") else "N/A",
        "received": str(msg.ReceivedTime) if hasattr(msg, "ReceivedTime") else "N/A",
        "body": msg.Body[:500] if hasattr(msg, "Body") else "",
        "was_unread": was_unread,
    }

    print(f"主题: {result['subject']}")
    print(f"发件人: {result['sender']} <{result['sender_email']}>")
    print(f"收件人: {result['to']}")
    print(f"时间: {result['received']}")
    print(f"状态: {'未读' if was_unread else '已读'}")
    print("-" * 50)
    print(result["body"])

    # 标记为已读
    if hasattr(msg, "UnRead"):
        msg.UnRead = False

    return result


def parse_date_for_outlook(date_str: str, is_start: bool = True):
    """
    解析日期字符串并转换为Outlook Restrict方法需要的格式
    
    参数:
        date_str: 日期字符串
        is_start: 是否为起始时间，True则默认00:00:00，False则默认23:59:59
    """
    if not date_str:
        return None
    
    # 带时间的格式
    time_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]
    
    # 只带日期的格式
    date_only_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    
    dt = None
    has_time = False
    
    # 先尝试带时间的格式
    for fmt in time_formats:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            has_time = True
            break
        except ValueError:
            continue
    
    # 如果没有带时间，尝试只带日期的格式
    if not dt:
        for fmt in date_only_formats:
            try:
                dt = datetime.datetime.strptime(date_str, fmt)
                has_time = False
                break
            except ValueError:
                continue
    
    if not dt:
        return None
    
    # 如果没有指定时间，设置默认时间
    if not has_time:
        if is_start:
            dt = datetime.datetime.combine(dt.date(), datetime.datetime.min.time())
        else:
            dt = datetime.datetime.combine(dt.date(), datetime.datetime.max.time())
    
    # 转换为Outlook Restrict需要的格式: mm/dd/yyyy HH:mm:ss (24小时制)
    return dt.strftime("%m/%d/%Y %H:%M:%S")


def mail_search(query: str = "", limit: int = 50, account: str = None, start_time: str = None, end_time: str = None):
    """
    搜索邮件

    参数:
        --query: 搜索关键词 (可选)
        --limit: 返回数量 (默认50)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
        --start-time: 起始时间 (如 2024-01-01 或 2024-01-01 09:00:00)
        --end-time: 结束时间 (如 2024-12-31 或 2024-12-31 18:00:00)
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)

    account = get_account(account)
    inbox = get_mail_folder(namespace, "inbox", account)
    messages = inbox.Items

    # 使用Outlook SQL查询语法
    sql_parts = []
    
    # 关键词搜索
    if query:
        # 转义单引号
        escaped_query = query.replace("'", "''")
        sql_parts.append(f"(urn:schemas:httpmail:subject LIKE '%{escaped_query}%' OR urn:schemas:httpmail:textdescription LIKE '%{escaped_query}%')")
    
    # 时间范围搜索
    if start_time or end_time:
        start_date_outlook = parse_date_for_outlook(start_time, is_start=True)
        end_date_outlook = parse_date_for_outlook(end_time, is_start=False)
        
        if start_date_outlook:
            sql_parts.append(f"urn:schemas:httpmail:datereceived >= '{start_date_outlook}'")
        if end_date_outlook:
            sql_parts.append(f"urn:schemas:httpmail:datereceived <= '{end_date_outlook}'")
    
    # 构建完整的SQL查询
    filtered_messages = messages
    if sql_parts:
        sql_criteria = " AND ".join(sql_parts)
        full_query = f"@SQL={sql_criteria}"
        try:
            #print(f"使用SQL查询: {full_query}")
            filtered_messages = messages.Restrict(full_query)
        except Exception as e:
            print(f"警告: SQL查询失败，将使用所有邮件 - {e}")
            filtered_messages = messages

    results = []
    for msg in filtered_messages:
        if len(results) >= limit:
            break
        
        results.append({
            "subject": msg.Subject if hasattr(msg, "Subject") else "",
            "sender": msg.SenderName if hasattr(msg, "SenderName") else "",
            "received": str(msg.ReceivedTime) if hasattr(msg, "ReceivedTime") else "N/A",
        })

    for i, r in enumerate(results):
        print(f"[{i + 1}] {r['subject']} - {r['sender']} ({r['received']})")

    return results


def account_list():
    """
    列出所有可用的 Outlook 邮箱账户
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    
    accounts = []
    for account in namespace.Accounts:
        accounts.append({
            "name": account.DisplayName,
            "email": account.SmtpAddress,
        })
    
    print("可用的 Outlook 账户:")
    for i, acc in enumerate(accounts):
        print(f"  [{i + 1}] {acc['name']} <{acc['email']}>")
    
    return accounts


# ============ Calendar 方法集合 ============

def calendar_list(limit: int = 10, days: int = 7, include_today: bool = True, account: str = None):
    """
    列出即将举行的日程安排事件

    参数:
        --limit: 返回数量 (默认10)
        --days: 查看未来几天的事件 (默认7)
        --include-today: 是否包含今天的事件 (true/false, 默认true)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    account = get_account(account)
    
    # 获取日历文件夹
    if account:
        for acc in namespace.Accounts:
            if acc.SmtpAddress.lower() == account.lower():
                store = acc.DeliveryStore
                calendar_folder = store.GetDefaultFolder(9)
                break
        else:
            # 如果没有找到指定账户，使用默认文件夹
            calendar_folder = namespace.GetDefaultFolder(9)
    else:
        calendar_folder = namespace.GetDefaultFolder(9)
    
    items = calendar_folder.Items
    items.IncludeRecurrences = True
    items.Sort("[Start]")
    
    # 构建时间范围
    now = datetime.datetime.now()
    if include_today:
        start_date = datetime.datetime.combine(now.date(), datetime.datetime.min.time())
    else:
        start_date = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.datetime.min.time())
    end_date = now + datetime.timedelta(days=days)
    
    results = []
    count = 0
    
    for item in items:
        if count >= limit:
            break
        
        try:
            start_time = None
            if hasattr(item, "Start"):
                # 转换 Outlook datetime 对象为 Python datetime
                start_str = str(item.Start)
                try:
                    # 尝试解析 Outlook 的日期时间格式
                    if '+' in start_str:
                        start_str = start_str.split('+')[0]
                    if '.' in start_str and ' ' in start_str:
                        start_str = start_str.split('.')[0]
                    start_time = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
            
            if start_time and start_date <= start_time <= end_date:
                results.append({
                    "index": count + 1,
                    "subject": item.Subject if hasattr(item, "Subject") else "",
                    "start": str(item.Start) if hasattr(item, "Start") else "",
                    "end": str(item.End) if hasattr(item, "End") else "",
                    "location": item.Location if hasattr(item, "Location") else "",
                    "all_day": item.AllDayEvent if hasattr(item, "AllDayEvent") else False,
                    "is_recurring": item.IsRecurring if hasattr(item, "IsRecurring") else False,
                })
                count += 1
        except Exception:
            continue
    
    today_text = "（包含今天）" if include_today else "（不包含今天）"
    print(f"未来 {days} 天的日程安排 {today_text} (最多 {limit} 条):")
    print("-" * 80)
    for r in results:
        all_day_icon = "☀️" if r["all_day"] else "⏰"
        recurring_icon = "🔄" if r["is_recurring"] else ""
        print(f"{all_day_icon}{recurring_icon} [{r['index']}] {r['subject']}")
        print(f"    时间: {r['start']} - {r['end']}")
        if r["location"]:
            print(f"    地点: {r['location']}")
        print()
    
    return results


def calendar_new(subject: str, start: str, end: str = "", location: str = "", body: str = "", 
                 required_attendees: str = "", optional_attendees: str = "",
                 all_day: bool = False, reminder: int = 15, account: str = None):
    """
    创建一个日程安排事件

    参数:
        --subject: 日程主题 (必需)
        --start: 开始时间 (格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD)
        --end: 结束时间 (可选，默认开始时间+30分钟)
        --location: 地点 (可选)
        --body: 备注 (可选)
        --required-attendees: 必需参与人 (多个用分号分隔)
        --optional-attendees: 可选参与人 (多个用分号分隔)
        --all-day: 是否全天事件 (true/false, 默认false)
        --reminder: 提醒提前分钟数 (默认15, 0表示不提醒)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    outlook = get_outlook_app()
    
    # 解析开始时间
    start_dt = parse_date_for_outlook(start, is_start=True)
    if not start_dt:
        print(f"错误: 无法解析开始时间 '{start}'")
        return None
    
    # 转换为 datetime 对象
    try:
        start_datetime = datetime.datetime.strptime(start_dt, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        print(f"错误: 时间格式无效 '{start}'")
        return None
    
    # 解析结束时间
    if end:
        end_dt = parse_date_for_outlook(end, is_start=False)
        if not end_dt:
            print(f"错误: 无法解析结束时间 '{end}'")
            return None
        try:
            end_datetime = datetime.datetime.strptime(end_dt, "%m/%d/%Y %H:%M:%S")
        except ValueError:
            print(f"错误: 时间格式无效 '{end}'")
            return None
    else:
        # 默认30分钟
        if all_day:
            end_datetime = start_datetime + datetime.timedelta(days=1)
        else:
            end_datetime = start_datetime + datetime.timedelta(minutes=30)
    
    # 创建日历项
    appointment = outlook.CreateItem(1)  # 1 = AppointmentItem
    
    appointment.Subject = subject
    appointment.StartUTC = start_datetime
    appointment.EndUTC = end_datetime
    appointment.AllDayEvent = all_day
    
    if location:
        appointment.Location = location
    if body:
        appointment.Body = body
    if required_attendees:
        appointment.RequiredAttendees = required_attendees
    if optional_attendees:
        appointment.OptionalAttendees = optional_attendees
    
    if reminder > 0:
        appointment.ReminderSet = True
        appointment.ReminderMinutesBeforeStart = reminder
    else:
        appointment.ReminderSet = False
    
    # 如果指定了账户，使用该账户发送
    if account:
        namespace = get_namespace(outlook)
        for acc in namespace.Accounts:
            if acc.SmtpAddress.lower() == account.lower():
                appointment.Save()
                appointment.Move(acc.DeliveryStore.GetDefaultFolder(9))
                break
    else:
        appointment.Save()
    
    print(f"日程已创建: {subject}")
    print(f"  时间: {start_datetime} - {end_datetime}")
    if all_day:
        print("  全天事件: 是")
    if location:
        print(f"  地点: {location}")
    if required_attendees:
        print(f"  必需参与人: {required_attendees}")
    if optional_attendees:
        print(f"  可选参与人: {optional_attendees}")
    if reminder > 0:
        print(f"  提醒: 提前 {reminder} 分钟")
    
    return {
        "success": True,
        "subject": subject,
        "start": str(start_datetime),
        "end": str(end_datetime),
        "location": location,
        "required_attendees": required_attendees,
        "optional_attendees": optional_attendees,
        "all_day": all_day,
    }


def calendar_edit(subject: str = None, start: str = None, new_subject: str = None, new_start: str = None, new_end: str = None, location: str = None, body: str = None,
                 required_attendees: str = None, optional_attendees: str = None, all_day: bool = None, reminder: int = None, account: str = None):
    """
    修改一个日程安排事件（仅保存，不发送通知）

    参数:
        --subject: 原日程主题 (可选，用于搜索)
        --start: 原日程开始时间 (可选，用于搜索，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD)
        --new-subject: 新日程主题 (可选)
        --new-start: 新开始时间 (可选，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD)
        --new-end: 新结束时间 (可选)
        --location: 地点 (可选)
        --body: 备注 (可选)
        --required-attendees: 必需参与人 (可选，多个用分号分隔)
        --optional-attendees: 可选参与人 (可选，多个用分号分隔)
        --all-day: 是否全天事件 (可选，true/false)
        --reminder: 提醒提前分钟数 (可选，0表示不提醒)
        --account: 邮箱账户地址，优先级：1. 传入参数 2. 环境变量 OUTLOOK_ACCOUNT 3. config.json 文件
    """
    # 检查至少提供了一个搜索参数
    if subject is None and start is None:
        print("错误: 必须提供 subject 或 start 参数用于搜索日程")
        return None
    
    outlook = get_outlook_app()
    namespace = get_namespace(outlook)
    account = get_account(account)
    
    # 获取日历文件夹
    if account:
        for acc in namespace.Accounts:
            if acc.SmtpAddress.lower() == account.lower():
                store = acc.DeliveryStore
                calendar_folder = store.GetDefaultFolder(9)
                break
        else:
            # 如果没有找到指定账户，使用默认文件夹
            calendar_folder = namespace.GetDefaultFolder(9)
    else:
        calendar_folder = namespace.GetDefaultFolder(9)
    
    items = calendar_folder.Items
    items.IncludeRecurrences = True
    items.Sort("[Start]")
    
    # 解析搜索用的开始时间（如果提供）
    search_start_datetime = None
    if start:
        search_start_dt = parse_date_for_outlook(start, is_start=True)
        if not search_start_dt:
            print(f"错误: 无法解析搜索开始时间 '{start}'")
            return None
        try:
            search_start_datetime = datetime.datetime.strptime(search_start_dt, "%m/%d/%Y %H:%M:%S")
        except ValueError:
            print(f"错误: 时间格式无效 '{start}'")
            return None
    
    # 找到匹配的日程
    target_item = None
    
    for item in items:
        try:
            item_subject = item.Subject if hasattr(item, "Subject") else ""
            item_start = None
            
            if hasattr(item, "Start"):
                # 转换 Outlook datetime 对象为 Python datetime
                start_str = str(item.Start)
                try:
                    # 尝试解析 Outlook 的日期时间格式
                    if '+' in start_str:
                        start_str = start_str.split('+')[0]
                    if '.' in start_str and ' ' in start_str:
                        start_str = start_str.split('.')[0]
                    item_start = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
            
            # 匹配条件：如果提供了subject则匹配subject，如果提供了start则匹配start时间
            match = True
            if subject:
                match = match and (item_subject == subject)
            if search_start_datetime and item_start:
                # 比较开始时间（允许1分钟内的误差）
                time_diff = abs((item_start - search_start_datetime).total_seconds())
                match = match and (time_diff <= 60)
            
            if match:
                target_item = item
                break
        except Exception:
            continue
    
    if not target_item:
        if subject and start:
            print(f"错误: 未找到主题为 '{subject}' 且开始时间为 '{start}' 的日程")
        elif subject:
            print(f"错误: 未找到主题为 '{subject}' 的日程")
        else:
            print(f"错误: 未找到开始时间为 '{start}' 的日程")
        return None
    
    # 修改日程属性
    if new_subject is not None:
        target_item.Subject = new_subject
    
    if new_start is not None:
        start_dt = parse_date_for_outlook(new_start, is_start=True)
        if not start_dt:
            print(f"错误: 无法解析开始时间 '{new_start}'")
            return None
        try:
            start_datetime = datetime.datetime.strptime(start_dt, "%m/%d/%Y %H:%M:%S")
            target_item.StartUTC = start_datetime
        except ValueError:
            print(f"错误: 时间格式无效 '{new_start}'")
            return None
    
    if new_end is not None:
        end_dt = parse_date_for_outlook(new_end, is_start=False)
        if not end_dt:
            print(f"错误: 无法解析结束时间 '{new_end}'")
            return None
        try:
            end_datetime = datetime.datetime.strptime(end_dt, "%m/%d/%Y %H:%M:%S")
            target_item.EndUTC = end_datetime
        except ValueError:
            print(f"错误: 时间格式无效 '{new_end}'")
            return None
    
    if location is not None:
        target_item.Location = location
    
    if body is not None:
        target_item.Body = body
    
    if required_attendees is not None:
        target_item.RequiredAttendees = required_attendees
    
    if optional_attendees is not None:
        target_item.OptionalAttendees = optional_attendees
    
    if all_day is not None:
        target_item.AllDayEvent = all_day
    
    if reminder is not None:
        if reminder > 0:
            target_item.ReminderSet = True
            target_item.ReminderMinutesBeforeStart = reminder
        else:
            target_item.ReminderSet = False
    
    # 保存修改（不发送通知）
    target_item.Save()
    
    # 获取修改后的日程信息
    modified_subject = target_item.Subject if hasattr(target_item, "Subject") else ""
    modified_start = str(target_item.Start) if hasattr(target_item, "Start") else ""
    modified_end = str(target_item.End) if hasattr(target_item, "End") else ""
    modified_location = target_item.Location if hasattr(target_item, "Location") else ""
    modified_all_day = target_item.AllDayEvent if hasattr(target_item, "AllDayEvent") else False
    
    print(f"日程已修改: {modified_subject}")
    print(f"  时间: {modified_start} - {modified_end}")
    if modified_all_day:
        print("  全天事件: 是")
    if modified_location:
        print(f"  地点: {modified_location}")
    
    return {
        "success": True,
        "subject": modified_subject,
        "start": modified_start,
        "end": modified_end,
        "location": modified_location,
        "all_day": modified_all_day,
    }


# ============ 方法注册表 ============

METHODS = {
    "mail-folders": mail_folders,
    "mail-new": mail_new,
    "mail-list": mail_list,
    "mail-read": mail_read,
    "mail-search": mail_search,
    "account-list": account_list,
    "calendar-list": calendar_list,
    "calendar-new": calendar_new,
    "calendar-edit": calendar_edit,
}


def parse_args():
    """解析命令行参数"""
    if len(sys.argv) < 2:
        print("用法: outlook-pywin32.py <方法名> --参数 值 ...")
        print(f"可用方法: {', '.join(METHODS.keys())}")
        sys.exit(1)

    method_name = sys.argv[1].lower().replace("_", "-")

    if method_name not in METHODS:
        print(f"错误: 未知方法 '{method_name}'")
        print(f"可用方法: {', '.join(METHODS.keys())}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f"Outlook {method_name}")
    parser.add_argument("_method", nargs="?", default=method_name, help=argparse.SUPPRESS)

    # 根据方法添加参数
    func = METHODS[method_name]
    import inspect
    sig = inspect.signature(func)

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        arg_name = f"--{param_name.replace('_', '-')}"
        default = param.default if param.default != inspect.Parameter.empty else None
        # 对于 calendar-edit 方法，所有参数都是可选的，但至少需要提供 subject 或 start 中的一个
        if method_name == "calendar-edit":
            required = False
        else:
            # 其他方法中，account、start_time、end_time 参数即使默认值是 None 也不需要是必需的
            required = default is None and param_name not in ("account", "start_time", "end_time")

        parser.add_argument(
            arg_name,
            dest=param_name,
            required=required,
            default=default,
            type=str,
            help=f"{param_name}"
        )

    args = parser.parse_args(sys.argv[1:])

    # 转换参数类型
    kwargs = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        value = getattr(args, param_name, None)
        if value is not None:
            # 类型转换
            if param.annotation == int:
                if isinstance(value, str):
                    value = int(value)
            elif param.annotation == bool:
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes")
            kwargs[param_name] = value

    return method_name, kwargs


def main():
    """主入口"""
    method_name, kwargs = parse_args()
    func = METHODS[method_name]

    try:
        result = func(**kwargs)
        return result
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
