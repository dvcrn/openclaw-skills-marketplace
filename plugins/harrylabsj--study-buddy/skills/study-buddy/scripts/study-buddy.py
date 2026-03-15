#!/usr/bin/env python3
"""
Study Buddy - 智能学习伴侣 CLI 工具
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 数据存储目录
DATA_DIR = Path.home() / ".study-buddy"
PROFILE_FILE = DATA_DIR / "profile.json"
PLANS_DIR = DATA_DIR / "plans"
LOGS_DIR = DATA_DIR / "logs"
WRONG_DIR = DATA_DIR / "wrong_questions"


def init_data_dir():
    """初始化数据目录"""
    DATA_DIR.mkdir(exist_ok=True)
    PLANS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    WRONG_DIR.mkdir(exist_ok=True)


def load_profile():
    """加载用户档案"""
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_profile(profile):
    """保存用户档案"""
    with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def cmd_start():
    """开始学习之旅 - 交互式收集学习背景"""
    print("🎯 欢迎使用 Study Buddy - 你的智能学习伴侣！")
    print("=" * 50)
    
    profile = load_profile()
    if profile:
        print(f"\n📋 发现已有学习档案：{profile.get('subject', '未设置')}")
        overwrite = input("是否重新设置？(y/N): ").strip().lower()
        if overwrite != 'y':
            print("保持现有设置。使用 /study-buddy today 查看今日任务。")
            return
    
    print("\n让我们先了解一下你的学习背景...")
    
    # 收集学习背景
    subject = input("\n1. 你想学习什么？（如：Python编程、英语口语、吉他）: ").strip()
    
    print("\n2. 你的学习目标是什么？")
    print("   a) 兴趣爱好，随便学学")
    print("   b) 工作需要，提升技能")
    print("   c) 考试/认证，有明确 deadline")
    print("   d) 转行/求职，系统学习")
    goal_type = input("请选择 (a/b/c/d): ").strip().lower()
    
    print("\n3. 你目前的基础如何？")
    print("   a) 完全零基础")
    print("   b) 了解一些基础概念")
    print("   c) 有一定经验，想进阶")
    print("   d) 经验丰富，追求精通")
    level = input("请选择 (a/b/c/d): ").strip().lower()
    
    daily_time = input("\n4. 每天能投入多少时间学习？（如：30分钟、1小时）: ").strip()
    
    print("\n5. 你偏好哪种学习方式？")
    print("   a) 看视频教程")
    print("   b) 阅读文档/书籍")
    print("   c) 动手实践项目")
    print("   d) 混合方式")
    learning_style = input("请选择 (a/b/c/d): ").strip().lower()
    
    deadline = input("\n6. 有完成目标的时间节点吗？（如：2026-06-01，或直接回车表示无）: ").strip()
    
    # 构建档案
    profile = {
        "subject": subject,
        "goal_type": goal_type,
        "level": level,
        "daily_time": daily_time,
        "learning_style": learning_style,
        "deadline": deadline if deadline else None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    save_profile(profile)
    
    print("\n" + "=" * 50)
    print("✅ 学习档案已创建！")
    print(f"\n📚 学习主题: {subject}")
    print(f"⏱️  每日投入: {daily_time}")
    print(f"🎯 目标类型: {goal_type}")
    
    # 生成初始学习计划
    print("\n📝 正在为你生成学习计划...")
    generate_plan(profile)
    
    print("\n💡 提示：使用 /study-buddy today 查看今日任务")


def generate_plan(profile):
    """基于档案生成学习计划"""
    plan = {
        "subject": profile["subject"],
        "created_at": datetime.now().isoformat(),
        "phases": []
    }
    
    # 根据水平生成不同阶段
    level_map = {"a": "入门", "b": "基础", "c": "进阶", "d": "精通"}
    current_level = level_map.get(profile["level"], "入门")
    
    # 简单示例：生成3个阶段
    phases = [
        {
            "name": f"阶段一：{current_level}基础",
            "duration": "2周",
            "tasks": [
                f"了解{profile['subject']}的基本概念",
                "完成第一个Hello World",
                "建立学习习惯"
            ]
        },
        {
            "name": "阶段二：核心技能",
            "duration": "4周",
            "tasks": [
                "学习核心知识点",
                "完成3-5个练习项目",
                "整理学习笔记"
            ]
        },
        {
            "name": "阶段三：实践应用",
            "duration": "持续",
            "tasks": [
                "完成一个完整项目",
                "复习巩固知识",
                "探索进阶内容"
            ]
        }
    ]
    
    plan["phases"] = phases
    
    # 保存计划
    plan_file = PLANS_DIR / f"plan_{datetime.now().strftime('%Y%m%d')}.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 学习计划已生成并保存！")
    print(f"   共 {len(phases)} 个阶段")
    for i, phase in enumerate(phases, 1):
        print(f"   {i}. {phase['name']} ({phase['duration']})")
    
    return plan


def cmd_today():
    """查看今日学习任务"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    print(f"🌟 今日学习任务 - {profile['subject']}")
    print("=" * 50)
    
    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今日是否已打卡
    today_log_file = LOGS_DIR / f"{today}.json"
    if today_log_file.exists():
        with open(today_log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
        print(f"\n✅ 今日已学习 {log.get('duration', '未知时长')}")
        print(f"   内容: {log.get('content', '无记录')}")
    else:
        print("\n⏳ 今日还未打卡")
    
    # 显示建议任务
    print("\n📋 建议今日任务：")
    print("   1. 投入 " + profile.get('daily_time', '30分钟') + " 学习")
    print("   2. 完成一个小目标")
    print("   3. 记录学习笔记")
    
    print("\n💡 使用 /study-buddy checkin \"学习内容\" 打卡")


def cmd_checkin(content, duration=None):
    """学习打卡"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"{today}.json"
    
    log_entry = {
        "date": today,
        "content": content,
        "duration": duration or "未记录",
        "timestamp": datetime.now().isoformat(),
        "subject": profile.get('subject', '未知')
    }
    
    # 如果已有记录，追加
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        if isinstance(existing, list):
            existing.append(log_entry)
        else:
            existing = [existing, log_entry]
        log_entry = existing
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
    
    print("✅ 打卡成功！")
    print(f"   学习内容: {content}")
    if duration:
        print(f"   学习时长: {duration}")
    
    # 计算连续打卡天数
    streak = calculate_streak()
    if streak > 1:
        print(f"\n🔥 连续打卡 {streak} 天！继续保持！")


def calculate_streak():
    """计算连续打卡天数"""
    streak = 0
    today = datetime.now()
    
    for i in range(365):  # 最多查一年
        check_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        log_file = LOGS_DIR / f"{check_date}.json"
        if log_file.exists():
            streak += 1
        else:
            if i > 0:  # 如果不是今天，中断
                break
    
    return streak


def cmd_progress():
    """查看学习进度"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    print(f"📊 学习进度报告 - {profile['subject']}")
    print("=" * 50)
    
    # 统计学习天数
    log_files = list(LOGS_DIR.glob("*.json"))
    total_days = len(log_files)
    
    # 统计本周学习
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_logs = [f for f in log_files if datetime.strptime(f.stem, '%Y-%m-%d') >= week_start]
    week_days = len(week_logs)
    
    # 连续打卡
    streak = calculate_streak()
    
    print(f"\n📈 统计数据：")
    print(f"   累计学习天数: {total_days} 天")
    print(f"   本周学习: {week_days} 天")
    print(f"   连续打卡: {streak} 天")
    
    # 显示最近的学习记录
    print(f"\n📝 最近学习记录：")
    recent_logs = sorted(log_files, reverse=True)[:5]
    for log_file in recent_logs:
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
        if isinstance(log, list):
            log = log[-1]
        date = log.get('date', log_file.stem)
        content = log.get('content', '无记录')[:30]
        print(f"   {date}: {content}...")
    
    # 简单进度条
    print(f"\n⏳ 学习进度: {'█' * min(total_days, 20)}{'░' * (20 - min(total_days, 20))} {total_days}天")


def cmd_feedback():
    """获取学习反馈建议"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    print(f"💡 学习反馈 - {profile['subject']}")
    print("=" * 50)
    
    # 基于简单规则的反馈
    streak = calculate_streak()
    log_files = list(LOGS_DIR.glob("*.json"))
    total_days = len(log_files)
    
    print("\n🎯 学习建议：")
    
    if streak >= 7:
        print("   ✅ 太棒了！你已经连续打卡一周以上，学习习惯正在养成！")
    elif streak >= 3:
        print("   👍 不错！连续打卡3天以上，继续保持这个节奏！")
    elif total_days == 0:
        print("   💪 刚开始学习？建议从每天15分钟开始，逐步建立习惯。")
    else:
        print("   📌 建议每天固定时间学习，哪怕只有15分钟，也比长时间中断好。")
    
    # 根据学习风格给建议
    style_map = {
        "a": "视频学习",
        "b": "阅读学习",
        "c": "实践学习",
        "d": "混合学习"
    }
    style = style_map.get(profile.get('learning_style', 'd'), '混合学习')
    print(f"\n📝 基于你的偏好（{style}）：")
    
    if profile.get('learning_style') == 'a':
        print("   - 推荐在B站、YouTube找优质教程")
        print("   - 看视频时做笔记，暂停思考")
    elif profile.get('learning_style') == 'b':
        print("   - 找一本经典教材系统学习")
        print("   - 建立自己的知识库/笔记系统")
    elif profile.get('learning_style') == 'c':
        print("   - 边学边做，从简单项目开始")
        print("   - 遇到问题再回头查资料")
    else:
        print("   - 结合多种方式：看视频+做练习+读文档")
        print("   - 根据内容灵活调整学习方式")
    
    print("\n🌟 下一步行动：")
    print("   1. 完成今日学习任务")
    print("   2. 记录学习心得")
    print("   3. 周末回顾本周所学")


def cmd_plan():
    """查看/管理学习计划"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    print(f"📋 学习计划 - {profile['subject']}")
    print("=" * 50)
    
    # 加载最新计划
    plan_files = sorted(PLANS_DIR.glob("*.json"), reverse=True)
    if not plan_files:
        print("\n⏳ 还没有学习计划。正在生成...")
        generate_plan(profile)
        plan_files = sorted(PLANS_DIR.glob("*.json"), reverse=True)
    
    if plan_files:
        with open(plan_files[0], 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        print(f"\n📅 计划创建时间: {plan.get('created_at', '未知')[:10]}")
        print(f"📚 学习主题: {plan.get('subject', profile['subject'])}")
        print(f"🎯 阶段数量: {len(plan.get('phases', []))}")
        
        # 计算当前阶段
        log_files = list(LOGS_DIR.glob("*.json"))
        total_days = len(log_files)
        
        print(f"\n📊 各阶段详情：")
        for i, phase in enumerate(plan.get('phases', []), 1):
            # 简单估算当前阶段
            is_current = False
            if i == 1 and total_days < 14:
                is_current = True
            elif i == 2 and 14 <= total_days < 42:
                is_current = True
            elif i == 3 and total_days >= 42:
                is_current = True
            
            marker = "👉" if is_current else "  "
            print(f"\n{marker} 阶段{i}: {phase.get('name', '未命名')}")
            print(f"     时长: {phase.get('duration', '未设定')}")
            print(f"     任务:")
            for task in phase.get('tasks', []):
                print(f"       • {task}")
        
        print(f"\n💡 提示：使用 /study-buddy today 查看今日具体任务")


def cmd_report():
    """生成学习报告"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    print(f"📊 学习报告 - {profile['subject']}")
    print("=" * 50)
    
    # 统计数据
    log_files = list(LOGS_DIR.glob("*.json"))
    total_days = len(log_files)
    streak = calculate_streak()
    
    # 计算本周数据
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_logs = [f for f in log_files if datetime.strptime(f.stem, '%Y-%m-%d') >= week_start]
    week_days = len(week_logs)
    
    # 计算本月数据
    month_start = datetime.now().replace(day=1)
    month_logs = [f for f in log_files if datetime.strptime(f.stem, '%Y-%m-%d') >= month_start]
    month_days = len(month_logs)
    
    print(f"\n📈 学习概况")
    print(f"   累计学习: {total_days} 天")
    print(f"   连续打卡: {streak} 天")
    print(f"   本周学习: {week_days} 天")
    print(f"   本月学习: {month_days} 天")
    
    # 学习频率评级
    print(f"\n🏆 学习评级")
    if streak >= 30:
        print("   🌟 卓越 - 连续打卡一个月，学习习惯非常棒！")
    elif streak >= 14:
        print("   ⭐ 优秀 - 连续两周打卡，保持得很好！")
    elif streak >= 7:
        print("   👍 良好 - 连续一周打卡，习惯正在养成！")
    elif streak >= 3:
        print("   ✨ 进步 - 连续打卡3天以上，继续加油！")
    elif total_days > 0:
        print("   🌱 起步 - 已经开始学习，建议每天打卡！")
    else:
        print("   📝 未开始 - 还没有学习记录，从今天开始吧！")
    
    # 阶段评估
    print(f"\n🎯 阶段评估")
    if total_days < 7:
        print("   当前处于：适应期")
        print("   建议：建立固定的学习时间，哪怕每天只有15分钟")
    elif total_days < 30:
        print("   当前处于：养成期")
        print("   建议：保持当前节奏，逐步增加学习时长")
    elif total_days < 90:
        print("   当前处于：巩固期")
        print("   建议：开始尝试更复杂的任务，挑战自己")
    else:
        print("   当前处于：进阶期")
        print("   建议：考虑深入学习或拓展相关领域")
    
    # 下周目标
    print(f"\n📋 下周目标")
    print(f"   目标：连续打卡 {streak + 7} 天")
    print(f"   建议：每天投入 {profile.get('daily_time', '30分钟')}")
    print(f"   重点：保持学习节奏，记录学习心得")
    
    # 生成报告文件
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "subject": profile['subject'],
        "stats": {
            "total_days": total_days,
            "streak": streak,
            "week_days": week_days,
            "month_days": month_days
        },
        "rating": "卓越" if streak >= 30 else "优秀" if streak >= 14 else "良好" if streak >= 7 else "进步" if streak >= 3 else "起步"
    }
    
    report_file = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: {report_file}")


def cmd_wrong(action=None, content=None, subject=None):
    """错题本管理"""
    profile = load_profile()
    if not profile:
        print("⚠️  还没有学习档案。请先运行 /study-buddy start")
        return
    
    if action == "add" and content:
        # 添加错题
        wrong_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "content": content,
            "subject": subject or profile['subject'],
            "added_at": datetime.now().isoformat(),
            "review_count": 0,
            "last_review": None,
            "mastered": False
        }
        
        wrong_file = WRONG_DIR / "wrong_questions.json"
        wrong_list = []
        if wrong_file.exists():
            with open(wrong_file, 'r', encoding='utf-8') as f:
                wrong_list = json.load(f)
        
        wrong_list.append(wrong_entry)
        
        with open(wrong_file, 'w', encoding='utf-8') as f:
            json.dump(wrong_list, f, ensure_ascii=False, indent=2)
        
        print("✅ 错题已记录")
        print(f"   内容: {content[:50]}..." if len(content) > 50 else f"   内容: {content}")
        print(f"   学科: {wrong_entry['subject']}")
        print(f"\n💡 使用 /study-buddy wrong list 查看所有错题")
        
    elif action == "list":
        # 列出错题
        wrong_file = WRONG_DIR / "wrong_questions.json"
        if not wrong_file.exists():
            print("📭 错题本为空")
            print("\n💡 使用 /study-buddy wrong add \"错题内容\" 添加错题")
            return
        
        with open(wrong_file, 'r', encoding='utf-8') as f:
            wrong_list = json.load(f)
        
        if not wrong_list:
            print("📭 错题本为空")
            return
        
        print(f"📚 错题本 - 共 {len(wrong_list)} 题")
        print("=" * 50)
        
        # 按掌握状态分组
        unmastered = [w for w in wrong_list if not w.get('mastered', False)]
        mastered = [w for w in wrong_list if w.get('mastered', False)]
        
        if unmastered:
            print(f"\n📝 待复习 ({len(unmastered)} 题):")
            for i, w in enumerate(unmastered[-5:], 1):  # 显示最近5题
                content = w['content'][:40] + "..." if len(w['content']) > 40 else w['content']
                review_info = f"(已复习{w.get('review_count', 0)}次)" if w.get('review_count', 0) > 0 else ""
                print(f"   {i}. [{w['subject']}] {content} {review_info}")
        
        if mastered:
            print(f"\n✅ 已掌握 ({len(mastered)} 题):")
            print(f"   共 {len(mastered)} 题已标记为掌握")
        
        print(f"\n💡 复习建议：优先复习待复习的题目")
        
    elif action == "review" and content:
        # 标记复习
        wrong_file = WRONG_DIR / "wrong_questions.json"
        if not wrong_file.exists():
            print("⚠️  错题本为空")
            return
        
        with open(wrong_file, 'r', encoding='utf-8') as f:
            wrong_list = json.load(f)
        
        # 查找并更新
        found = False
        for w in wrong_list:
            if w['id'] == content or w['content'] == content:
                w['review_count'] = w.get('review_count', 0) + 1
                w['last_review'] = datetime.now().isoformat()
                found = True
                print(f"✅ 已记录复习: {w['content'][:30]}...")
                print(f"   累计复习 {w['review_count']} 次")
                
                # 如果复习3次以上，建议标记掌握
                if w['review_count'] >= 3:
                    print(f"\n💡 这道题已复习3次，是否标记为已掌握？")
                    print(f"   使用 /study-buddy wrong master \"{w['id']}\" 标记掌握")
                break
        
        if found:
            with open(wrong_file, 'w', encoding='utf-8') as f:
                json.dump(wrong_list, f, ensure_ascii=False, indent=2)
        else:
            print("⚠️  未找到该错题")
            
    elif action == "master" and content:
        # 标记掌握
        wrong_file = WRONG_DIR / "wrong_questions.json"
        if not wrong_file.exists():
            print("⚠️  错题本为空")
            return
        
        with open(wrong_file, 'r', encoding='utf-8') as f:
            wrong_list = json.load(f)
        
        found = False
        for w in wrong_list:
            if w['id'] == content or w['content'] == content:
                w['mastered'] = True
                w['mastered_at'] = datetime.now().isoformat()
                found = True
                print(f"✅ 已标记掌握: {w['content'][:30]}...")
                break
        
        if found:
            with open(wrong_file, 'w', encoding='utf-8') as f:
                json.dump(wrong_list, f, ensure_ascii=False, indent=2)
        else:
            print("⚠️  未找到该错题")
    else:
        # 显示帮助
        print("📚 错题本管理")
        print("=" * 50)
        print("\n用法:")
        print("   /study-buddy wrong add \"错题内容\" [--subject \"学科\"]")
        print("   /study-buddy wrong list")
        print("   /study-buddy wrong review \"错题ID\"")
        print("   /study-buddy wrong master \"错题ID\"")
        print("\n示例:")
        print('   /study-buddy wrong add "二次函数求根公式应用错误"')
        print('   /study-buddy wrong list')


def cmd_data():
    """查看数据存储位置"""
    print("📁 Study Buddy 数据存储位置")
    print("=" * 50)
    print(f"\n数据目录: {DATA_DIR}")
    print(f"   档案文件: {PROFILE_FILE}")
    print(f"   计划目录: {PLANS_DIR}")
    print(f"   日志目录: {LOGS_DIR}")
    print(f"   错题目录: {WRONG_DIR}")
    
    # 检查数据是否存在
    if PROFILE_FILE.exists():
        print(f"\n✅ 学习档案: 已存在")
    else:
        print(f"\n⏳ 学习档案: 未创建")
    
    plan_count = len(list(PLANS_DIR.glob("*.json")))
    log_count = len(list(LOGS_DIR.glob("*.json")))
    wrong_count = 0
    wrong_file = WRONG_DIR / "wrong_questions.json"
    if wrong_file.exists():
        with open(wrong_file, 'r', encoding='utf-8') as f:
            wrong_count = len(json.load(f))
    
    print(f"📋 学习计划: {plan_count} 个")
    print(f"📝 学习记录: {log_count} 条")
    print(f"❌ 错题记录: {wrong_count} 题")


def main():
    """主入口"""
    init_data_dir()
    
    parser = argparse.ArgumentParser(
        description="Study Buddy - 智能学习伴侣",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  study-buddy start              # 开始学习之旅
  study-buddy today              # 查看今日任务
  study-buddy checkin "内容"      # 学习打卡
  study-buddy progress           # 查看进度
  study-buddy feedback           # 获取反馈
  study-buddy plan               # 查看学习计划
  study-buddy report             # 生成学习报告
  study-buddy wrong add "内容"    # 添加错题
  study-buddy wrong list         # 查看错题
  study-buddy data               # 查看数据位置
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # start 命令
    subparsers.add_parser('start', help='开始学习之旅（交互式设置）')
    
    # today 命令
    subparsers.add_parser('today', help='查看今日学习任务')
    
    # checkin 命令
    checkin_parser = subparsers.add_parser('checkin', help='学习打卡')
    checkin_parser.add_argument('content', help='学习内容')
    checkin_parser.add_argument('--duration', '-d', help='学习时长（如：30分钟）')
    
    # progress 命令
    subparsers.add_parser('progress', help='查看学习进度')
    
    # feedback 命令
    subparsers.add_parser('feedback', help='获取学习反馈建议')
    
    # plan 命令 - 查看学习计划
    subparsers.add_parser('plan', help='查看学习计划详情')
    
    # report 命令 - 学习报告
    subparsers.add_parser('report', help='生成学习报告')
    
    # wrong 命令 - 错题本
    wrong_parser = subparsers.add_parser('wrong', help='错题本管理')
    wrong_subparsers = wrong_parser.add_subparsers(dest='wrong_action', help='错题本操作')
    
    # wrong add
    wrong_add = wrong_subparsers.add_parser('add', help='添加错题')
    wrong_add.add_argument('content', help='错题内容')
    wrong_add.add_argument('--subject', '-s', help='学科（可选）')
    
    # wrong list
    wrong_subparsers.add_parser('list', help='列出错题')
    
    # wrong review
    wrong_review = wrong_subparsers.add_parser('review', help='记录复习')
    wrong_review.add_argument('content', help='错题ID或内容')
    
    # wrong master
    wrong_master = wrong_subparsers.add_parser('master', help='标记掌握')
    wrong_master.add_argument('content', help='错题ID或内容')
    
    # data 命令
    subparsers.add_parser('data', help='查看数据存储位置')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        cmd_start()
    elif args.command == 'today':
        cmd_today()
    elif args.command == 'checkin':
        cmd_checkin(args.content, args.duration)
    elif args.command == 'progress':
        cmd_progress()
    elif args.command == 'feedback':
        cmd_feedback()
    elif args.command == 'plan':
        cmd_plan()
    elif args.command == 'report':
        cmd_report()
    elif args.command == 'wrong':
        if hasattr(args, 'wrong_action') and args.wrong_action:
            if args.wrong_action == 'add':
                cmd_wrong('add', args.content, args.subject)
            elif args.wrong_action == 'list':
                cmd_wrong('list')
            elif args.wrong_action == 'review':
                cmd_wrong('review', args.content)
            elif args.wrong_action == 'master':
                cmd_wrong('master', args.content)
            else:
                cmd_wrong()
        else:
            cmd_wrong()
    elif args.command == 'data':
        cmd_data()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
