"""
学习资源数据操作
"""
import json
from .connection import get_connection


def add_resource(title: str, url: str = None, resource_type: str = "article",
                 tags: list = None, goal_id: int = None, notes: str = None) -> int:
    """添加学习资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO resources (title, url, resource_type, tags, goal_id, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, url, resource_type, json.dumps(tags or [], ensure_ascii=False), 
          goal_id, notes))
    
    resource_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resource_id


def get_resource(resource_id: int) -> dict:
    """获取资源详情"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return _row_to_dict(row)
    return None


def list_resources(goal_id: int = None, resource_type: str = None) -> list:
    """列出资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if goal_id:
        cursor.execute("SELECT * FROM resources WHERE goal_id = ? ORDER BY created_at DESC", 
                       (goal_id,))
    elif resource_type:
        cursor.execute("SELECT * FROM resources WHERE resource_type = ? ORDER BY created_at DESC", 
                       (resource_type,))
    else:
        cursor.execute("SELECT * FROM resources ORDER BY created_at DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]


def search_resources(keyword: str) -> list:
    """搜索资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM resources 
        WHERE title LIKE ? OR notes LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]


def update_resource(resource_id: int, data: dict):
    """更新资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ["title", "url", "resource_type", "tags", "goal_id", "notes"]
    
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            if field == "tags" and data[field] is not None:
                updates.append(f"{field} = ?")
                values.append(json.dumps(data[field], ensure_ascii=False))
            else:
                updates.append(f"{field} = ?")
                values.append(data[field])
    
    if not updates:
        conn.close()
        return
    
    values.append(resource_id)
    query = f"UPDATE resources SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()


def delete_resource(resource_id: int):
    """删除资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()


def link_to_goal(resource_id: int, goal_id: int):
    """关联资源到目标"""
    update_resource(resource_id, {"goal_id": goal_id})


def get_resources_by_tag(tag: str) -> list:
    """按标签获取资源"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM resources 
        WHERE tags LIKE ? 
        ORDER BY created_at DESC
    """, (f'%"{tag}"%',))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row) -> dict:
    """将行转换为字典"""
    result = dict(row)
    if result.get("tags"):
        try:
            result["tags"] = json.loads(result["tags"])
        except:
            result["tags"] = []
    else:
        result["tags"] = []
    return result
