#!/usr/bin/env python3
"""
Cleanup v1.5 - 記憶衰減與清理系統

功能：
1. 記憶衰減計算
2. 自動歸檔過期記憶
3. 統計報告生成

Usage:
    python cleanup.py --dry-run
    python cleanup.py --run
    python cleanup.py --status
"""

import re
import yaml
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲
ARCHIVE_DIR = SKILL_DIR.parent / "memory_archive"


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_memories() -> List[Dict]:
    """載入所有記憶"""
    memories = []
    
    if not MEMORY_FILE.exists():
        return memories
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        entries = re.split(r'\n---+\n', content)
        
        for i, entry in enumerate(entries):
            if not entry.strip():
                continue
            
            # 解析元數據
            weight = "N"
            date_str = None
            
            weight_match = re.search(r'\[([CIN])\]', entry)
            if weight_match:
                weight = weight_match.group(1)
            
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', entry)
            if date_match:
                date_str = date_match.group(1)
            
            # 解析分類
            category = "General"
            cat_match = re.search(r'\[([A-Za-z_]+)\]', entry)
            if cat_match and cat_match.group(1) not in ['C', 'I', 'N']:
                category = cat_match.group(1)
            
            memories.append({
                "index": i,
                "content": entry.strip(),
                "weight": weight,
                "date": date_str,
                "category": category,
                "size": len(entry)
            })
    
    return memories


def get_age_days(date_str: Optional[str]) -> int:
    """計算記憶年齡（天）"""
    if not date_str:
        return 0
    
    try:
        mem_date = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - mem_date).days
    except:
        return 0


def should_cleanup(memory: Dict, config: dict) -> Tuple[bool, str]:
    """
    判斷記憶是否應該清理
    
    Returns:
        (should_cleanup, reason)
    """
    cleanup_config = config.get("cleanup", {})
    max_age = cleanup_config.get("max_age_days", {})
    
    weight = memory["weight"]
    age_days = get_age_days(memory["date"])
    
    if weight == "C":
        # Critical: 永不刪除
        return False, "Critical memory - never cleanup"
    
    elif weight == "I":
        # Important: 365 天後歸檔
        threshold = max_age.get("important", 365)
        if age_days >= threshold:
            return True, f"Important memory expired ({age_days} >= {threshold} days)"
    
    else:
        # Normal: 30 天後刪除
        threshold = max_age.get("normal", 30)
        if age_days >= threshold:
            return True, f"Normal memory expired ({age_days} >= {threshold} days)"
    
    return False, "Memory still valid"


def get_decay_multiplier(weight: str, age_days: int, config: dict) -> float:
    """計算衰減係數"""
    decay = config.get("decay", {})
    
    if weight == "C":
        return 1.0  # 不衰減
    elif weight == "I":
        rate = decay.get("important", 0.1)
        return max(0.1, 1.0 - age_days * rate / 365)
    else:
        rate = decay.get("normal", 0.5)
        return max(0.1, 1.0 - age_days * rate / 30)


def cleanup_memories(dry_run: bool = True) -> Dict:
    """
    清理記憶
    
    Args:
        dry_run: True = 模擬運行，不實際刪除
    
    Returns:
        清理報告
    """
    config = load_config()
    memories = load_memories()
    
    to_delete = []
    to_archive = []
    to_keep = []
    
    for memory in memories:
        should, reason = should_cleanup(memory, config)
        
        if should:
            if memory["weight"] == "I":
                to_archive.append((memory, reason))
            else:
                to_delete.append((memory, reason))
        else:
            to_keep.append((memory, reason))
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "summary": {
            "total": len(memories),
            "kept": len(to_keep),
            "archived": len(to_archive),
            "deleted": len(to_delete)
        },
        "kept": [{"index": m[0]["index"], "reason": m[1]} for m in to_keep],
        "archived": [{"index": m[0]["index"], "reason": m[1], "date": m[0]["date"]} for m in to_archive],
        "deleted": [{"index": m[0]["index"], "reason": m[1], "date": m[0]["date"]} for m in to_delete]
    }
    
    if not dry_run:
        # 執行清理
        # 1. 歸檔 Important 記憶
        if to_archive:
            archive_memories(to_archive)
        
        # 2. 刪除 Normal 記憶
        if to_delete:
            delete_memories([m[0] for m in to_delete])
        
        # 3. 重建 MEMORY.md
        rebuild_memory_file(to_keep)
    
    return report


def archive_memories(memories: List[Tuple[Dict, str]]):
    """歸檔記憶到 ARCHIVE_DIR"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = ARCHIVE_DIR / f"archive_{timestamp}.md"
    
    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(f"# Archived Memories - {timestamp}\n\n")
        f.write("---\n\n".join(m[0]["content"] for m in memories))
        f.write("\n")
    
    print(f"✅ Archived {len(memories)} memories to {archive_file}")


def delete_memories(memories: List[Dict]):
    """刪除記憶"""
    print(f"🗑️ Deleted {len(memories)} memories")


def rebuild_memory_file(kept_memories: List[Tuple[Dict, str]]):
    """重建 MEMORY.md"""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        contents = [m[0]["content"] for m in kept_memories]
        f.write("\n---\n\n".join(contents))
        f.write("\n")
    
    print(f"✅ Rebuilt MEMORY.md with {len(kept_memories)} memories")


def show_status() -> Dict:
    """顯示記憶狀態"""
    config = load_config()
    memories = load_memories()
    
    stats = {
        "total": len(memories),
        "by_weight": {"C": 0, "I": 0, "N": 0},
        "by_age": {"recent": 0, "week": 0, "month": 0, "old": 0},
        "by_category": {},
        "decay_status": []
    }
    
    cleanup_config = config.get("cleanup", {})
    max_age = cleanup_config.get("max_age_days", {})
    
    for mem in memories:
        # 按權重分類
        stats["by_weight"][mem["weight"]] += 1
        
        # 按年齡分類
        age = get_age_days(mem["date"])
        if age < 7:
            stats["by_age"]["recent"] += 1
        elif age < 30:
            stats["by_age"]["week"] += 1
        elif age < 365:
            stats["by_age"]["month"] += 1
        else:
            stats["by_age"]["old"] += 1
        
        # 按分類分類
        cat = mem["category"]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        # 衰減狀態
        decay = get_decay_multiplier(mem["weight"], age, config)
        if mem["weight"] != "C" and decay < 0.5:
            stats["decay_status"].append({
                "category": cat,
                "weight": mem["weight"],
                "age_days": age,
                "decay": round(decay, 2)
            })
    
    return stats


def print_status():
    """打印狀態"""
    stats = show_status()
    
    print(f"\n📊 Memory Status")
    print(f"{'='*50}")
    print(f"總記憶數: {stats['total']}")
    
    print(f"\n📦 By Weight:")
    print(f"  [C] Critical: {stats['by_weight']['C']}")
    print(f"  [I] Important: {stats['by_weight']['I']}")
    print(f"  [N] Normal: {stats['by_weight']['N']}")
    
    print(f"\n📅 By Age:")
    print(f"  < 7 天: {stats['by_age']['recent']}")
    print(f"  7-30 天: {stats['by_age']['week']}")
    print(f"  30-365 天: {stats['by_age']['month']}")
    print(f"  > 365 天: {stats['by_age']['old']}")
    
    print(f"\n📁 By Category:")
    for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    if stats["decay_status"]:
        print(f"\n⚠️ High Decay Memories:")
        for m in stats["decay_status"][:5]:
            print(f"  {m['category']}: {m['decay']} (age: {m['age_days']}d, weight: {m['weight']})")


def print_report(report: Dict):
    """打印清理報告"""
    print(f"\n🧹 Cleanup Report - {report['timestamp']}")
    print(f"{'='*50}")
    print(f"Dry Run: {report['dry_run']}")
    
    print(f"\n📊 Summary:")
    print(f"  Total: {report['summary']['total']}")
    print(f"  Kept: {report['summary']['kept']}")
    print(f"  Archived: {report['summary']['archived']}")
    print(f"  Deleted: {report['summary']['deleted']}")
    
    if report['archived']:
        print(f"\n📦 Archived:")
        for m in report['archived'][:5]:
            print(f"  • [{m['date']}] {m['reason']}")
    
    if report['deleted']:
        print(f"\n🗑️ Deleted:")
        for m in report['deleted'][:5]:
            print(f"  • [{m['date']}] {m['reason']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Cleanup System v1.5")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
    parser.add_argument("--run", action="store_true", help="Run cleanup")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.status:
        print_status()
    elif args.run:
        report = cleanup_memories(dry_run=False)
        print_report(report)
    elif args.dry_run:
        report = cleanup_memories(dry_run=True)
        print_report(report)
        if args.verbose:
            print("\n📋 Detailed Status:")
            print_status()
    else:
        # 默認顯示狀態
        print_status()
