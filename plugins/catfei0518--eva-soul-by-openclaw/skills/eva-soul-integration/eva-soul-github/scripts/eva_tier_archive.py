#!/usr/bin/env python3
"""
夏娃分层归档系统 (Tier-Based Archive System)
==========================================

设计原理:
- 短期记忆: 7天未访问 或 重要性<3 → 升级到中期
- 中期记忆: 30天未访问 → 升级到长期
- 长期记忆: 90天未访问 → 彻底归档(压缩存储)

特点:
- 智能触发: 每次访问记忆时自动检查是否需要升级
- 无需Cron: 纯事件驱动
- 自动流转: 重要记忆被人经常访问，自然保留
- 压缩归档: 彻底归档时进行简单压缩(去重)
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# 配置路径
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
ARCHIVE_DIR = os.path.expanduser("~/.openclaw/workspace/memory/archive")

# 时间配置(天)
TIER_CONFIG = {
    "short": {
        "upgrade_days": 7,
        "importance_threshold": 3,
        "next_tier": "medium"
    },
    "medium": {
        "upgrade_days": 30,
        "importance_threshold": None,  # 中期不考虑重要性
        "next_tier": "long"
    },
    "long": {
        "upgrade_days": 90,
        "importance_threshold": None,
        "next_tier": "archive"  # 彻底归档
    }
}

# 初始化目录
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def load_tier_memories(tier: str) -> List[Dict]:
    """加载指定层级的记忆"""
    tier_file = os.path.join(MEMORY_DIR, tier, f"{tier}.json")
    if not os.path.exists(tier_file):
        return []
    try:
        with open(tier_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def save_tier_memories(tier: str, memories: List[Dict]):
    """保存指定层级的记忆"""
    tier_dir = os.path.join(MEMORY_DIR, tier)
    os.makedirs(tier_dir, exist_ok=True)
    tier_file = os.path.join(tier_dir, f"{tier}.json")
    with open(tier_file, 'w', encoding='utf-8') as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)


def get_days_since_access(accessed_at: str) -> int:
    """计算距离上次访问的天数"""
    if not accessed_at:
        return 0
    try:
        dt = datetime.fromisoformat(accessed_at.replace('Z', '+00:00'))
        # 使用本地时区
        dt = dt.replace(tzinfo=None)
        return (datetime.now() - dt).days
    except:
        return 0


def should_upgrade(memory: Dict, current_tier: str) -> tuple[bool, str]:
    """
    检查记忆是否应该升级到下一个层级
    
    返回: (是否应该升级, 目标层级)
    """
    config = TIER_CONFIG.get(current_tier)
    if not config:
        return False, ""
    
    days = get_days_since_access(memory.get("accessed_at", ""))
    importance = memory.get("importance", 5)
    
    # 检查条件1: 时间到期
    if days > config["upgrade_days"]:
        return True, config["next_tier"]
    
    # 检查条件2: 重要性低于阈值(仅短期)
    if config["importance_threshold"] and importance < config["importance_threshold"]:
        return True, config["next_tier"]
    
    return False, ""


def upgrade_memory(memory: Dict, from_tier: str, to_tier: str) -> Dict:
    """
    升级记忆到下一个层级
    """
    memory["tier"] = to_tier
    memory["upgraded_from"] = from_tier
    memory["upgraded_at"] = datetime.now().isoformat()
    return memory


def archive_memory(memory: Dict) -> Dict:
    """
    彻底归档记忆(压缩存储)
    - 去重(基于内容hash)
    - 合并计数
    """
    # 生成内容hash
    content = memory.get("content", "")
    content_hash = hashlib.md5(content[:100].encode()).hexdigest()
    
    archive_file = os.path.join(ARCHIVE_DIR, "archive_index.json")
    
    # 读取现有归档
    archives = []
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
    
    # 检查是否已存在相似内容
    for arc in archives:
        if arc.get("content_hash") == content_hash:
            arc["original_count"] = arc.get("original_count", 1) + 1
            arc["last_archived_at"] = datetime.now().isoformat()
            memory["archived_as"] = arc["id"]
            break
    else:
        # 新归档
        archive_id = f"arc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        archives.append({
            "id": archive_id,
            "content": content[:200],  # 只存前200字符
            "content_hash": content_hash,
            "original_count": 1,
            "source_tier": memory.get("tier", "long"),
            "created_range": datetime.now().strftime("%Y-%m"),
            "importance": memory.get("importance", 0),
            "archived_at": datetime.now().isoformat(),
            "last_archived_at": datetime.now().isoformat()
        })
        memory["archived_as"] = archive_id
    
    # 保存归档索引
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archives, f, ensure_ascii=False, indent=2)
    
    return memory


def check_and_upgrade_all():
    """
    检查并升级所有层级的记忆
    (可在每次启动或定时调用)
    """
    stats = {
        "short_to_medium": 0,
        "medium_to_long": 0,
        "long_to_archive": 0,
        "total_checked": 0
    }
    
    # 按层级顺序处理
    tiers = ["short", "medium", "long"]
    
    for tier in tiers:
        memories = load_tier_memories(tier)
        if not memories:
            continue
        
        to_upgrade = []
        to_keep = []
        
        for memory in memories:
            stats["total_checked"] += 1
            should_upg, new_tier = should_upgrade(memory, tier)
            
            if should_upg:
                if new_tier == "archive":
                    # 彻底归档
                    archive_memory(memory)
                    stats[f"{tier}_to_archive"] = stats.get(f"{tier}_to_archive", 0) + 1
                else:
                    # 升级到下一层级
                    memory = upgrade_memory(memory, tier, new_tier)
                    to_upgrade.append(memory)
                    stats[f"{tier}_to_{new_tier}"] = stats.get(f"{tier}_to_{new_tier}", 0) + 1
            else:
                to_keep.append(memory)
        
        # 保存剩余记忆
        save_tier_memories(tier, to_keep)
        
        # 添加升级的记忆到目标层级
        if to_upgrade:
            target_tier = to_upgrade[0].get("tier", tiers[tiers.index(tier) + 1])
            target_memories = load_tier_memories(target_tier)
            target_memories.extend(to_upgrade)
            save_tier_memories(target_tier, target_memories)
    
    return stats


def on_memory_access(memory_id: str = None, content: str = None):
    """
    当记忆被访问时调用
    - 更新访问时间
    - 检查是否需要升级
    
    参数:
        memory_id: 记忆ID(可选)
        content: 记忆内容(可选,用于定位)
    """
    # 这个函数应该在记忆检索后调用
    # 更新accessed_at为当前时间
    pass


def restore_from_archive(archive_id: str = None, content: str = None) -> Optional[Dict]:
    """
    从归档中恢复记忆
    
    参数:
        archive_id: 归档ID
        content: 内容(用于搜索)
    
    返回: 恢复的记忆或None
    """
    archive_file = os.path.join(ARCHIVE_DIR, "archive_index.json")
    if not os.path.exists(archive_file):
        return None
    
    with open(archive_file, 'r', encoding='utf-8') as f:
        archives = json.load(f)
    
    # 查找
    target = None
    if archive_id:
        for arc in archives:
            if arc.get("id") == archive_id:
                target = arc
                break
    elif content:
        # 模糊搜索
        for arc in archives:
            if content in arc.get("content", ""):
                target = arc
                break
    
    if target:
        return {
            "content": target.get("content", ""),
            "original_count": target.get("original_count", 1),
            "archived_at": target.get("archived_at", ""),
            "source_tier": target.get("source_tier", "")
        }
    
    return None


def get_tier_stats() -> Dict:
    """获取各层级统计"""
    stats = {}
    for tier in ["short", "medium", "long"]:
        memories = load_tier_memories(tier)
        stats[tier] = {
            "count": len(memories),
            "avg_importance": sum(m.get("importance", 0) for m in memories) / max(len(memories), 1)
        }
    
    # 归档统计
    archive_file = os.path.join(ARCHIVE_DIR, "archive_index.json")
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
        stats["archive"] = {
            "count": len(archives),
            "total_original": sum(a.get("original_count", 1) for a in archives)
        }
    else:
        stats["archive"] = {"count": 0, "total_original": 0}
    
    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="夏娃分层归档系统")
    parser.add_argument("--action", choices=["check", "stats", "restore"], default="check")
    parser.add_argument("--archive-id", help="归档ID")
    parser.add_argument("--content", help="搜索内容")
    args = parser.parse_args()
    
    if args.action == "check":
        print("🔄 检查并升级记忆层级...")
        stats = check_and_upgrade_all()
        print(f"✅ 完成! 统计: {stats}")
    elif args.action == "stats":
        stats = get_tier_stats()
        print("📊 各层级统计:")
        for tier, data in stats.items():
            print(f"  {tier}: {data}")
    elif args.action == "restore":
        result = restore_from_archive(args.archive_id, args.content)
        if result:
            print(f"✅ 恢复: {result}")
        else:
            print("❌ 未找到")


def adjust_importance_on_access(memory):
    """
    根据访问次数调整重要性
    - 访问次数 > 5: 重要性 +3
    - 访问次数 > 10: 重要性 +5
    最高100
    """
    access_count = memory.get("access_count", 0)
    current_importance = memory.get("importance", 5)
    
    if access_count > 10:
        new_importance = min(100, current_importance + 5)
    elif access_count > 5:
        new_importance = min(100, current_importance + 3)
    else:
        new_importance = current_importance
    
    if new_importance != current_importance:
        memory["importance"] = new_importance
        memory["importance_adjusted_at"] = datetime.now().isoformat()
        return True
    return False


def increment_access_count(memory):
    """增加访问计数"""
    memory["access_count"] = memory.get("access_count", 0) + 1
    memory["accessed_at"] = datetime.now().isoformat()
    return memory


def check_and_upgrade_with_adjustment():
    """
    检查并升级记忆，同时调整重要性
    """
    stats = {
        "short_to_medium": 0,
        "medium_to_long": 0,
        "long_to_archive": 0,
        "importance_adjusted": 0,
        "total_checked": 0
    }
    
    tiers = ["short", "medium", "long"]
    
    for tier in tiers:
        memories = load_tier_memories(tier)
        if not memories:
            continue
        
        to_upgrade = []
        to_keep = []
        
        for memory in memories:
            stats["total_checked"] += 1
            
            # 先增加访问计数
            increment_access_count(memory)
            
            # 调整重要性
            if adjust_importance_on_access(memory):
                stats["importance_adjusted"] += 1
            
            # 检查是否需要升级
            should_upg, new_tier = should_upgrade(memory, tier)
            
            if should_upg:
                if new_tier == "archive":
                    archive_memory(memory)
                    stats[f"{tier}_to_archive"] = stats.get(f"{tier}_to_archive", 0) + 1
                else:
                    memory = upgrade_memory(memory, tier, new_tier)
                    to_upgrade.append(memory)
                    stats[f"{tier}_to_{new_tier}"] = stats.get(f"{tier}_to_{new_tier}", 0) + 1
            else:
                to_keep.append(memory)
        
        save_tier_memories(tier, to_keep)
        
        if to_upgrade:
            target_tier = to_upgrade[0].get("tier", tiers[tiers.index(tier) + 1])
            target_memories = load_tier_memories(target_tier)
            target_memories.extend(to_upgrade)
            save_tier_memories(target_tier, target_memories)
    
    return stats
