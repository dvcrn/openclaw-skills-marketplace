#!/usr/bin/env python3
"""
夏娃概念抽象系统
从具体记忆提炼普遍概念

功能:
- 实时抽象: 新记忆入库时检查
- 每日增量: 每天更新概念
- 每周深度: 全面刷新
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
CONCEPTS_FILE = os.path.join(MEMORY_DIR, "concepts.json")

# 概念分类
CONCEPT_CATEGORIES = {
    "person": "人物",
    "place": "地点", 
    "thing": "事物",
    "preference": "偏好",
    "habit": "习惯",
    "skill": "技能",
    "emotion": "情感模式",
    "relationship": "关系",
    "work": "工作",
    "life": "生活"
}

def load_concepts():
    """加载概念库"""
    if os.path.exists(CONCEPTS_FILE):
        with open(CONCEPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "updated_at": None,
        "concepts": [],  # 概念列表
        "stats": {
            "total_abstracted": 0,
            "last_daily": None,
            "last_weekly": None
        }
    }

def save_concepts(data):
    """保存概念库"""
    data["updated_at"] = datetime.now().isoformat()
    with open(CONCEPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_memories():
    """加载所有记忆"""
    memories = []
    
    # 短期记忆
    short_file = os.path.join(MEMORY_DIR, "short/short.json")
    if os.path.exists(short_file):
        with open(short_file, 'r', encoding='utf-8') as f:
            memories.extend(json.load(f))
    
    # 中期记忆
    medium_file = os.path.join(MEMORY_DIR, "medium/medium.json")
    if os.path.exists(medium_file):
        with open(medium_file, 'r', encoding='utf-8') as f:
            memories.extend(json.load(f))
    
    # 长期记忆
    long_file = os.path.join(MEMORY_DIR, "long/long.json")
    if os.path.exists(long_file):
        with open(long_file, 'r', encoding='utf-8') as f:
            memories.extend(json.load(f))
    
    return memories

def extract_keywords(content):
    """提取关键词"""
    keywords = set()
    
    # 简单关键词提取
    important_words = ["喜欢", "讨厌", "经常", "总是", "每天", "工作", "生活", "学习",
                      "朋友", "家人", "公司", "项目", "爱好", "习惯", "要", "想做"]
    
    for word in important_words:
        if word in content:
            keywords.add(word)
    
    return keywords

def calculate_similarity(mem1, mem2):
    """计算两条记忆的相似度"""
    # 基于标签相似度
    tags1 = mem1.get("tags", {})
    tags2 = mem2.get("tags", {})
    
    all_keys = set(tags1.keys()) | set(tags2.keys())
    if not all_keys:
        return 0
    
    score = 0
    for key in all_keys:
        set1 = set(tags1.get(key, []))
        set2 = set(tags2.get(key, []))
        if set1 & set2:
            score += 1
    
    return score / len(all_keys)

def group_similar_memories(memories, threshold=0.5):
    """将相似记忆分组"""
    groups = []
    used = set()
    
    for i, mem in enumerate(memories):
        if mem.get("id") in used:
            continue
        
        group = [mem]
        used.add(mem.get("id"))
        
        for j, other in enumerate(memories):
            if i == j or other.get("id") in used:
                continue
            
            sim = calculate_similarity(mem, other)
            if sim >= threshold:
                group.append(other)
                used.add(other.get("id"))
        
        if len(group) >= 2:
            groups.append(group)
    
    return groups

def abstract_concept(memories_group):
    """从记忆组抽象出概念"""
    if len(memories_group) < 2:
        return None
    
    # 提取共同特征
    all_tags = defaultdict(list)
    keywords_count = defaultdict(int)
    
    for mem in memories_group:
        tags = mem.get("tags", {})
        for tag_type, tag_list in tags.items():
            for tag in tag_list:
                all_tags[tag_type].append(tag)
        
        # 关键词统计
        keywords = extract_keywords(mem.get("content", ""))
        for kw in keywords:
            keywords_count[kw] += 1
    
    # 统计最常见的标签
    common_tags = {}
    for tag_type, tags in all_tags.items():
        if tags:
            from collections import Counter
            counter = Counter(tags)
            common_tags[tag_type] = counter.most_common(3)
    
    # 提取最常见关键词
    top_keywords = sorted(keywords_count.items(), key=lambda x: -x[1])[:5]
    
    # 生成概念描述
    concept_evidence = [m.get("content", "")[:50] for m in memories_group[:3]]
    
    concept = {
        "id": f"概念_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
        "category": detect_category(all_tags),
        "evidence_count": len(memories_group),
        "evidence": concept_evidence,
        "common_tags": common_tags,
        "keywords": [k for k, _ in top_keywords],
        "summary": generate_summary(common_tags, top_keywords),
        "confidence": min(len(memories_group) * 0.1, 0.9),  # 置信度
        "created_at": datetime.now().isoformat(),
        "last_verified": datetime.now().isoformat()
    }
    
    return concept

def detect_category(tags):
    """检测概念类别"""
    topics = tags.get("topic", [])
    entities = tags.get("entity", [])
    
    topic_str = "".join(topics)
    entity_str = "".join(entities)
    
    if "工作" in topic_str or "项目" in entity_str:
        return "work"
    elif "生活" in topic_str or "习惯" in topic_str:
        return "life"
    elif "学习" in topic_str or "技能" in topic_str:
        return "skill"
    elif "喜欢" in topic_str or "爱好" in topic_str:
        return "preference"
    elif "情感" in topic_str or "难过" in topic_str or "开心" in topic_str:
        return "emotion"
    elif "关系" in topic_str or "朋友" in entity_str:
        return "relationship"
    else:
        return "thing"

def generate_summary(common_tags, keywords):
    """生成概念摘要"""
    parts = []
    
    # 从标签生成
    if common_tags.get("topic"):
        topics = [t[0] for t in common_tags["topic"][:2]]
        parts.append(f"关于{'、'.join(topics)}")
    
    if common_tags.get("emotion"):
        emotions = [e[0] for e in common_tags["emotion"][:2]]
        parts.append(f"情感倾向:{'、'.join(emotions)}")
    
    # 从关键词生成
    if keywords:
        kws = [k for k, _ in keywords[:3]]
        parts.append(f"关键词:{'、'.join(kws)}")
    
    return "，".join(parts) if parts else "综合概念"

def realtime_abstract(new_memory):
    """实时抽象 - 新记忆入库时调用"""
    concepts = load_concepts()
    
    # 加载最近记忆
    memories = load_memories()
    
    # 找相似记忆
    similar = []
    for mem in memories[-50:]:  # 只检查最近50条
        if mem.get("id") == new_memory.get("id"):
            continue
        sim = calculate_similarity(new_memory, mem)
        if sim >= 0.3:
            similar.append(mem)
    
    # 如果有5条以上相似，尝试抽象
    if len(similar) >= 5:
        group = [new_memory] + similar
        new_concept = abstract_concept(group)
        
        if new_concept:
            # 检查是否已存在相似概念
            exists = False
            for c in concepts["concepts"]:
                if c.get("summary") == new_concept.get("summary"):
                    exists = True
                    break
            
            if not exists:
                concepts["concepts"].append(new_concept)
                concepts["stats"]["total_abstracted"] += 1
                save_concepts(concepts)
                return new_concept
    
    return None

def daily_incremental_update():
    """每日增量更新"""
    concepts = load_concepts()
    memories = load_memories()
    
    # 检查现有概念是否需要更新
    updated = 0
    for concept in concepts["concepts"]:
        # 找与概念相关的记忆
        related = []
        for mem in memories:
            if concept.get("summary") in mem.get("content", ""):
                related.append(mem)
        
        # 如果有新证据，更新置信度
        if len(related) > concept.get("evidence_count", 0):
            concept["evidence_count"] = len(related)
            concept["confidence"] = min(len(related) * 0.1, 0.95)
            concept["last_verified"] = datetime.now().isoformat()
            updated += 1
    
    concepts["stats"]["last_daily"] = datetime.now().isoformat()
    save_concepts(concepts)
    
    return {"updated": updated, "total": len(concepts["concepts"])}

def weekly_deep_refresh():
    """每周深度刷新"""
    print("🔄 开始每周概念深度刷新...")
    
    concepts = load_concepts()
    memories = load_memories()
    
    # 重新分组所有记忆
    groups = group_similar_memories(memories, threshold=0.4)
    
    # 重新抽象所有概念
    new_concepts = []
    for group in groups:
        concept = abstract_concept(group)
        if concept:
            new_concepts.append(concept)
    
    # 合并新旧概念
    merged = merge_concepts(concepts.get("concepts", []), new_concepts)
    
    concepts["concepts"] = merged
    concepts["stats"]["total_abstracted"] = len(merged)
    concepts["stats"]["last_weekly"] = datetime.now().isoformat()
    save_concepts(concepts)
    
    return {
        "total_concepts": len(merged),
        "new_abstracted": len(new_concepts)
    }

def merge_concepts(old, new):
    """合并新旧概念"""
    merged = old.copy()
    
    for nc in new:
        exists = False
        for oc in merged:
            if nc.get("summary") == oc.get("summary"):
                # 更新旧概念
                if nc.get("evidence_count", 0) > oc.get("evidence_count", 0):
                    oc.update(nc)
                exists = True
                break
        
        if not exists:
            merged.append(nc)
    
    return merged

def get_concept_stats():
    """获取概念统计"""
    concepts = load_concepts()
    
    # 按类别统计
    categories = defaultdict(int)
    for c in concepts["concepts"]:
        categories[c.get("category", "unknown")] += 1
    
    return {
        "total": len(concepts["concepts"]),
        "categories": dict(categories),
        "stats": concepts["stats"],
        "recent": concepts["concepts"][-5:] if concepts["concepts"] else []
    }

# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 eva_concept.py realtime <json>  - 实时抽象")
        print("  python3 eva_concept.py daily           - 每日增量")
        print("  python3 eva_concept.py weekly          - 每周深度")
        print("  python3 eva_concept.py stats           - 查看统计")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "realtime":
        if len(sys.argv) > 2:
            new_mem = json.loads(sys.argv[2])
            result = realtime_abstract(new_mem)
            if result:
                print(f"✅ 创建新概念: {result['summary']}")
            else:
                print("⏳ 暂未形成概念")
        else:
            print("❌ 需要提供记忆JSON")
    
    elif action == "daily":
        result = daily_incremental_update()
        print(f"✅ 每日更新完成: 更新{result['updated']}个概念，共{result['total']}个")
    
    elif action == "weekly":
        result = weekly_deep_refresh()
        print(f"✅ 每周刷新完成: 共{result['total_concepts']}个概念")
    
    elif action == "stats":
        stats = get_concept_stats()
        print("=== 概念统计 ===")
        print(f"总数: {stats['total']}")
        print(f"类别: {stats['categories']}")
        print(f"统计: {stats['stats']}")
    
    else:
        print(f"❌ 未知动作: {action}")
