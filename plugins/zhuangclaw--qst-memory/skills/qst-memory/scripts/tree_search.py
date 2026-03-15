#!/usr/bin/env python3
"""
Tree Search v1.4 - 樹狀搜索
精確定位記憶，從根到葉逐步匹配

Usage:
    python tree_search.py "暗物質計算"
    python tree_search.py --path "QST.Physics.FSCA"
"""

import json
import re
import yaml
from pathlib import Path
from typing import Optional

# 配置路徑
SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
MEMORY_FILE = SKILL_DIR / "data" / "qst_memories.md"  # 獨立存儲


def load_config() -> dict:
    """載入配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {"tree": {}}


def load_memory() -> list:
    """載入記憶"""
    memories = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 解析記憶條目
            entries = re.split(r'\n---+\n', content)
            for entry in entries:
                if entry.strip():
                    memories.append(entry.strip())
    return memories


def classify_query(query: str, config: dict) -> list:
    """
    分類查詢，返回路徑

    例如: "暗物質計算" → ["QST", "Physics", "FSCA"]
    """
    path = []
    tree = config.get("tree", {})

    # 第一層：掃描所有根節點
    for root_name, root_data in tree.items():
        root_matched = match_keywords(query, root_data)

        # 檢查子節點（即使根節點不匹配也要檢查）
        children = root_data.get("children", {})
        for child_name, child_data in children.items():
            if match_keywords(query, child_data):
                # 找到匹配的子節點，添加路徑
                path.append(root_name)
                path.append(child_name)

                # 第三層：掃描孫節點
                grand_children = child_data.get("children", {})
                for grand_name, grand_data in grand_children.items():
                    if match_keywords(query, grand_data):
                        path.append(grand_name)
                        break
                return path

        # 如果子節點都不匹配，但根節點匹配
        if root_matched and not path:
            path.append(root_name)
            return path

    return path


def match_keywords(query: str, node_data: dict) -> bool:
    """檢查查詢是否匹配節點關鍵詞"""
    keywords = node_data.get("keywords", [])
    description = node_data.get("description", "").lower()

    query_lower = query.lower()

    # 檢查關鍵詞
    for kw in keywords:
        if kw.lower() in query_lower:
            return True

    # 檢查描述
    if description and description in query_lower:
        return True

    # 檢查節點名稱
    return False


def traverse_tree(memories: list, path: list, config: dict) -> list:
    """
    根據路徑遍歷記憶樹

    返回匹配的記憶列表
    """
    if not path:
        return memories[:10]  # 返回前10條

    results = []
    path_str = ".".join(path)

    # 獲取路徑對應的關鍵詞
    keywords = get_keywords_for_path(path, config)

    for memory in memories:
        # 檢查記憶是否包含標籤
        if f"[{path_str}]" in memory or f"[{path[-1]}]" in memory:
            results.append(memory)
        # 檢查記憶是否包含關鍵詞
        elif any(kw.lower() in memory.lower() for kw in keywords):
            results.append(memory)

    return results[:10]


def get_keywords_for_path(path: list, config: dict) -> list:
    """獲取路徑對應的所有關鍵詞"""
    keywords = []
    tree = config.get("tree", {})

    current = tree
    for node in path:
        if node in current:
            node_data = current[node]
            keywords.extend(node_data.get("keywords", []))
            current = node_data.get("children", {})
        elif "children" in current and node in current["children"]:
            node_data = current["children"][node]
            keywords.extend(node_data.get("keywords", []))
            current = node_data.get("children", {})

    return list(set(keywords))


def tree_search(query: str, method: str = "auto") -> dict:
    """
    樹狀搜索主函數

    Args:
        query: 搜索查詢
        method: 搜索方法 (auto, tree, path)

    Returns:
        {
            "path": ["QST", "Physics", "FSCA"],
            "keywords": ["暗物質", "FSCA", ...],
            "results": [...],
            "count": 5
        }
    """
    config = load_config()
    memories = load_memory()

    # 分類查詢
    path = classify_query(query, config)
    keywords = get_keywords_for_path(path, config)

    # 遍歷記憶
    results = traverse_tree(memories, path, config)

    return {
        "path": path,
        "keywords": keywords,
        "results": results,
        "count": len(results)
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tree Search for QST Memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--path", help="Direct path (e.g., QST.Physics.FSCA)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.path:
        # 直接路徑搜索
        path = args.path.split(".")
        config = load_config()
        memories = load_memory()
        results = traverse_tree(memories, path, config)
        keywords = get_keywords_for_path(path, config)
    else:
        # 自動分類搜索
        result = tree_search(args.query)
        path = result["path"]
        keywords = result["keywords"]
        results = result["results"]

    # 顯示完整樹狀路徑 (v1.5+ 改進)
    print(f"\n📁 完整路徑: {' → '.join(path) if path else 'Root'}")
    print(f"   層次: L{len(path) if path else 0} 分層")
    
    # 顯示從 L1 到 L3 的完整結構
    if path:
        print(f"\n   📂 L1 (根): {path[0]}")
        if len(path) > 1:
            print(f"   ├ 📂 L2 (次): {path[1]}")
        if len(path) > 2:
            print(f"   └ 📂 L3 (葉): {path[2]}")
    
    print(f"\n🔑 關鍵詞: {', '.join(keywords[:8]) if keywords else 'None'}")
    print(f"📊 找到 {len(results)} 條記憶\n")

    if args.verbose:
        for i, r in enumerate(results[:5], 1):
            print(f"--- Memory {i} ---")
            print(r[:200] + "..." if len(r) > 200 else r)
            print()
