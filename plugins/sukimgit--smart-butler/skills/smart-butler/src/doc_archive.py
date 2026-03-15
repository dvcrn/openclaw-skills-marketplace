"""
文档归档器
将 temp 中的草稿移动到正式目录
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def get_project_dir(project_name: str, base_dir: str = "D:\\OpenClawDocs\\projects") -> str:
    """
    获取或创建项目目录
    
    :param project_name: 项目名称
    :param base_dir: 项目基础目录
    :return: 项目目录路径
    """
    project_path = Path(base_dir) / project_name
    
    # 如果目录不存在，创建它
    project_path.mkdir(parents=True, exist_ok=True)
    
    return str(project_path)


def get_meeting_dir(meeting_name: str, date: str = None, base_dir: str = "D:\\OpenClawDocs\\meetings") -> str:
    """
    获取或创建会议目录
    
    :param meeting_name: 会议名称
    :param date: 日期（YYYYMMDD 格式，默认今天）
    :param base_dir: 会议基础目录
    :return: 会议目录路径
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    meeting_path = Path(base_dir) / f"{date}_{meeting_name}"
    meeting_path.mkdir(parents=True, exist_ok=True)
    
    return str(meeting_path)


def archive_document(
    source_path: str,
    project_name: str,
    filename: str = None,
    mark_as_final: bool = False,
    copy: bool = False
) -> dict:
    """
    归档文档到正式目录
    
    :param source_path: 源文件路径
    :param project_name: 项目名称
    :param filename: 新文件名（默认保持原名）
    :param mark_as_final: 是否标记为最终版
    :param copy: True=复制，False=移动
    :return: 归档结果
    """
    source = Path(source_path)
    
    if not source.exists():
        return {"success": False, "error": "源文件不存在"}
    
    # 获取项目目录
    project_dir = get_project_dir(project_name)
    
    # 生成新文件名
    if filename is None:
        filename = source.name
    
    # 如果标记为最终版，添加"_最终版"后缀
    if mark_as_final:
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        if "_最终版" not in stem:
            filename = f"{stem}_最终版{suffix}"
    
    # 目标路径
    target = Path(project_dir) / filename
    
    # 如果文件已存在，添加时间戳
    if target.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stem}_{timestamp}{suffix}"
        target = Path(project_dir) / filename
    
    # 执行移动/复制
    try:
        if copy:
            shutil.copy2(source, target)
            action = "复制"
        else:
            shutil.move(source, target)
            action = "移动"
        
        return {
            "success": True,
            "action": action,
            "source": str(source),
            "target": str(target),
            "project": project_name,
            "filename": filename
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def archive_to_meeting(
    source_path: str,
    meeting_name: str,
    date: str = None,
    filename: str = None
) -> dict:
    """
    归档文档到会议目录
    
    :param source_path: 源文件路径
    :param meeting_name: 会议名称
    :param date: 日期（YYYYMMDD）
    :param filename: 新文件名
    :return: 归档结果
    """
    source = Path(source_path)
    
    if not source.exists():
        return {"success": False, "error": "源文件不存在"}
    
    # 获取会议目录
    meeting_dir = get_meeting_dir(meeting_name, date)
    
    # 生成新文件名
    if filename is None:
        filename = source.name
    
    target = Path(meeting_dir) / filename
    
    # 如果文件已存在，添加时间戳
    if target.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stem}_{timestamp}{suffix}"
        target = Path(meeting_dir) / filename
    
    # 执行移动
    try:
        shutil.move(source, target)
        return {
            "success": True,
            "action": "移动",
            "source": str(source),
            "target": str(target),
            "meeting": meeting_name,
            "filename": filename
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def clean_temp(days_old: int = 7, dry_run: bool = True) -> dict:
    """
    清理 temp 目录中的旧文件
    
    :param days_old: 清理多少天前的文件
    :param dry_run: True=只查看不删除，False=实际删除
    :return: 清理结果
    """
    temp_dir = Path("D:\\OpenClawDocs\\temp")
    
    if not temp_dir.exists():
        return {"success": True, "message": "temp 目录不存在"}
    
    deleted_files = []
    skipped_files = []
    
    for file in temp_dir.glob("*"):
        if file.is_file():
            # 检查文件修改时间
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            days_since = (datetime.now() - mtime).days
            
            if days_since >= days_old:
                if dry_run:
                    deleted_files.append({
                        "path": str(file),
                        "days_old": days_since,
                        "size": file.stat().st_size
                    })
                else:
                    try:
                        file.unlink()
                        deleted_files.append({
                            "path": str(file),
                            "days_old": days_since,
                            "action": "deleted"
                        })
                    except Exception as e:
                        skipped_files.append({
                            "path": str(file),
                            "error": str(e)
                        })
    
    return {
        "success": True,
        "dry_run": dry_run,
        "days_old_threshold": days_old,
        "deleted_count": len(deleted_files),
        "skipped_count": len(skipped_files),
        "deleted_files": deleted_files,
        "skipped_files": skipped_files
    }


def list_projects(base_dir: str = "D:\\OpenClawDocs\\projects") -> list:
    """
    列出所有项目
    
    :param base_dir: 项目基础目录
    :return: 项目列表
    """
    projects = []
    base_path = Path(base_dir)
    
    if base_path.exists():
        for item in base_path.iterdir():
            if item.is_dir():
                # 统计项目中的文件数
                files = list(item.glob("*"))
                projects.append({
                    "name": item.name,
                    "path": str(item),
                    "file_count": len(files),
                    "last_modified": max(
                        [f.stat().st_mtime for f in files],
                        default=0
                    )
                })
    
    # 按最后修改时间排序
    projects.sort(key=lambda x: x["last_modified"], reverse=True)
    
    return projects


# 测试
if __name__ == "__main__":
    # 测试项目列表
    print("=== 项目列表 ===")
    projects = list_projects()
    for p in projects:
        print(f"  {p['name']} - {p['file_count']} 个文件")
    
    # 测试 temp 清理预览
    print("\n=== Temp 清理预览（7 天以上）===")
    result = clean_temp(days_old=7, dry_run=True)
    if result["deleted_files"]:
        for f in result["deleted_files"]:
            print(f"  {f['path']} ({f['days_old']} 天前)")
    else:
        print("  没有需要清理的文件")
