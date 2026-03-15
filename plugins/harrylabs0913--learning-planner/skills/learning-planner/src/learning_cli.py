#!/usr/bin/env python3
"""
Learning Planner CLI - 学习规划师命令行工具
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich import box

from learning_database import (
    init_database, get_db_path,
    create_goal, get_goal, list_goals, update_goal, delete_goal, 
    get_subgoals, get_goal_tree, update_progress, get_stats as get_goal_stats,
    create_plan, get_plan, list_plans, get_today_plans, get_week_plans,
    complete_plan, postpone_plan, generate_daily_plan, get_completion_stats,
    create_card, get_card, list_cards, get_due_cards, get_new_cards, review_card, get_review_stats,
    add_resource, get_resource, list_resources, search_resources, link_to_goal,
    start_session, end_session, get_session, list_sessions, get_total_time, get_daily_stats,
)
from learning_utils import (
    print_goal_table, print_goal_tree, print_plan_table, print_card, print_resource_table,
    print_stats_panel, print_progress_bar,
    format_datetime, format_date, format_duration,
)

console = Console()


# 初始化数据库
init_database()


@click.group()
@click.version_option(version="1.0.0", prog_name="learning")
def cli():
    """学习规划师 - 个人学习管理系统"""


# ========== 学习目标命令 ==========
@cli.group()
def goal():
    """学习目标管理"""
    pass


@goal.command()
@click.argument("title")
@click.option("--description", "-d", help="目标描述")
@click.option("--parent", "-p", type=int, help="父目标 ID")
@click.option("--priority", "-P", type=click.Choice(["low", "medium", "high"]), 
              default="medium", help="优先级")
@click.option("--deadline", help="截止日期 (YYYY-MM-DD)")
@click.option("--hours", "-h", type=int, default=0, help="预估学习时长(小时)")
def create(title, description, parent, priority, deadline, hours):
    """创建学习目标"""
    goal_id = create_goal(title, description, parent, priority, deadline, hours)
    console.print(f"[green]✓ 目标已创建 (ID: {goal_id})[/green]")


@goal.command()
@click.option("--status", "-s", type=click.Choice(["active", "completed", "paused"]))
def list(status):
    """列出目标"""
    goals = list_goals(status=status)
    print_goal_table(goals)


@goal.command()
@click.argument("goal_id", type=int)
def show(goal_id):
    """查看目标详情"""
    goal = get_goal(goal_id)
    if not goal:
        console.print("[red]目标不存在[/red]")
        return
    
    subgoals = get_subgoals(goal_id)
    
    content = f"""
[bold cyan]🎯 {goal.get('title')}[/bold cyan]

[bold]描述:[/bold] {goal.get('description') or '无'}
[bold]优先级:[/bold] {goal.get('priority')}
[bold]状态:[/bold] {goal.get('status')}
[bold]进度:[/bold] {print_progress_bar(goal.get('progress', 0), 100)}
[bold]截止日期:[/bold] {goal.get('deadline') or '无'}
[bold]预估时长:[/bold] {goal.get('estimated_hours')} 小时
[bold]已完成:[/bold] {goal.get('completed_hours')} 小时

[bold]子目标 ({len(subgoals)}个):[/bold]
    """.strip()
    
    for sg in subgoals:
        content += f"\n  • {sg.get('title')} [{sg.get('progress'):.0f}%]"
    
    console.print(Panel(content, box=box.ROUNDED))


@goal.command()
@click.argument("goal_id", type=int)
@click.option("--percent", "-p", type=float, required=True, help="进度百分比 0-100")
def progress(goal_id, percent):
    """更新目标进度"""
    update_progress(goal_id, percent)
    console.print(f"[green]✓ 进度已更新为 {percent}%[/green]")


@goal.command()
@click.argument("goal_id", type=int)
def complete(goal_id):
    """完成目标"""
    update_progress(goal_id, 100)
    console.print(f"[green]✓ 目标已完成[/green]")


@goal.command()
@click.argument("goal_id", type=int)
@click.confirmation_option(prompt="确定要删除这个目标吗？")
def delete(goal_id):
    """删除目标"""
    delete_goal(goal_id)
    console.print(f"[green]✓ 目标已删除[/green]")


@goal.command()
def tree():
    """查看技能树"""
    goals = get_goal_tree()
    print_goal_tree(goals)


# ========== 学习计划命令 ==========
@cli.group()
def plan():
    """学习计划管理"""
    pass


@plan.command()
def today():
    """今日学习计划"""
    plans = get_today_plans()
    if not plans:
        # 自动生成今日计划
        plans = generate_daily_plan()
    print_plan_table(plans, "今日学习计划")


@plan.command()
def week():
    """本周学习计划"""
    plans = get_week_plans()
    print_plan_table(plans, "本周学习计划")


@plan.command()
def list():
    """列出所有计划"""
    plans = list_plans()
    print_plan_table(plans)


@plan.command()
@click.argument("plan_id", type=int)
def complete(plan_id):
    """完成任务"""
    complete_plan(plan_id)
    console.print(f"[green]✓ 任务已完成[/green]")


@plan.command()
@click.argument("plan_id", type=int)
@click.option("--days", "-d", type=int, default=1, help="推迟天数")
def postpone(plan_id, days):
    """推迟任务"""
    postpone_plan(plan_id, days)
    console.print(f"[green]✓ 任务已推迟 {days} 天[/green]")


# ========== 复习卡片命令 ==========
@cli.group()
def card():
    """复习卡片管理"""
    pass


@card.command()
@click.argument("front")
@click.option("--back", "-b", required=True, help="答案")
@click.option("--goal", "-g", type=int, help="关联目标 ID")
@click.option("--tags", "-t", help="标签(逗号分隔)")
def create(front, back, goal, tags):
    """创建复习卡片"""
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    card_id = create_card(front, back, goal, tag_list)
    console.print(f"[green]✓ 卡片已创建 (ID: {card_id})[/green]")


@card.command()
@click.argument("card_id", type=int)
def show(card_id):
    """查看卡片"""
    card = get_card(card_id)
    if card:
        print_card(card, show_answer=True)
    else:
        console.print("[red]卡片不存在[/red]")


@card.command()
def list():
    """列出卡片"""
    cards = list_cards()
    console.print(f"[bold]共有 {len(cards)} 张卡片[/bold]")
    for card in cards[:10]:
        console.print(f"  [{card.get('id')}] {card.get('front')[:40]}...")


@card.command()
@click.argument("card_id", type=int)
@click.option("--quality", "-q", type=int, required=True, 
              help="评分 0-5 (5完美, 4正确, 3困难, 2接近, 1模糊, 0忘记)")
@click.option("--time", "-t", type=int, help="用时(秒)")
def review(card_id, quality, time):
    """复习卡片"""
    if quality < 0 or quality > 5:
        console.print("[red]评分必须在 0-5 之间[/red]")
        return
    
    review_card(card_id, quality, time)
    
    quality_text = ["完全忘记", "模糊记得", "接近正确", "正确但困难", "正确", "完美"][quality]
    console.print(f"[green]✓ 复习完成 - 评分: {quality} ({quality_text})[/green]")


# ========== 复习命令 ==========
@cli.group()
def review():
    """复习管理"""
    pass


@review.command()
def today():
    """今日复习"""
    due = get_due_cards(limit=20)
    new = get_new_cards(limit=10)
    
    console.print(f"\n[bold cyan]📚 今日复习[/bold cyan]")
    console.print(f"到期卡片: {len(due)} 张")
    console.print(f"新卡片: {len(new)} 张")
    
    if due:
        console.print(f"\n[bold]到期卡片:[/bold]")
        for card in due[:5]:
            print_card(card)
            console.print()


@review.command()
def stats():
    """复习统计"""
    stats = get_review_stats()
    print_stats_panel(stats, "复习统计")


# ========== 学习资源命令 ==========
@cli.group()
def resource():
    """学习资源管理"""
    pass


@resource.command()
@click.argument("title")
@click.option("--url", "-u", help="资源链接")
@click.option("--type", "-t", type=click.Choice(["video", "article", "book", "documentation"]),
              default="article", help="资源类型")
@click.option("--tags", help="标签(逗号分隔)")
@click.option("--goal", "-g", type=int, help="关联目标 ID")
@click.option("--notes", "-n", help="备注")
def add(title, url, type, tags, goal, notes):
    """添加学习资源"""
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    resource_id = add_resource(title, url, type, tag_list, goal, notes)
    console.print(f"[green]✓ 资源已添加 (ID: {resource_id})[/green]")


@resource.command()
def list():
    """列出资源"""
    resources = list_resources()
    print_resource_table(resources)


@resource.command()
@click.argument("keyword")
def search(keyword):
    """搜索资源"""
    resources = search_resources(keyword)
    print_resource_table(resources, f"搜索 '{keyword}' 的结果")


@resource.command()
@click.argument("resource_id", type=int)
@click.option("--goal", "-g", type=int, required=True, help="目标 ID")
def link(resource_id, goal):
    """关联资源到目标"""
    link_to_goal(resource_id, goal)
    console.print(f"[green]✓ 资源已关联到目标[/green]")


# ========== 学习时长命令 ==========
@cli.group()
def session():
    """学习时长记录"""
    pass


@session.command()
@click.argument("goal_id", type=int)
@click.option("--notes", "-n", help="备注")
def start(goal_id, notes):
    """开始学习"""
    session_id = start_session(goal_id, notes)
    console.print(f"[green]✓ 学习会话已开始 (ID: {session_id})[/green]")


@session.command()
@click.argument("session_id", type=int)
def stop(session_id):
    """结束学习"""
    end_session(session_id)
    session_data = get_session(session_id)
    if session_data:
        console.print(f"[green]✓ 学习会话已结束[/green]")
        console.print(f"  时长: {format_duration(session_data.get('duration', 0))}")


@session.command()
@click.option("--days", "-d", type=int, default=7, help="天数")
def list(days):
    """学习记录"""
    sessions = list_sessions(days=days)
    console.print(f"[bold]最近 {days} 天学习记录:[/bold]")
    for s in sessions[:10]:
        console.print(f"  {format_datetime(s.get('start_time'))} - "
                     f"{format_duration(s.get('duration', 0))}")


@session.command()
@click.option("--days", "-d", type=int, default=7, help="天数")
def time(days):
    """学习时长统计"""
    total = get_total_time(days=days)
    daily = get_daily_stats(days=days)
    
    console.print(f"\n[bold cyan]⏱️ 学习时长统计 ({days}天)[/bold cyan]")
    console.print(f"总时长: {format_duration(total)}")
    
    if daily:
        console.print(f"\n[bold]每日分布:[/bold]")
        for d in daily:
            console.print(f"  {d.get('day')}: {format_duration(d.get('total_minutes'))} "
                         f"({d.get('session_count')} 次)")


# ========== 统计报告命令 ==========
@cli.group()
def report():
    """学习报告"""
    pass


@report.command()
def stats():
    """学习统计概览"""
    goal_stats = get_goal_stats()
    plan_stats = get_completion_stats()
    review_stats_data = get_review_stats()
    
    content = f"""
[bold cyan]📊 学习统计[/bold cyan]

[bold]目标[/bold]
  总目标: {goal_stats['total']}
  进行中: {goal_stats['active']}
  已完成: {goal_stats['completed']}
  平均进度: {goal_stats['avg_progress']:.1f}%

[bold]计划[/bold]
  完成率: {plan_stats['completion_rate']:.1f}%
  已完成: {plan_stats['completed']}
  待完成: {plan_stats['pending']}

[bold]复习[/bold]
  总卡片: {review_stats_data['total_cards']}
  今日到期: {review_stats_data['due_today']}
  平均质量: {review_stats_data['avg_quality']:.2f}
    """.strip()
    
    console.print(Panel(content, box=box.ROUNDED))


# ========== 数据管理命令 ==========
@cli.group()
def data():
    """数据管理"""
    pass


@data.command("path")
def data_path():
    """查看数据库路径"""
    console.print(f"数据库路径: {get_db_path()}")


# 主入口
@click.group()
@click.version_option(version="1.0.0")
def main():
    """学习规划师 - 个人学习管理系统"""
    pass


# 自定义帮助信息
@main.command()
def help():
    """显示帮助信息"""
    console.print(Panel.fit(
        "[bold cyan]🎯 学习规划师[/bold cyan]\n\n"
        "命令:\n"
        "  [green]learning goal[/green]     学习目标\n"
        "  [green]learning plan[/green]     学习计划\n"
        "  [green]learning card[/green]     复习卡片\n"
        "  [green]learning review[/green]   复习管理\n"
        "  [green]learning resource[/green]  学习资源\n"
        "  [green]learning session[/green]   学习时长\n"
        "  [green]learning report[/green]   学习报告\n\n"
        "使用 [yellow]learning --help[/yellow] 查看帮助",
        box=box.ROUNDED
    ))


# 注册子命令
main.add_command(goal)
main.add_command(plan)
main.add_command(card)
main.add_command(review)
main.add_command(resource)
main.add_command(session)
main.add_command(report)
main.add_command(data)


if __name__ == "__main__":
    main()
