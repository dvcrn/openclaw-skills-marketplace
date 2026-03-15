"""
学习计划数据操作
"""
from datetime import datetime, timedelta
from .connection import get_connection


def create_plan(goal_id: int, title: str, description: str = None,
                scheduled_date: str = None, estimated_minutes: int = 30) -> int:
    """创建学习计划"""
    if not scheduled_date:
        scheduled_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO plans (goal_id, title, description, scheduled_date, estimated_minutes)
        VALUES (?, ?, ?, ?, ?)
    """, (goal_id, title, description, scheduled_date, estimated_minutes))
    
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plan_id


def get_plan(plan_id: int) -> dict:
    """获取计划详情"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def list_plans(date: str = None, status: str = None, goal_id: int = None) -> list:
    """列出计划"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM plans WHERE 1=1"
    params = []
    
    if date:
        query += " AND scheduled_date = ?"
        params.append(date)
    if status:
        query += " AND status = ?"
        params.append(status)
    if goal_id:
        query += " AND goal_id = ?"
        params.append(goal_id)
    
    query += " ORDER BY scheduled_date, created_at"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_today_plans() -> list:
    """获取今日计划"""
    today = datetime.now().strftime("%Y-%m-%d")
    return list_plans(date=today)


def get_week_plans() -> list:
    """获取本周计划"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM plans 
        WHERE scheduled_date BETWEEN ? AND ?
        ORDER BY scheduled_date, created_at
    """, (week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def complete_plan(plan_id: int):
    """完成任务"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE plans SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (plan_id,))
    
    conn.commit()
    conn.close()


def postpone_plan(plan_id: int, days: int = 1):
    """推迟任务"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT scheduled_date FROM plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    
    if row:
        current_date = datetime.strptime(row[0], "%Y-%m-%d")
        new_date = current_date + timedelta(days=days)
        
        cursor.execute("""
            UPDATE plans SET scheduled_date = ?, status = 'pending'
            WHERE id = ?
        """, (new_date.strftime("%Y-%m-%d"), plan_id))
        
        conn.commit()
    
    conn.close()


def delete_plan(plan_id: int):
    """删除计划"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()


def get_completion_stats(days: int = 7) -> dict:
    """获取完成统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM plans 
        WHERE scheduled_date >= date('now', '-{} days')
    """.format(days))
    
    row = cursor.fetchone()
    conn.close()
    
    total = row[0] or 0
    completed = row[1] or 0
    
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": round(completed / total * 100, 2) if total > 0 else 0,
    }


def generate_daily_plan() -> list:
    """生成今日学习计划"""
    from .goals import list_goals
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 获取活跃目标
    active_goals = list_goals(status="active")
    
    plans = []
    for goal in active_goals[:3]:  # 每天最多3个目标
        # 检查是否已有今日计划
        existing = list_plans(date=today, goal_id=goal["id"])
        if not existing:
            plan_id = create_plan(
                goal_id=goal["id"],
                title=f"学习: {goal['title']}",
                description=f"继续学习 {goal['title']}",
                scheduled_date=today,
                estimated_minutes=30
            )
            plans.append(get_plan(plan_id))
    
    return plans
